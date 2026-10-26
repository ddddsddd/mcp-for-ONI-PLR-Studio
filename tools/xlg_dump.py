"""Разбор проекта ONI PLR Studio (.xlg) и проверка связей.

Использование: python3 tools/xlg_dump.py файл.xlg [...]

Печатает блоки и линии связи и проверяет, что:
- поток объектов MFC разбирается до конца, без лишних байтов;
- каждая линия начинается у выхода блока-источника и кончается у входа приёмника;
- у блока-приёмника на этом входе записан тот же источник, что и у линии.
Выход 0, если ошибок нет.
"""
import struct
import sys

# Размер тела записи (после имени класса) для блоков фиксированной длины.
FIXED = {"CInputEntity": 0x438, "COutputEntity": 0x440, "CRSEntity": 0x41C,
         "CLogicANDEntity": 0x480, "CLogicOREntity": 0x480, "CLogicNOTEntity": 0x480}
NOTE_HEAD, NOTE_TAIL = 0x41, 0x13C
LINE_HEAD = 0x166            # до счётчика точек
POINT_PAD = 100               # байты-заполнители перед координатами точки
PREFIX = {"CInputEntity": "I", "COutputEntity": "Q", "CRSEntity": "B", "CLogicANDEntity": "B",
          "CLogicOREntity": "B", "CLogicNOTEntity": "B"}


class Reader:
    def __init__(self, data):
        self.d, self.p = data, 0
        self.classes = {}         # номер в архиве -> имя класса
        self.next_index = 1

    def u16(self):
        v = struct.unpack_from("<H", self.d, self.p)[0]
        self.p += 2
        return v

    def take(self, n):
        b = self.d[self.p:self.p + n]
        if len(b) != n:
            raise ValueError("файл обрывается на 0x%x" % self.p)
        self.p += n
        return b

    def cls(self):
        """Читает тег класса CArchive, возвращает имя класса."""
        tag = self.u16()
        if tag == 0xFFFF:
            self.u16()                          # schema
            name = self.take(self.u16()).decode("ascii")
            self.classes[self.next_index] = name
            self.next_index += 1
        elif tag & 0x8000:
            name = self.classes[tag & 0x7FFF]
        else:
            raise ValueError("ссылка на объект 0x%x на 0x%x не поддерживается"
                             % (tag, self.p - 2))
        self.next_index += 1                    # сам объект тоже получает номер
        return name


def read_points(r, n):
    pts = []
    for _ in range(n):
        if r.cls() != "CPointObj":
            raise ValueError("ожидалась точка линии на 0x%x" % r.p)
        r.take(POINT_PAD)
        pts.append(struct.unpack("<2I", r.take(8)))
    return pts


def parse(data):
    r = Reader(data)
    count = r.u16()
    objs = []
    for _ in range(count):
        start = r.p
        name = r.cls()
        if name in FIXED:
            body = r.take(FIXED[name])
            x1, x2, y1, y2 = struct.unpack_from("<4d", body, 0)
            bid = struct.unpack_from("<I", body, 0x142)[0]
            srcs = struct.unpack_from("<20I", body, 0x148)
            out_net = struct.unpack_from("<I", body, 0x2A0)[0]
            n_in = struct.unpack_from("<I", body, 0x261)[0]
            objs.append(dict(kind=name, id=bid, rect=(x1, x2, y1, y2), n_in=n_in,
                             srcs=srcs, out_net=out_net, at=start))
        elif name == "CNoteEntity":
            head = r.take(NOTE_HEAD)
            n = r.take(1)[0]
            text = r.take(n).decode("cp1251")
            r.take(NOTE_TAIL)
            objs.append(dict(kind=name, text=text, rect=struct.unpack_from("<4d", head, 0), at=start))
        elif name == "CLineEntity":
            head = r.take(LINE_HEAD)
            src, dst, _, pin, _ = struct.unpack_from("<5I", head, 0x14E)
            npts = r.u16()
            pts = read_points(r, npts)
            joints = read_points(r, r.u16())    # точки ветвления (жирные точки на схеме)
            r.take(2)
            objs.append(dict(kind=name, src=src, dst=dst, pin=pin, joints=joints,
                             ends=struct.unpack_from("<4I", head, 0x13E), pts=pts, at=start))
        else:
            raise ValueError("неизвестный класс %s на 0x%x" % (name, start))
    return objs, r.p


def label(block, _=None):
    p = PREFIX[block["kind"]]
    base = {"I": 100, "Q": 12000, "B": 100000}[p]
    return "%s%03d" % (p, block["id"] - base + 1)


def check(path):
    data = open(path, "rb").read()
    objs, end = parse(data)
    errors = []
    if data[end:end + 4] != struct.pack("<I", 10000):
        errors.append("после объектов нет блока свойств проекта (0x%x)" % end)
    blocks = {o["id"]: o for o in objs if o["kind"] in FIXED}
    print("==", path)
    for b in blocks.values():
        x1, x2, y1, y2 = b["rect"]
        srcs = [s for s in b["srcs"] if s]
        print("  %-6s %-14s id=%-6d rect=(%g..%g, %g..%g) входы от %s"
              % (label(b, None), b["kind"], b["id"], x1, x2, y1, y2, srcs or "-"))
    for o in objs:
        if o["kind"] == "CNoteEntity":
            print("  заметка:", o["text"].replace("\r\n", " | "))
    for o in objs:
        if o["kind"] != "CLineEntity":
            continue
        s, t = blocks.get(o["src"]), blocks.get(o["dst"])
        print("  линия  %s -> %s (вход %d), точки %s%s"
              % (label(s, None) if s else o["src"], label(t, None) if t else o["dst"],
                 o["pin"], o["pts"], ", ветвление %s" % o["joints"] if o["joints"] else ""))
        if not s or not t:
            errors.append("линия ссылается на несуществующий блок")
            continue
        sx1, sx2, sy1, _ = s["rect"]
        tx1, _, ty1, _ = t["rect"]
        if o["pts"][0] != (sx2 + 6, sy1 + 16):
            errors.append("начало линии не у выхода %s" % label(s, None))
        # один вход — посередине блока; два — сверху (+8) и снизу (+32); четыре — через 8
        pin_y = {1: [16], 2: [8, 32], 4: [8, 16, 24, 32]}.get(t["n_in"])
        if pin_y and o["pts"][-1] != (tx1 - 6, ty1 + pin_y[o["pin"]]):
            errors.append("конец линии не у входа %d блока %s" % (o["pin"], label(t, None)))
        # вход I передаёт свой ID; выход функц. блока — адрес флага M (B001[M1] = 50000)
        net = s["id"] if s["kind"] == "CInputEntity" else s["out_net"]
        # вход I хранит ID одного блока, куда идёт его сигнал (при нескольких — первого)
        dsts = [l["dst"] for l in objs if l["kind"] == "CLineEntity" and l["src"] == s["id"]]
        if s["kind"] == "CInputEntity" and s["out_net"] not in dsts:
            errors.append("у %s адресатом записан %d, а линии идут в %s"
                          % (label(s), s["out_net"], dsts))
        if t["srcs"][o["pin"]] != net:
            errors.append("у %s на входе %d записан источник %d, а линия идёт от %d"
                          % (label(t, None), o["pin"], t["srcs"][o["pin"]], net))
    for e in errors:
        print("  ОШИБКА:", e)
    print("  итог:", "ошибок нет" if not errors else "%d ошибок" % len(errors))
    return not errors


if __name__ == "__main__":
    ok = all([check(p) for p in sys.argv[1:]])
    sys.exit(0 if ok else 1)
