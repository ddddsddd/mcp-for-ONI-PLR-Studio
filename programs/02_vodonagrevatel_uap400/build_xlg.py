"""Собирает vodonagrevatel.xlg из блоков проекта 01_pusk_stop.

Формат .xlg — сериализация MFC (CArchive). Записи блоков берутся из
pusk_stop.xlg как шаблоны, меняются только связи, координаты и тексты.
Схема: I1 (термоконтакт SK) -> Q1 (контактор KM + лампа HG).
"""
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "01_pusk_stop" / "pusk_stop.xlg"
DST = HERE / "vodonagrevatel.xlg"

d = SRC.read_bytes()


def cstr(text):
    raw = text.encode("cp1251")
    assert len(raw) < 255
    return bytes([len(raw)]) + raw


def put_u32(buf, off, val):
    struct.pack_into("<I", buf, off, val)


def put_dbl(buf, off, *vals):
    for i, v in enumerate(vals):
        struct.pack_into("<d", buf, off + 8 * i, v)


# --- шаблоны записей из pusk_stop.xlg ---
assert struct.unpack_from("<H", d, 0)[0] == 8
inp = bytearray(d[0x02:0x44C])     # CInputEntity I1 (ID 100)
out = bytearray(d[0x886:0xCD9])    # COutputEntity Q1 (ID 12000)
note = bytearray(d[0x1104:0x12F1])  # CNoteEntity
line = bytearray(d[0x12F1:0x1633])  # CLineEntity + 4 x CPointObj
tail = bytearray(d[0x1C7F:])        # свойства проекта и модели

assert inp[6:18] == b"CInputEntity"
assert out[6:19] == b"COutputEntity"
assert note[6:17] == b"CNoteEntity"
assert line[6:17] == b"CLineEntity"

# --- I1: куда идёт сигнал — ID блока-приёмника (Q001), так сохраняет Studio ---
IN_BODY = 6 + 12
assert struct.unpack_from("<I", inp, IN_BODY + 0x2A0)[0] == 100000
put_u32(inp, IN_BODY + 0x2A0, 12000)

# --- Q1: источник сигнала — I1 (ID 100) вместо выхода RS-триггера ---
OUT_BODY = 6 + 13
assert struct.unpack_from("<I", out, OUT_BODY + 0x142)[0] == 12000
assert struct.unpack_from("<I", out, OUT_BODY + 0x148)[0] == 50000
put_u32(out, OUT_BODY + 0x148, 100)

# --- линия I1 -> Q1 ---
LB = 6 + 11
p_start, p_end = (150, 144), (658, 208)
put_dbl(line, LB, 150.0, 658.0, 144.0, 208.0)
ep = line.index(struct.pack("<4I", 150, 144, 394, 208))
struct.pack_into("<4I", line, ep, *p_start, *p_end)
assert struct.unpack_from("<2I", line, ep + 16) == (100, 100000)
struct.pack_into("<5I", line, ep + 16, 100, 12000, 20, 0, 1)
pts = [(150, 144), (404, 144), (404, 208), (658, 208)]
old_pts = [(150, 144), (272, 144), (272, 208), (394, 208)]
pos = ep + 16 + 20 + 4 + 2
for (x, y), (ox, oy) in zip(pts, old_pts):
    k = line.index(struct.pack("<2I", ox, oy), pos)
    struct.pack_into("<2I", line, k, x, y)
    pos = k + 8
# ссылка на класс CPointObj: в новом файле у него номер 9 (был 12)
line = bytearray(bytes(line).replace(b"\x0c\x80", b"\x09\x80"))
assert bytes(line).count(b"\x09\x80") == 3

# --- комментарий на схеме ---
NB = 6 + 11
assert d[0x1104 + NB + 0x41] == 0x5E
note_text = ("Водонагреватель УАП-400/0,9\r\n"
             "I1 - термоконтакт SK\r\n"
             "(замкнут, пока вода холодная)\r\n"
             "Q1 - контактор KM (ТЭНы)\r\n"
             "и лампа HG через R\r\n"
             "Реле KV заменено PLR")
nt = NB + 0x41
note = note[:nt] + cstr(note_text) + note[nt + 1 + 0x5E:]
put_dbl(note, NB, 32.0, 300.0, 328.0, 470.0)
# размеры текстового поля заметки (ширина + 3, высота + 4)
dims = note.index(struct.pack("<4I", 100, 1, 162, 234))
struct.pack_into("<4I", note, dims, 100, 1, 271, 146)

# --- свойства проекта ---
def replace_cstr(buf, old, new):
    o = cstr(old)
    k = buf.index(o)
    return buf[:k] + cstr(new) + buf[k + len(o):]

tail = replace_cstr(tail, "Пуск-Стоп (первая программа)",
                    "Водонагреватель УАП-400/0,9")
old_desc_k = tail.index(b"\x01\x31\x01\x30\x01\x30") + 6
old_desc_len = tail[old_desc_k]
desc = ("Водонагреватель УАП-400/0,9 (рис. 18.1). "
        "I1 - термоконтакт SK, Q1 - контактор KM (6 ТЭНов) и лампа HG. "
        "Вода холодная - SK замкнут - Q1 включает нагрев. "
        "Вода нагрелась - SK разомкнут - нагрев выключен.")
tail = tail[:old_desc_k] + cstr(desc) + tail[old_desc_k + 1 + old_desc_len:]
dt = tail.index(struct.pack("<H", 2026) + struct.pack("<H", 10))
struct.pack_into("<8H", tail, dt, 2026, 10, 26, 10, 0, 0, 0, 1)

data = struct.pack("<H", 4) + inp + out + note + line + tail
DST.write_bytes(data)
print(DST, len(data))
