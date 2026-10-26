"""Полная схема водонагревателя УАП-400/0,9 с программируемым реле A1 (ONI PLR).

На одном листе: силовая цепь с ТЭНами, цепь управления, реле A1 со всеми клеммами,
программа для ONI PLR Studio, клеммы реле, работа схемы и перечень элементов.

Запуск:  python3 draw_full.py   -> full_scheme.png и full_scheme.pdf рядом со скриптом
Нужен matplotlib:  pip install matplotlib
"""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

PHASE, NEUTRAL, BLACK = "#d62728", "#1f5fbf", "#111111"
GREEN, GREEN_DARK, BLUE, BLUE_DARK = "#1fae4f", "#0b7a32", "#3d7cc9", "#1f4f8f"
LW = 2.6

fig = plt.figure(figsize=(24, 17), dpi=100)
frame = fig.add_axes([0, 0, 1, 1])
frame.axis("off")
frame.add_patch(Rectangle((0.008, 0.01), 0.984, 0.98, transform=frame.transAxes,
                          fill=False, lw=2.5))
frame.text(0.5, 0.965, "Емкостной электроводонагреватель УАП-400/0,9 — схема электрическая "
           "принципиальная с программируемым реле A1 (ONI PLR)",
           ha="center", va="center", fontsize=21, fontweight="bold")

# =================================================================== схема
s = fig.add_axes([0.015, 0.03, 0.6, 0.9])
s.set_xlim(0, 30)
s.set_ylim(0, 30)
s.axis("off")


def ln(pts, color=BLACK, lw=LW, ls="-"):
    xs, ys = zip(*pts)
    s.plot(xs, ys, color=color, lw=lw, ls=ls, solid_capstyle="round", zorder=2)


def dot(x, y, color=BLACK):
    s.plot(x, y, "o", color=color, markersize=8, zorder=5)


def txt(x, y, t, size=14, bold=True, **kw):
    s.text(x, y, t, fontsize=size, fontweight="bold" if bold else "normal", zorder=6, **kw)


def rect(x, y, w, h, lw=LW, fc="white"):
    s.add_patch(Rectangle((x, y), w, h, fc=fc, ec=BLACK, lw=lw, zorder=3))


def terminal(x, y):
    s.add_patch(Circle((x, y), 0.22, fc="white", ec=BLACK, lw=2.2, zorder=6))


def no_contact(x, y_top, y_bot, color_in, color_out, name, note=None):
    """Замыкающий контакт на вертикальном проводе, сверху вниз."""
    a, b = y_top - 0.5, y_bot + 0.5
    ln([(x, y_top), (x, a)], color_in)
    ln([(x, a), (x - 0.55, b + 0.15)], color_in)
    ln([(x, b), (x, y_bot)], color_out)
    txt(x - 0.75, (a + b) / 2 + 0.25, name, 14, ha="right", va="center")
    if note:
        txt(x - 0.75, (a + b) / 2 - 0.45, note, 10, False, ha="right", va="center",
            color="#444444")


# ---------- силовая цепь
PH = {"A": 1.6, "B": 3.6, "C": 5.6}
XN = 7.4
for name, x in PH.items():
    txt(x, 29.3, name, 17, ha="center")
    ln([(x, 28.9), (x, 27.1)])
    rect(x - 0.27, 25.4, 0.54, 1.7)
    ln([(x, 27.3), (x, 25.2)], lw=1.5)
    ln([(x, 25.4), (x, 22.6)])
    ln([(x, 21.2), (x + 0.6, 22.45)])                     # силовой контакт KM
    ln([(x, 21.2), (x, 19.6)])
    ln([(x - 0.5, 19.6), (x + 0.5, 19.6)])
    dot(x, 19.6)
