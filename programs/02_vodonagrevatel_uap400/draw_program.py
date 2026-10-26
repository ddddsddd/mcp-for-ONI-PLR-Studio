"""Рисует реле A1 (ONI PLR) для водонагревателя УАП-400/0,9: подключение и программу.

Сверху — подключение реле: фаза L и ноль N, входы I1/I2, выходы Q1/Q2 с нагрузками.
Ниже — программа, которую нужно собрать в ONI PLR Studio, и таблица работы.

Запуск:  python3 draw_program.py      -> program.png рядом со скриптом
Нужен matplotlib:  pip install matplotlib
"""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

GREEN, GREEN_DARK = "#1fae4f", "#0b7a32"
BLUE, BLUE_DARK = "#3d7cc9", "#1f4f8f"
PHASE, NEUTRAL, SIGNAL = "#d62728", "#1f5fbf", "#111111"

fig = plt.figure(figsize=(16, 24), dpi=100)


# ---------------------------------------------------------------- подключение
w = fig.add_axes([0, 0.53, 1, 0.47])
w.set_xlim(0, 16)
w.set_ylim(0, 13)
w.axis("off")
w.text(8, 12.55, "1. Подключение реле A1: фаза L и ноль N", ha="center", fontsize=22,
       fontweight="bold")


def line(points, color, lw=3):
    xs, ys = zip(*points)
    w.plot(xs, ys, color=color, lw=lw, zorder=2, solid_capstyle="round")


def dot(x, y, color):
    w.plot(x, y, "o", color=color, markersize=11, zorder=4)


def terminal(x, y, name, below=False):
    w.add_patch(Circle((x, y), 0.17, fc="white", ec="black", lw=2.5, zorder=5))
    w.text(x, y - 0.55 if not below else y + 0.5, name, ha="center", va="center",
           fontsize=17, fontweight="bold", zorder=5)


def contact(x, y_top, y_bot, color, name, note):
    """Нормально открытый контакт на вертикальном проводе."""
    gap_top, gap_bot = y_top - 0.35, y_bot + 0.35
    line([(x, y_top), (x, gap_top)], color)
    line([(x, gap_top), (x - 0.45, gap_bot + 0.1)], color)
    line([(x, gap_bot), (x, y_bot)], SIGNAL)
    mid = (gap_top + gap_bot) / 2
    w.text(x - 0.6, mid + 0.35, name, ha="right", va="center", fontsize=17, fontweight="bold")
    w.text(x - 0.6, mid - 0.45, note, ha="right", va="center", fontsize=12, color="#444444")


# шины
YN, YL = 11.6, 10.8
line([(0.6, YN), (15.3, YN)], NEUTRAL, 4)
line([(0.6, YL), (11.0, YL)], PHASE, 4)
w.text(0.6, YN + 0.3, "N — ноль", color=NEUTRAL, fontsize=16, fontweight="bold")
w.text(11.2, YL, "L — фаза C\nпосле автомата SF", color=PHASE, fontsize=16,
       fontweight="bold", va="center")

# реле
X0, X1, YT, YB = 2.6, 13.4, 8.2, 5.4
w.add_patch(FancyBboxPatch((X0, YB), X1 - X0, YT - YB, boxstyle="round,pad=0.05",
                           fc="#f2f2f2", ec="black", lw=3, zorder=1))
w.text(X1 - 0.2, (YT + YB) / 2, "A1\nONI PLR", ha="right", va="center", fontsize=20,
       fontweight="bold")
TOP = {"L": 3.4, "N": 4.6, "I1": 7.3, "I2": 9.9, "I3": 11.2, "I4": 12.3}
for name, x in TOP.items():
    terminal(x, YT, name)
w.text(11.75, YT - 1.2, "резерв", ha="center", fontsize=12, color="#666666")
BOT = {"Q1": (3.4, 4.9), "Q2": (6.9, 8.6)}
for name, (c, o) in BOT.items():
    terminal(c, YB, "", below=True)
    terminal(o, YB, "", below=True)
    w.text((c + o) / 2, YB + 0.95, name, ha="center", fontsize=17, fontweight="bold")
    # контакт выхода внутри реле
    w.plot([c, c, c + 0.75], [YB + 0.17, YB + 0.45, YB + 0.75], color="black", lw=2)
    w.plot([o, o, o - 0.45], [YB + 0.17, YB + 0.45, YB + 0.45], color="black", lw=2)

