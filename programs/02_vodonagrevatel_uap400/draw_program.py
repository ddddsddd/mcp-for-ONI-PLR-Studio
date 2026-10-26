"""Рисует программу для реле A1 (ONI PLR), которую нужно собрать в ONI PLR Studio.

Запуск:  python3 draw_program.py      -> program.png рядом со скриптом
Нужен matplotlib:  pip install matplotlib
"""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

GREEN, GREEN_DARK = "#1fae4f", "#0b7a32"
BLUE, BLUE_DARK = "#3d7cc9", "#1f4f8f"
WIRE = "#111111"

fig = plt.figure(figsize=(16, 11), dpi=110)
ax = fig.add_axes([0, 0.36, 1, 0.64])
ax.set_xlim(0, 16)
ax.set_ylim(0, 9)
ax.axis("off")

# фон как в ONI PLR Studio: серое поле в точку
ax.add_patch(Rectangle((0, 0), 16, 9, color="#e4e4e4", zorder=0))
for x in range(1, 32):
    for y in range(1, 18):
        ax.plot(x / 2, y / 2, ".", color="#9a9a9a", markersize=1.5, zorder=1)


def block(x, y, w, h, text, color, edge, top, side=None, side_left=True):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02",
                                fc=color, ec=edge, lw=2.5, zorder=3))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", color="white",
            fontsize=24, fontweight="bold", zorder=4)
    ax.text(x + w / 2, y + h + 0.15, top, ha="center", va="bottom", fontsize=15,
            fontweight="bold", zorder=4)
    if side:
        sx = x - 0.25 if side_left else x + w + 0.25
        ax.text(sx, y + h / 2, side, ha="right" if side_left else "left", va="center",
                fontsize=14, zorder=4)


def wire(points):
    xs, ys = zip(*points)
    ax.plot(xs, ys, color=WIRE, lw=2.5, zorder=2, solid_capstyle="round")


# входы
block(2.6, 6.2, 0.9, 1.3, "DI", GREEN, GREEN_DARK, "I1", "SK t°\nтермоконтакт")
block(2.6, 2.2, 0.9, 1.3, "DI", GREEN, GREEN_DARK, "I2", "SA\nвыключатель")

# блок «И»: 4 входа, используются 1 и 2
ax_, ay, aw, ah = 7.3, 3.6, 1.3, 2.6
block(ax_, ay, aw, ah, "&", BLUE, BLUE_DARK, "B001  «И»")
pins = [ay + ah - 0.35 - i * 0.62 for i in range(4)]
for i, py in enumerate(pins):
    ax.plot([ax_ - 0.35, ax_], [py, py], color=WIRE, lw=2.5, zorder=2)
    ax.text(ax_ + 0.12, py, str(i + 1), ha="left", va="center", color="white",
            fontsize=11, zorder=5)
ax.text(ax_ - 0.45, (pins[2] + pins[3]) / 2, "входы 3, 4\nне подключать", ha="right",
        va="center", fontsize=11, color="#555555", zorder=4)

# выходы
block(12.6, 6.2, 0.9, 1.3, "DO", GREEN, GREEN_DARK, "Q1", "KM — контактор\n(ТЭНы)", False)
block(12.6, 1.9, 0.9, 1.3, "DO", GREEN, GREEN_DARK, "Q2", "HG — лампа\n«Нагрев»", False)

# связи
wire([(3.5, 6.85), (5.4, 6.85), (5.4, pins[0]), (ax_ - 0.35, pins[0])])
wire([(3.5, 2.85), (5.4, 2.85), (5.4, pins[1]), (ax_ - 0.35, pins[1])])
out_y = ay + ah / 2
jx = 10.6
wire([(ax_ + aw, out_y), (jx, out_y)])
wire([(jx, out_y), (jx, 6.85), (12.6, 6.85)])
wire([(jx, out_y), (jx, 2.55), (12.6, 2.55)])
ax.plot(jx, out_y, "o", color=WIRE, markersize=9, zorder=3)

ax.text(8, 8.55, "Программа реле A1 для ONI PLR Studio:  Q1 = Q2 = I1 И I2",
        ha="center", fontsize=20, fontweight="bold")

# нижняя часть: как собрать и как работает
tx = fig.add_axes([0, 0, 1, 0.36])
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
tx.text(0.03, 0.92, steps, va="top", fontsize=14, linespacing=1.6, family="DejaVu Sans")

rows = [("I1 (SK)", "I2 (SA)", "Q1 (KM)", "Q2 (HG)"),
        ("0", "0", "0", "0"), ("1", "0", "0", "0"), ("0", "1", "0", "0"), ("1", "1", "1", "1")]
table = tx.table(cellText=rows[1:], colLabels=rows[0], cellLoc="center",
                 bbox=[0.58, 0.32, 0.38, 0.6])
table.auto_set_font_size(False)
table.set_fontsize(14)
for (r, _), cell in table.get_celld().items():
    if r == 0:
        cell.set_text_props(fontweight="bold")
    if r == 4:
        cell.set_facecolor("#d9f2e0")
tx.text(0.77, 0.2, "Нагрев (KM) и лампа (HG) включены только когда\n"
        "SA включён и вода холодная (SK замкнут).",
        ha="center", va="top", fontsize=13)

out = Path(__file__).with_name("program.png")
fig.savefig(out, facecolor="white")
print(out)