txt(PH["A"] - 0.55, 26.25, "FU1", 12, ha="right", va="center")
txt(PH["B"] - 0.55, 26.25, "FU2", 12, ha="right", va="center")
txt(PH["C"] - 0.55, 26.25, "FU3", 12, ha="right", va="center")
ln([(1.9, 21.85), (6.3, 21.85)], lw=1.5, ls=(0, (4, 3)))
txt(0.55, 21.85, "KM", 14, va="center")

ek = 1
for x in PH.values():
    for dx in (-0.5, 0.5):
        ln([(x + dx, 19.6), (x + dx, 18.6)])
        rect(x + dx - 0.22, 16.4, 0.44, 2.2)
        s.text(x + dx, 17.5, f"EK{ek}", rotation=90, ha="center", va="center", fontsize=10,
               fontweight="bold", zorder=6)
        ln([(x + dx, 16.4), (x + dx, 15.2)])
        ek += 1
ln([(PH["A"] - 0.5, 15.2), (XN, 15.2)])
dot(XN, 15.2)
txt(4.5, 14.3, "EK1…EK6 — ТЭНы, по 2 на фазу,\nсоединение «звезда» с нулём N",
    11, False, ha="center", va="top")

# ---------- нулевая шина
txt(XN, 29.3, "N", 17, ha="center", color=NEUTRAL)
ln([(XN, 28.9), (XN, 15.2)], NEUTRAL)
ln([(XN, 28.2), (29.2, 28.2), (29.2, 1.4)], NEUTRAL)
dot(XN, 28.2, NEUTRAL)
txt(29.0, 20, "N", 15, ha="right", color=NEUTRAL)

# ---------- автомат SF и шина L
XL = 10.2
ln([(PH["C"], 24.4), (XL, 24.4), (XL, 23.6)], PHASE)
dot(PH["C"], 24.4, PHASE)
rect(XL - 0.95, 22.75, 0.42, 0.65, lw=2)                   # тепловой расцепитель
ln([(XL, 21.6), (XL - 0.45, 23.3)], PHASE)
ln([(XL - 0.17, 23.75), (XL + 0.17, 23.45)], PHASE, 2)
ln([(XL - 0.17, 23.45), (XL + 0.17, 23.75)], PHASE, 2)
ln([(XL, 21.6), (XL, 21.0)], PHASE)
txt(XL + 0.35, 22.8, "SF", 15, va="center")
YL = 21.0
ln([(XL, YL), (24.0, YL)], PHASE, 3.2)
dot(XL, YL, PHASE)
txt(24.2, YL, "L ~220 В", 14, va="center", color=PHASE)

# ---------- реле A1
RX0, RX1, RY0, RY1 = 12.0, 27.6, 11.8, 17.0
s.add_patch(FancyBboxPatch((RX0, RY0), RX1 - RX0, RY1 - RY0, boxstyle="round,pad=0.08",
                           fc="#f3f3f3", ec=BLACK, lw=3.2, zorder=1))
txt(RX1 - 0.3, RY1 + 0.45, "A1  ONI PLR-S-CPU-1410", 15, ha="right")
TOP = {"L": 13.2, "N": 15.0, "I1": 18.3, "I2": 21.0, "I3": 23.2, "I4": 25.2}
for n, x in TOP.items():
    terminal(x, RY1)
    txt(x, RY1 - 0.65, n, 13, ha="center", va="center")
txt(24.2, RY1 - 1.35, "резерв", 10, False, ha="center", color="#666666")
OUT = {"Q1": (13.2, 15.0), "Q2": (17.6, 20.2)}
for n, (c, o) in OUT.items():
    terminal(c, RY0)
    terminal(o, RY0)
    txt((c + o) / 2, RY0 + 1.45, n, 13, ha="center")
    s.plot([c, c, c + 1.0], [RY0 + 0.22, RY0 + 0.55, RY0 + 1.0], color=BLACK, lw=2, zorder=4)
    s.plot([o, o, o - 0.55], [RY0 + 0.22, RY0 + 0.55, RY0 + 0.55], color=BLACK, lw=2,
           zorder=4)
    txt(c - 0.35, RY0 - 0.55, "общ.", 9, False, ha="right", va="center", color="#555555")
