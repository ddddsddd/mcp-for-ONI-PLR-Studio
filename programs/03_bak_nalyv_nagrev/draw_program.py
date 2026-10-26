"""Программа реле A1 (ONI PLR) для бака с наливом и нагревом — FBD для ONI PLR Studio.

Входы:  I1 SB1 «Пуск» (НО), I2 SB2 «Стоп» (НЗ), I3 SL1 нижний уровень, I4 SL2 верхний
        уровень, I5 SK t° (замкнут, пока t < уставки).
Выходы: Q1 YA клапан налива, Q2 KM нагрев (ТЭН), Q3 HL1 «Работа», Q4 HL2 «Нагрев».

Та же логика, что в LD на листе:
    M1 = (I1 + M1) · I2            Q1 = M1 · (¬I3 + Q1) · ¬I4
    Q2 = M1 · ¬Q1 · I3 · I5        Q3 = M1        Q4 = Q2

Запуск:  python3 draw_program.py   -> program.png рядом со скриптом
Нужен matplotlib:  pip install matplotlib
"""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

GREEN, GREEN_DARK = "#1fae4f", "#0b7a32"
BLUE, BLUE_DARK = "#3d7cc9", "#1f4f8f"
RS_C, RS_DARK = "#7a5cc4", "#4b3590"
WIRE = "#111111"

fig = plt.figure(figsize=(22, 21), dpi=100)
ax = fig.add_axes([0, 0.36, 1, 0.64])
ax.set_xlim(-1.6, 28.6)
ax.set_ylim(1.2, 20.6)
ax.axis("off")
ax.add_patch(Rectangle((-1.6, 1.2), 30.2, 18.3, color="#e6e6e6", zorder=0))
for gx in range(-3, 57):
    for gy in range(3, 39):
        ax.plot(gx / 2, gy / 2, ".", color="#a0a0a0", markersize=1.3, zorder=1)
ax.text(13.7, 20.0, "Программа реле A1 в ONI PLR Studio (FBD): налив и нагрев бака",
        ha="center", va="center", fontsize=22, fontweight="bold")


def wire(*pts):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=WIRE, lw=2.2, zorder=2, solid_capstyle="round")


def dot(x, y):
    ax.plot(x, y, "o", color=WIRE, markersize=8, zorder=6)


def io(x, y, kind, name, label, left=True):
    w, h = 1.1, 1.2
    ax.add_patch(FancyBboxPatch((x, y - h / 2), w, h, boxstyle="round,pad=0.02", fc=GREEN,
                                ec=GREEN_DARK, lw=2, zorder=3))
    ax.text(x + w / 2, y, kind, ha="center", va="center", color="white", fontsize=15,
            fontweight="bold", zorder=4)
    ax.text(x + w / 2, y + h / 2 + 0.12, name, ha="center", va="bottom", fontsize=14,
            fontweight="bold", zorder=4)
    if left:
        ax.text(x - 0.2, y, label, ha="right", va="center", fontsize=12, zorder=4)
    else:
        ax.text(x + w + 0.2, y, label, ha="left", va="center", fontsize=12, zorder=4)
    return (x + w, y) if left else (x, y)


class Block:
    """Функциональный блок: входы слева (снизу вверх нумерация сверху), выход справа."""

    def __init__(self, x, yc, n_in, sym, num, note, color=BLUE, edge=BLUE_DARK, pin_names=None):
        self.w = 1.3
        self.h = max(1.4, 0.7 * n_in + 0.2)
        self.x, self.y0 = x, yc - self.h / 2
        ax.add_patch(FancyBboxPatch((x, self.y0), self.w, self.h, boxstyle="round,pad=0.02",
                                    fc=color, ec=edge, lw=2, zorder=3))
        ax.text(x + self.w / 2, yc, sym, ha="center", va="center", color="white", fontsize=17,
                fontweight="bold", zorder=4)
        ax.text(x + self.w / 2, self.y0 + self.h + 0.12, num, ha="center", va="bottom",
                fontsize=12, fontweight="bold", zorder=4)
        if note:
            ax.text(x + self.w / 2, self.y0 - 0.12, note, ha="center", va="top", fontsize=10,
                    color="#333333", zorder=4)
        top = self.y0 + self.h - 0.45
        self.pins = [top - i * 0.7 for i in range(n_in)] if n_in > 1 else [yc]
        for i, py in enumerate(self.pins):
            ax.plot([x - 0.35, x], [py, py], color=WIRE, lw=2.2, zorder=2)
            label = pin_names[i] if pin_names else (str(i + 1) if n_in > 1 else "")
            ax.text(x + 0.1, py, label, ha="left", va="center", color="white", fontsize=9,
                    zorder=5)
        self.out = (x + self.w, yc)

    def pin(self, i):
        return (self.x - 0.35, self.pins[i])