# питание реле
line([(TOP["L"], YL), (TOP["L"], YT + 0.17)], PHASE)
dot(TOP["L"], YL, PHASE)
line([(TOP["N"], YN), (TOP["N"], YT + 0.17)], NEUTRAL)
dot(TOP["N"], YN, NEUTRAL)
w.text(TOP["L"] + 0.15, 9.3, "питание\nреле", fontsize=12, color="#444444")

# входы: фаза через SK и SA
contact(TOP["I1"], YL, YT + 0.17, PHASE, "SK t°", "замкнут, пока\nвода холодная")
dot(TOP["I1"], YL, PHASE)
contact(TOP["I2"], YL, YT + 0.17, PHASE, "SA", "нагрев\nразрешён")
dot(TOP["I2"], YL, PHASE)

# общие контакты выходов — от фазы
line([(1.5, YL), (1.5, 4.4), (BOT["Q2"][0], 4.4)], PHASE)
dot(1.5, YL, PHASE)
for c in (BOT["Q1"][0], BOT["Q2"][0]):
    line([(c, YB - 0.17), (c, 4.4)], PHASE)
dot(BOT["Q1"][0], 4.4, PHASE)
w.text(1.65, 4.6, "фаза на общие\nконтакты Q1, Q2", fontsize=12, color=PHASE, va="bottom")

# нагрузки
YNB = 0.7
o1, o2 = BOT["Q1"][1], BOT["Q2"][1]
line([(o1, YB - 0.17), (o1, 3.5)], SIGNAL)
w.add_patch(Rectangle((o1 - 0.5, 2.2), 1.0, 1.3, fc="white", ec="black", lw=3, zorder=3))
w.text(o1, 2.85, "KM", ha="center", va="center", fontsize=17, fontweight="bold", zorder=4)
w.text(o1 + 0.7, 2.85, "катушка\nконтактора\n(ТЭНы)", va="center", fontsize=12, color="#444444")
line([(o1, 2.2), (o1, YNB)], NEUTRAL)

line([(o2, YB - 0.17), (o2, 3.9)], SIGNAL)
w.add_patch(Rectangle((o2 - 0.22, 3.0), 0.44, 0.9, fc="white", ec="black", lw=3, zorder=3))
w.text(o2 + 0.4, 3.45, "R", va="center", fontsize=17, fontweight="bold")
line([(o2, 3.0), (o2, 2.35)], SIGNAL)
w.add_patch(Circle((o2, 1.95), 0.4, fc="white", ec="black", lw=3, zorder=3))
r = 0.28
w.plot([o2 - r, o2 + r], [1.95 - r, 1.95 + r], color="black", lw=2.5, zorder=4)
w.plot([o2 - r, o2 + r], [1.95 + r, 1.95 - r], color="black", lw=2.5, zorder=4)
w.text(o2 + 0.6, 1.95, "HG лампа\n«Нагрев»", va="center", fontsize=12, color="#444444")
line([(o2, 1.55), (o2, YNB)], NEUTRAL)

# ноль от нагрузок обратно на шину N
line([(o1, YNB), (15.3, YNB), (15.3, YN)], NEUTRAL, 4)
dot(o2, YNB, NEUTRAL)
w.text(15.1, 6.5, "N", color=NEUTRAL, fontsize=18, fontweight="bold", ha="right")

legend = [(PHASE, "фаза L"), (NEUTRAL, "ноль N"), (SIGNAL, "сигнал / после контакта")]
for i, (c, t) in enumerate(legend):
    w.plot([10.2, 10.9], [3.4 - i * 0.55] * 2, color=c, lw=4)
    w.text(11.05, 3.4 - i * 0.55, t, va="center", fontsize=13)


# ---------------------------------------------------------------- программа
ax = fig.add_axes([0, 0.2, 1, 0.33])
ax.set_xlim(0, 16)
ax.set_ylim(0, 9)
ax.axis("off")
ax.add_patch(Rectangle((0, 0), 16, 9, color="#e4e4e4", zorder=0))
for x in range(1, 32):
    for y in range(1, 17):
        ax.plot(x / 2, y / 2, ".", color="#9a9a9a", markersize=1.5, zorder=1)


def block(x, y, bw, bh, text, color, edge, top, side=None, side_left=True):
    ax.add_patch(FancyBboxPatch((x, y), bw, bh, boxstyle="round,pad=0.02",
                                fc=color, ec=edge, lw=2.5, zorder=3))
    ax.text(x + bw / 2, y + bh / 2, text, ha="center", va="center", color="white",
            fontsize=24, fontweight="bold", zorder=4)
    ax.text(x + bw / 2, y + bh + 0.15, top, ha="center", va="bottom", fontsize=15,
            fontweight="bold", zorder=4)
    if side:
        sx = x - 0.25 if side_left else x + bw + 0.25
        ax.text(sx, y + bh / 2, side, ha="right" if side_left else "left", va="center",
                fontsize=14, zorder=4)