txt(RX1 - 0.4, RY0 + 0.35, "Q3…  резерв", 10, False, ha="right", color="#666666")

# программа внутри реле
px, py = 21.6, 13.9
for i, (n, yy) in enumerate((("I1", py + 0.55), ("I2", py - 0.25))):
    txt(px - 0.1, yy, n, 10, ha="right", va="center")
    s.plot([px, px + 0.9], [yy, yy], color="#555555", lw=1.6, zorder=4)
s.add_patch(Rectangle((px + 0.9, py - 0.55), 1.0, 1.4, fc=BLUE, ec=BLUE_DARK, lw=1.8, zorder=4))
s.text(px + 1.4, py + 0.15, "&", color="white", fontsize=15, fontweight="bold", ha="center",
       va="center", zorder=5)
s.plot([px + 1.9, px + 2.6], [py + 0.15, py + 0.15], color="#555555", lw=1.6, zorder=4)
for n, yy in (("Q1", py + 0.55), ("Q2", py - 0.25)):
    s.plot([px + 2.6, px + 2.6, px + 3.1], [py + 0.15, yy, yy], color="#555555", lw=1.6,
           zorder=4)
    txt(px + 3.2, yy, n, 10, ha="left", va="center")
txt(px + 1.4, py - 1.05, "программа", 9, False, ha="center", color="#555555")

# питание реле
ln([(TOP["L"], YL), (TOP["L"], RY1 + 0.22)], PHASE)
dot(TOP["L"], YL, PHASE)
ln([(TOP["N"], 28.2), (TOP["N"], RY1 + 0.22)], NEUTRAL)
dot(TOP["N"], 28.2, NEUTRAL)

# входы
no_contact(TOP["I1"], YL, RY1 + 0.22, PHASE, BLACK, "SK t°", "замкнут, пока\nвода холодная")
dot(TOP["I1"], YL, PHASE)
no_contact(TOP["I2"], YL, RY1 + 0.22, PHASE, BLACK, "SA", "нагрев\nразрешён")
dot(TOP["I2"], YL, PHASE)

# общие контакты выходов от L
YC = 9.6
ln([(XL, YL), (XL, YC), (OUT["Q2"][0], YC)], PHASE)
for c in (OUT["Q1"][0], OUT["Q2"][0]):
    ln([(c, RY0 - 0.22), (c, YC)], PHASE)
dot(OUT["Q1"][0], YC, PHASE)

# нагрузки
YN0 = 1.4
o1, o2 = OUT["Q1"][1], OUT["Q2"][1]
ln([(o1, RY0 - 0.22), (o1, 7.9)])
rect(o1 - 0.75, 5.3, 1.5, 2.6)
txt(o1, 6.6, "KM", 15, ha="center", va="center")
txt(o1 + 1.0, 6.6, "катушка\nконтактора", 10, False, va="center", color="#444444")
ln([(o1, 5.3), (o1, YN0)], NEUTRAL)

ln([(o2, RY0 - 0.22), (o2, 9.0)])
rect(o2 - 0.3, 7.3, 0.6, 1.7)
txt(o2 + 0.6, 8.15, "R", 15, va="center")
ln([(o2, 7.3), (o2, 5.65)])
s.add_patch(Circle((o2, 4.85), 0.8, fc="white", ec=BLACK, lw=LW, zorder=3))
r = 0.56
s.plot([o2 - r, o2 + r], [4.85 - r, 4.85 + r], color=BLACK, lw=2.2, zorder=4)
s.plot([o2 - r, o2 + r], [4.85 + r, 4.85 - r], color=BLACK, lw=2.2, zorder=4)
txt(o2 + 1.1, 4.85, "HG", 15, va="center")
txt(o2 + 1.1, 4.0, "лампа «Нагрев»", 10, False, va="center", color="#444444")
ln([(o2, 4.05), (o2, YN0)], NEUTRAL)
ln([(o1, YN0), (29.2, YN0)], NEUTRAL)
dot(o2, YN0, NEUTRAL)