# ---------------------------------------------------------------- входы
i1 = io(1.0, 18.0, "DI", "I1", "SB1 «Пуск»\n(НО)")
i2 = io(1.0, 15.8, "DI", "I2", "SB2 «Стоп»\n(НЗ)")
i3 = io(1.0, 12.0, "DI", "I3", "SL1\nнижний уровень")
i4 = io(1.0, 9.35, "DI", "I4", "SL2\nверхний уровень")
i5 = io(1.0, 3.55, "DI", "I5", "SK t°\n(t < уставки)")

# ---------------------------------------------------------------- блоки
b001 = Block(4.4, 15.8, 1, "1", "B001 «НЕ»", "Стоп нажата")
b002 = Block(7.6, 17.0, 2, "RS", "B002 «RS»", "M1 «Работа»", RS_C, RS_DARK, ["S", "R"])
b003 = Block(4.4, 12.0, 1, "1", "B003 «НЕ»", "ниже SL1")
b004 = Block(11.2, 12.2, 2, "&", "B004 «И»", "начать налив")
b005 = Block(11.2, 7.4, 1, "1", "B005 «НЕ»", "не в работе")
b006 = Block(13.8, 9.0, 2, "≥1", "B006 «ИЛИ»", "конец налива")
b007 = Block(16.4, 10.6, 2, "RS", "B007 «RS»", "налив", RS_C, RS_DARK, ["S", "R"])
b008 = Block(19.0, 6.9, 1, "1", "B008 «НЕ»", "не наливаем")
b009 = Block(21.6, 4.6, 4, "&", "B009 «И»", "нагрев")
for b in (b001, b003, b005, b008):           # у «НЕ» символ инверсии на выходе
    ax.plot(b.out[0] + 0.12, b.out[1], "o", mfc="white", mec=WIRE, mew=2, markersize=8,
            zorder=5)

# ---------------------------------------------------------------- выходы
q3 = io(24.6, 17.0, "DO", "Q3", "HL1 «Работа»", left=False)
q1 = io(24.6, 10.6, "DO", "Q1", "YA клапан\nналива", left=False)
q2 = io(24.6, 5.6, "DO", "Q2", "KM нагрев\n(ТЭН)", left=False)
q4 = io(24.6, 3.0, "DO", "Q4", "HL2 «Нагрев»", left=False)

# ---------------------------------------------------------------- связи
wire(i1, (7.0, 18.0), (7.0, b002.pins[0]), b002.pin(0))
wire(i2, b001.pin(0))
wire((b001.out[0] + 0.24, b001.out[1]), (6.8, 15.8), (6.8, b002.pins[1]), b002.pin(1))

BUS = 10.0                                    # шина M1
wire(b002.out, (BUS, 17.0), q3)
dot(BUS, 17.0)
wire((BUS, 17.0), (BUS, b009.pins[0]), b009.pin(0))
wire((BUS, b004.pins[0]), b004.pin(0))
dot(BUS, b004.pins[0])
wire((BUS, 7.4), b005.pin(0))
dot(BUS, 7.4)

wire(i3, b003.pin(0))
dot(3.2, 12.0)
wire((3.2, 12.0), (3.2, b009.pins[2]), b009.pin(2))
wire((b003.out[0] + 0.24, 12.0), (10.6, 12.0), (10.6, b004.pins[1]), b004.pin(1))