def wire(points):
    xs, ys = zip(*points)
    ax.plot(xs, ys, color=SIGNAL, lw=2.5, zorder=2, solid_capstyle="round")


block(2.6, 5.6, 0.9, 1.3, "DI", GREEN, GREEN_DARK, "I1", "SK t°\nтермоконтакт")
block(2.6, 1.6, 0.9, 1.3, "DI", GREEN, GREEN_DARK, "I2", "SA\nвыключатель")
ax_, ay, aw, ah = 7.3, 3.0, 1.3, 2.6
block(ax_, ay, aw, ah, "&", BLUE, BLUE_DARK, "B001  «И»")
pins = [ay + ah - 0.35 - i * 0.62 for i in range(4)]
for i, py in enumerate(pins):
    ax.plot([ax_ - 0.35, ax_], [py, py], color=SIGNAL, lw=2.5, zorder=2)
    ax.text(ax_ + 0.12, py, str(i + 1), ha="left", va="center", color="white",
            fontsize=11, zorder=5)
ax.text(ax_ - 0.45, (pins[2] + pins[3]) / 2, "входы 3, 4\nне подключать", ha="right",
        va="center", fontsize=11, color="#555555", zorder=4)
block(12.6, 5.6, 0.9, 1.3, "DO", GREEN, GREEN_DARK, "Q1", "KM — контактор\n(ТЭНы)", False)
block(12.6, 1.3, 0.9, 1.3, "DO", GREEN, GREEN_DARK, "Q2", "HG — лампа\n«Нагрев»", False)
wire([(3.5, 6.25), (5.4, 6.25), (5.4, pins[0]), (ax_ - 0.35, pins[0])])
wire([(3.5, 2.25), (5.4, 2.25), (5.4, pins[1]), (ax_ - 0.35, pins[1])])
out_y, jx = ay + ah / 2, 10.6
wire([(ax_ + aw, out_y), (jx, out_y)])
wire([(jx, out_y), (jx, 6.25), (12.6, 6.25)])
wire([(jx, out_y), (jx, 1.95), (12.6, 1.95)])
ax.plot(jx, out_y, "o", color=SIGNAL, markersize=9, zorder=3)
ax.text(8, 8.2, "2. Программа в ONI PLR Studio:  Q1 = Q2 = I1 И I2", ha="center",
        fontsize=22, fontweight="bold")


# ---------------------------------------------------------------- как собрать
tx = fig.add_axes([0, 0, 1, 0.2])
tx.axis("off")
steps = (
    "Как собрать в ONI PLR Studio\n"
    "1.  Входы/Выходы → Вход: поставить I1 и I2.\n"
    "2.  Логические функции → И: поставить блок B001.\n"
    "3.  Входы/Выходы → Выход: поставить Q1 и Q2.\n"
    "4.  Подключение (F5): I1 → вход 1 блока «И»,\n"
    "      I2 → вход 2 блока «И».\n"
    "5.  Выход блока «И» → Q1 и тот же выход → Q2.\n"
    "6.  F3 — симулятор: щёлкать по I1 и I2 и смотреть Q1, Q2."
)
tx.text(0.03, 0.95, steps, va="top", fontsize=14, linespacing=1.6)
rows = [("I1 (SK)", "I2 (SA)", "Q1 (KM)", "Q2 (HG)"),
        ("0", "0", "0", "0"), ("1", "0", "0", "0"), ("0", "1", "0", "0"), ("1", "1", "1", "1")]
table = tx.table(cellText=rows[1:], colLabels=rows[0], cellLoc="center",
                 bbox=[0.58, 0.36, 0.38, 0.58])
table.auto_set_font_size(False)
table.set_fontsize(14)
for (r_, _), cell in table.get_celld().items():
    if r_ == 0:
        cell.set_text_props(fontweight="bold")
    if r_ == 4:
        cell.set_facecolor("#d9f2e0")
tx.text(0.77, 0.25, "Нагрев (KM) и лампа (HG) включены только когда\n"
        "SA включён и вода холодная (SK замкнут).", ha="center", va="top", fontsize=13)

out = Path(__file__).with_name("program.png")
fig.savefig(out, facecolor="white")
print(out)
