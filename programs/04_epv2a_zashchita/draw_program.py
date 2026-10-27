"""Программа реле A1 (ONI PLR) для ЭПВ-2А с защитой от перегрева и работы без воды — FBD.

Входы:  I1 SB1 «Пуск» (НО), I2 SB2 «Стоп» (НЗ), I3 SK1 регулирование (замкнут, пока t < 85 °C),
        I4 SK2 перегрев (НЗ, размыкается при 95 °C), I5 SL — есть вода в трубопроводе.
Выходы: Q1 KM нагрев (через аварийный SK3), Q2 HL1 «Нагрев», Q3 HL2 «Перегрев», Q4 HL3 «Нет воды».

Та же логика, что в LD на листе:
    M1 = (I1 + M1) · I2 · ¬M2       M2 = (¬I4 + M2) · I2
    Q1 = M1 · I3 · I4 · I5 · ¬M2    Q2 = Q1    Q3 = M2    Q4 = M1 · ¬I5

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

fig = plt.figure(figsize=(22, 20), dpi=100)
ax = fig.add_axes([0, 0.36, 1, 0.64])
ax.set_xlim(-1.6, 25.6)
ax.set_ylim(2.2, 20.6)
ax.axis("off")
ax.add_patch(Rectangle((-1.6, 2.2), 27.2, 17.3, color="#e6e6e6", zorder=0))
for gx in range(-3, 51):
    for gy in range(5, 39):
        ax.plot(gx / 2, gy / 2, ".", color="#a0a0a0", markersize=1.3, zorder=1)
ax.text(12, 20.0, "Программа реле A1 в ONI PLR Studio (FBD): ЭПВ-2А с защитами",
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
        return (x + w, y)
    ax.text(x + w + 0.2, y, label, ha="left", va="center", fontsize=12, zorder=4)
    return (x, y)


class Block:
    def __init__(self, x, yc, n_in, sym, num, note, color=BLUE, edge=BLUE_DARK, pin_names=None):
        self.w, self.h = 1.3, max(1.4, 0.7 * n_in + 0.2)
        self.x, self.y0 = x, yc - self.h / 2
        ax.add_patch(FancyBboxPatch((x, self.y0), self.w, self.h, boxstyle="round,pad=0.02",
                                    fc=color, ec=edge, lw=2, zorder=3))
        ax.text(x + self.w / 2, yc, sym, ha="center", va="center", color="white", fontsize=17,
                fontweight="bold", zorder=4)
        ax.text(x + self.w / 2, self.y0 + self.h + 0.12, num, ha="center", va="bottom",
                fontsize=12, fontweight="bold", zorder=4)
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
        if sym == "1":                       # инверсия на выходе «НЕ»
            ax.plot(x + self.w + 0.12, yc, "o", mfc="white", mec=WIRE, mew=2, markersize=8,
                    zorder=5)

    def pin(self, i):
        return (self.x - 0.35, self.pins[i])

    @property
    def o(self):
        return (self.out[0] + (0.24 if self.pins and len(self.pins) == 1 else 0), self.out[1])


# входы
i1 = io(1.0, 18.0, "DI", "I1", "SB1 «Пуск»\n(НО)")
i4 = io(1.0, 15.8, "DI", "I4", "SK2 перегрев\n(НЗ, 95 °C)")
i2 = io(1.0, 13.0, "DI", "I2", "SB2 «Стоп»\n(НЗ)")
i3 = io(1.0, 8.85, "DI", "I3", "SK1 регулирование\n(t < 85 °C)")
i5 = io(1.0, 4.05, "DI", "I5", "SL\nвода есть")

# блоки (номера как в проекте epv2a.xlg)
b002 = Block(4.4, 15.8, 1, "1", "B002 «НЕ»", "перегрев")
b001 = Block(4.4, 13.0, 1, "1", "B001 «НЕ»", "Стоп нажата")
b003 = Block(7.6, 14.4, 2, "RS", "B003 «RS»", "M2 перегрев", RS_C, RS_DARK, ["S", "R"])
b004 = Block(10.6, 11.6, 2, "≥1", "B004 «ИЛИ»", "сброс M1")
b005 = Block(12.6, 17.0, 2, "RS", "B005 «RS»", "M1 работа", RS_C, RS_DARK, ["S", "R"])
b006 = Block(17.5, 8.5, 4, "&", "B006 «И»", "нагрев")
b007 = Block(12.6, 4.05, 1, "1", "B007 «НЕ»", "нет воды")
b008 = Block(17.5, 4.4, 2, "&", "B008 «И»", "в работе без воды")

# выходы
q3 = io(21.2, 14.4, "DO", "Q3", "HL2 «Перегрев»", left=False)
q1 = io(21.2, 9.8, "DO", "Q1", "KM нагрев\n(через SK3)", left=False)
q2 = io(21.2, 7.2, "DO", "Q2", "HL1 «Нагрев»", left=False)
q4 = io(21.2, 4.4, "DO", "Q4", "HL3 «Нет воды»", left=False)

# связи
wire(i4, b002.pin(0))
dot(3.2, 15.8)
wire((3.2, 15.8), (3.2, b006.pins[2]), b006.pin(2))
wire(i2, b001.pin(0))
wire(b002.o, (6.9, 15.8), (6.9, b003.pins[0]), b003.pin(0))
wire(b001.o, (6.9, 13.0), (6.9, b003.pins[1]), b003.pin(1))
dot(6.4, 13.0)
wire((6.4, 13.0), (6.4, b004.pins[0]), b004.pin(0))
wire(b003.out, (9.6, 14.4), q3)
dot(9.6, 14.4)
wire((9.6, 14.4), (9.6, b004.pins[1]), b004.pin(1))
wire(i1, (11.9, 18.0), (11.9, b005.pins[0]), b005.pin(0))
wire(b004.out, (12.25, 11.6), (12.25, b005.pins[1]), b005.pin(1))
M1 = 14.6
wire(b005.out, (M1, 17.0), (M1, b006.pins[0]), b006.pin(0))
dot(M1, b006.pins[0])
wire((M1, b006.pins[0]), (M1, b008.pins[0]), b008.pin(0))
ax.text(M1 + 0.15, 15.8, "M1", fontsize=12, fontweight="bold", color=RS_DARK)
wire(i3, b006.pin(1))
dot(3.6, 4.05)
wire((3.6, 4.05), (3.6, b006.pins[3]), b006.pin(3))
wire(i5, b007.pin(0))
wire(b007.o, (16.6, 4.05), (16.6, b008.pins[1]), b008.pin(1))
wire(b006.out, (19.9, 8.5))
dot(19.9, 8.5)
wire((19.9, 8.5), (19.9, 9.8), q1)
wire((19.9, 8.5), (19.9, 7.2), q2)
wire(b008.out, q4)

# пояснения
tx = fig.add_axes([0, 0, 1, 0.36])
tx.axis("off")
tx.text(0.02, 0.97, "Что с чем соединить", fontsize=17, fontweight="bold", va="top")
links = [
    ("B001 «НЕ»", "вход ← I2"),
    ("B002 «НЕ»", "вход ← I4"),
    ("B003 «RS»", "S ← B002,  R ← B001;  выход (M2) → Q3, B004.2"),
    ("B004 «ИЛИ»", "1 ← B001,  2 ← B003;  выход → B005.R"),
    ("B005 «RS»", "S ← I1,  R ← B004;  выход (M1) → B006.1, B008.1"),
    ("B006 «И»", "1 ← B005,  2 ← I3,  3 ← I4,  4 ← I5;  выход → Q1, Q2"),
    ("B007 «НЕ»", "вход ← I5"),
    ("B008 «И»", "1 ← B005,  2 ← B007;  выход → Q4"),
]
for k, (b, t) in enumerate(links):
    y = 0.88 - k * 0.08
    tx.text(0.02, y, b, fontsize=13, fontweight="bold", va="top")
    tx.text(0.105, y, t, fontsize=13, va="top")
tx.text(0.02, 0.2, "«НЕ», «И», «ИЛИ» — Логические функции;  «RS» — Специальные функции → "
        "Цифровые → RS триггер (сброс R главнее установки S).\n"
        "Свободные входы «И» считаются 1, свободные входы «ИЛИ» — 0.",
        fontsize=11.5, va="top", color="#333333")

tx.text(0.57, 0.97, "Как работает", fontsize=17, fontweight="bold", va="top")
how = (
    "1.  SB1 «Пуск» → M1 = 1. SB2 «Стоп» → M1 = 0.\n"
    "2.  Нагрев (KM, HL1) — когда M1, t < 85 °C (SK1),\n"
    "     нет перегрева (SK2) и есть вода (SL).\n"
    "3.  Нет воды в работе → нагрев выключен, горит HL3.\n"
    "     Вода появилась → нагрев продолжается сам.\n"
    "4.  Перегрев 95 °C (SK2) → M2 = 1: M1 сброшен, горит HL2.\n"
    "     Защёлка держится и после остывания, «Пуск» не работает,\n"
    "     пока не нажать «Стоп».\n"
    "5.  SK3 на корпусе ТЭН отключает KM в обход реле."
)
tx.text(0.57, 0.88, how, fontsize=13, va="top", linespacing=1.55)
tx.text(0.57, 0.27, "Та же логика, что в LD на листе:", fontsize=13, fontweight="bold", va="top")
tx.text(0.57, 0.2, "M1 = (I1 + M1) · I2 · ¬M2     M2 = (¬I4 + M2) · I2\n"
        "Q1 = Q2 = M1 · I3 · I4 · I5    Q3 = M2    Q4 = M1 · ¬I5",
        fontsize=13, va="top", family="DejaVu Sans Mono", linespacing=1.6)

out = Path(__file__).with_name("program.png")
fig.savefig(out, facecolor="white")
print(out)