# легенда
for i, (c, t) in enumerate(((PHASE, "фаза L (цепь управления)"),
                            (NEUTRAL, "ноль N"),
                            (BLACK, "силовая цепь / после контакта"))):
    yy = 10.6 - i * 0.9
    s.plot([0.6, 1.8], [yy, yy], color=c, lw=4)
    txt(2.0, yy, t, 11, False, va="center")

# =================================================================== правая колонка
right = 0.63


def panel(y0, h):
    a = fig.add_axes([right, y0, 0.355, h])
    a.axis("off")
    return a


# ---------- программа
p = fig.add_axes([right, 0.70, 0.355, 0.235])
p.set_xlim(0, 16)
p.set_ylim(0, 9)
p.axis("off")
p.add_patch(Rectangle((0, 0), 16, 8.2, color="#e4e4e4", zorder=0))
for gx in range(1, 32):
    for gy in range(1, 16):
        p.plot(gx / 2, gy / 2, ".", color="#9a9a9a", markersize=1.2, zorder=1)
p.text(8, 8.6, "Программа A1 в ONI PLR Studio (FBD)", ha="center", va="center", fontsize=16,
       fontweight="bold")


def fblock(x, y, w, h, t, fc, ec, top, side=None, left=True):
    p.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02", fc=fc, ec=ec, lw=2,
                               zorder=3))
    p.text(x + w / 2, y + h / 2, t, ha="center", va="center", color="white", fontsize=16,
           fontweight="bold", zorder=4)
    p.text(x + w / 2, y + h + 0.12, top, ha="center", va="bottom", fontsize=12,
           fontweight="bold")
    if side:
        p.text(x - 0.2 if left else x + w + 0.2, y + h / 2, side, ha="right" if left else "left",
               va="center", fontsize=11)


fblock(3.0, 5.0, 1.0, 1.4, "DI", GREEN, GREEN_DARK, "I1", "SK t°")
fblock(3.0, 1.2, 1.0, 1.4, "DI", GREEN, GREEN_DARK, "I2", "SA")
fblock(7.2, 2.4, 1.4, 2.8, "&", BLUE, BLUE_DARK, "B001 «И»")
fblock(12.0, 5.0, 1.0, 1.4, "DO", GREEN, GREEN_DARK, "Q1", "KM", False)
fblock(12.0, 1.2, 1.0, 1.4, "DO", GREEN, GREEN_DARK, "Q2", "HG", False)
pins = [5.2 - 0.35 - i * 0.67 for i in range(4)]
for i, y in enumerate(pins):
    p.plot([6.85, 7.2], [y, y], color=BLACK, lw=2, zorder=2)
    p.text(7.3, y, str(i + 1), color="white", fontsize=9, va="center", zorder=5)
p.text(7.9, 2.0, "входы 3, 4 свободны", ha="center", va="center", fontsize=9,
       color="#555555")


def pw(pts):
    xs, ys = zip(*pts)
    p.plot(xs, ys, color=BLACK, lw=2, zorder=2)


pw([(4.0, 5.7), (5.6, 5.7), (5.6, pins[0]), (6.85, pins[0])])
pw([(4.0, 1.9), (5.6, 1.9), (5.6, pins[1]), (6.85, pins[1])])
pw([(8.6, 3.8), (10.4, 3.8)])
pw([(10.4, 3.8), (10.4, 5.7), (12.0, 5.7)])
pw([(10.4, 3.8), (10.4, 1.9), (12.0, 1.9)])
p.plot(10.4, 3.8, "o", color=BLACK, markersize=7, zorder=3)
p.text(8, 0.45, "Q1 = I1 · I2        Q2 = Q1", ha="center", fontsize=14, fontweight="bold")