wire(i4, b006.pin(0))
wire((b005.out[0] + 0.24, 7.4), (13.1, 7.4), (13.1, b006.pins[1]), b006.pin(1))

wire(b004.out, (15.6, 12.2), (15.6, b007.pins[0]), b007.pin(0))
wire(b006.out, (15.4, 9.0), (15.4, b007.pins[1]), b007.pin(1))
wire(b007.out, q1)
dot(18.4, 10.6)
wire((18.4, 10.6), (18.4, 6.9), b008.pin(0))
wire((b008.out[0] + 0.24, 6.9), (20.8, 6.9), (20.8, b009.pins[1]), b009.pin(1))
wire(i5, b009.pin(3))

wire(b009.out, (23.6, 4.6))
dot(23.6, 4.6)
wire((23.6, 4.6), (23.6, 5.6), q2)
wire((23.6, 4.6), (23.6, 3.0), q4)

ax.text(BUS + 0.15, 15.6, "M1", fontsize=12, fontweight="bold", color="#4b3590", zorder=5)

# ---------------------------------------------------------------- пояснения
tx = fig.add_axes([0, 0, 1, 0.36])
tx.axis("off")
tx.text(0.02, 0.97, "Что с чем соединить", fontsize=17, fontweight="bold", va="top")
links = [
    ("B001 «НЕ»", "вход ← I2"),
    ("B002 «RS»", "S ← I1,  R ← B001;  выход → Q3, B004.1, B005, B009.1"),
    ("B003 «НЕ»", "вход ← I3"),
    ("B004 «И»", "1 ← B002,  2 ← B003  (3, 4 свободны);  выход → B007.S"),
    ("B005 «НЕ»", "вход ← B002"),
    ("B006 «ИЛИ»", "1 ← I4,  2 ← B005  (3, 4 свободны);  выход → B007.R"),
    ("B007 «RS»", "S ← B004,  R ← B006;  выход → Q1, B008"),
    ("B008 «НЕ»", "вход ← B007"),
    ("B009 «И»", "1 ← B002,  2 ← B008,  3 ← I3,  4 ← I5;  выход → Q2, Q4"),
]
for k, (b, t) in enumerate(links):
    y = 0.88 - k * 0.072
    tx.text(0.02, y, b, fontsize=13, fontweight="bold", va="top")
    tx.text(0.105, y, t, fontsize=13, va="top")
tx.text(0.02, 0.2, "«НЕ», «И», «ИЛИ» — Логические функции;  «RS» — Специальные функции → "
        "RS-триггер (у него сброс R главнее установки S).\n"
        "Свободные входы «И» считаются 1, свободные входы «ИЛИ» — 0, их не подключать.",
        fontsize=11.5, va="top", color="#333333")

tx.text(0.57, 0.97, "Как работает", fontsize=17, fontweight="bold", va="top")
how = (
    "1.  SB1 «Пуск» → M1 = 1, горит HL1 «Работа».\n"
    "     SB2 «Стоп» (НЗ) → M1 = 0, всё отключается.\n"
    "2.  Уровень ниже SL1 → открывается клапан YA (налив)\n"
    "     и держится открытым до верхнего уровня SL2.\n"
    "3.  Налив окончен, вода выше SL1 и t < уставки (SK замкнут)\n"
    "     → KM включает ТЭНы, горит HL2 «Нагрев».\n"
    "4.  Во время налива нагрев выключен.\n"
    "     Вода нагрелась (SK разомкнут) → нагрев выключается."
)
tx.text(0.57, 0.88, how, fontsize=13, va="top", linespacing=1.55)
tx.text(0.57, 0.27, "Та же логика, что в LD на листе:", fontsize=13, fontweight="bold", va="top")
tx.text(0.57, 0.2, "M1 = (I1 + M1) · I2          Q1 = M1 · (¬I3 + Q1) · ¬I4\n"
        "Q2 = M1 · ¬Q1 · I3 · I5     Q3 = M1          Q4 = Q2",
        fontsize=13, va="top", family="DejaVu Sans Mono", linespacing=1.6)

out = Path(__file__).with_name("program.png")
fig.savefig(out, facecolor="white")
print(out)