def table(ax, title, rows, widths, bbox, fs=11, head_bold=True, green_row=None):
    ax.text(bbox[0], bbox[1] + bbox[3] + 0.03, title, fontsize=14, fontweight="bold",
            transform=ax.transAxes)
    t = ax.table(cellText=rows[1:], colLabels=rows[0], colWidths=widths, cellLoc="left",
                 bbox=bbox)
    t.auto_set_font_size(False)
    t.set_fontsize(fs)
    for (r_, _), cell in t.get_celld().items():
        cell.set_linewidth(1)
        cell.PAD = 0.03
        if r_ == 0 and head_bold:
            cell.set_text_props(fontweight="bold")
            cell.set_facecolor("#eeeeee")
        if green_row is not None and r_ == green_row:
            cell.set_facecolor("#d9f2e0")
    return t


# ---------- клеммы реле
k = panel(0.475, 0.2)
table(k, "Клеммы реле A1", [
    ("Клемма", "Подключение"),
    ("L", "фаза после автомата SF (питание реле)"),
    ("N", "нулевой провод N"),
    ("I1", "фаза через термоконтакт SK t°"),
    ("I2", "фаза через выключатель SA"),
    ("I3, I4", "не подключены (резерв)"),
    ("Q1 общ. / Q1", "фаза L  /  катушка KM → N"),
    ("Q2 общ. / Q2", "фаза L  /  резистор R → лампа HG → N"),
], [0.22, 0.78], [0, 0, 1, 0.9])

# ---------- работа схемы
w = panel(0.27, 0.18)
table(w, "Работа схемы", [
    ("SK t° (I1)", "SA (I2)", "Q1 → KM, ТЭНы", "Q2 → HG"),
    ("разомкнут", "выключен", "выкл", "не горит"),
    ("замкнут", "выключен", "выкл", "не горит"),
    ("разомкнут", "включён", "выкл", "не горит"),
    ("замкнут", "включён", "ВКЛ — нагрев", "горит"),
], [0.25, 0.25, 0.27, 0.23], [0, 0.3, 1, 0.62], green_row=4)
w.text(0, 0.22, "SK замкнут, пока вода холодная. Нагрев идёт, только когда SA включён\n"
       "и вода не нагрета. Вода нагрелась → SK разомкнулся → KM отключает ТЭНы.",
       fontsize=11, va="top", transform=w.transAxes)

# ---------- перечень элементов
e = panel(0.035, 0.205)
table(e, "Перечень элементов", [
    ("Поз.", "Наименование", "Кол.", "Примечание"),
    ("A1", "Программируемое реле ONI PLR-S-CPU-1410", "1", "программа vodonagrevatel.xlg"),
    ("EK1…EK6", "Электронагреватель трубчатый (ТЭН)", "6", "по 2 на фазу, «звезда»"),
    ("FU1…FU3", "Предохранитель плавкий", "3", "силовая цепь"),
    ("HG", "Лампа сигнальная «Нагрев»", "1", "~220 В"),
    ("KM", "Контактор электромагнитный", "1", "катушка ~220 В"),
    ("R", "Резистор добавочный", "1", "для лампы HG"),
    ("SA", "Выключатель", "1", "разрешение нагрева"),
    ("SF", "Выключатель автоматический", "1", "цепь управления"),
    ("SK", "Датчик-реле температуры", "1", "замыкающий контакт"),
], [0.13, 0.5, 0.07, 0.3], [0, 0, 1, 0.92], fs=10)

frame.text(0.62, 0.012, "Реле A1 показано в исполнении ~220 В. Для исполнения =24 В клеммы L/N "
           "и контакты SK, SA питаются от блока питания 24 В; выходы Q1, Q2 по-прежнему "
           "коммутируют ~220 В.", fontsize=10, ha="center", va="bottom", color="#444444")

here = Path(__file__).parent
fig.savefig(here / "full_scheme.png", facecolor="white")
fig.savefig(here / "full_scheme.pdf", facecolor="white")
print(here / "full_scheme.png")
