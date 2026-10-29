"""Рисует программу реверсивного транспортёра прямо из transporter.xlg.

Запуск:  python3 draw_program.py   -> program.png рядом со скриптом
Нужен matplotlib:  pip install matplotlib
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "tools"))
from xlg_dump import parse  # noqa: E402

IO = {
    100: "SB1 «ПУСК»\n(вперёд)", 101: "SB2 «НАЗАД»", 102: "SQ1 конец", 103: "SQ2 начало",
    12000: "HA звонок 3 с", 12001: "KM1 вперёд", 12002: "KM2 назад",
}
NOTES = {
    100000: "стоп вперёд", 100001: "M1 вперёд", 100002: "стоп назад", 100003: "M2 назад",
    100004: "T1 3 с", 100005: "T2 3 с", 100006: "есть ход", 100007: "мотор вкл.",
    100008: "звонок",
}
SYM = {"CLogicANDEntity": ("&", "#3d7cc9", "#1f4f8f"), "CLogicOREntity": ("≥1", "#3d7cc9", "#1f4f8f"),
       "CLogicNOTEntity": ("1", "#3d7cc9", "#1f4f8f"), "CRSEntity": ("RS", "#7a5cc4", "#4b3590"),
       "CLogicXOREntity": ("=1", "#3d7cc9", "#1f4f8f"), "CTimeOnDelayEntity": ("T", "#d08a1f", "#8a5a10"),
       "CInputEntity": ("DI", "#1fae4f", "#0b7a32"), "COutputEntity": ("DO", "#1fae4f", "#0b7a32")}

objs, _ = parse((HERE / "transporter.xlg").read_bytes())
S = 1 / 40                                     # пиксели Studio -> единицы рисунка


def P(x, y):
    return x * S, -y * S


fig = plt.figure(figsize=(26, 15), dpi=100)
ax = fig.add_axes([0, 0.3, 1, 0.7])
ax.set_xlim(-3.6, 31.5)
ax.set_ylim(-11.2, 1.4)
ax.axis("off")
ax.add_patch(Rectangle((-3.6, -11.2), 35.1, 11.6, color="#e6e6e6", zorder=0))
for gx in range(-7, 63):
    for gy in range(-22, 1):
        ax.plot(gx / 2, gy / 2, ".", color="#a0a0a0", markersize=1.2, zorder=1)
ax.text(14, 0.9, "Программа реле A1 в ONI PLR Studio (FBD): реверсивный транспортёр",
        ha="center", va="center", fontsize=24, fontweight="bold")

base = {"I": 100, "Q": 12000, "B": 100000}
for o in objs:
    if o["kind"] not in SYM:
        continue
    x1, x2, y1, y2 = o["rect"]
    (ax0, ay1), (ax1, ay0) = P(x1, y1), P(x2, y2)
    sym, fc, ec = SYM[o["kind"]]
    ax.add_patch(FancyBboxPatch((ax0, ay0), ax1 - ax0, ay1 - ay0, boxstyle="round,pad=0.02",
                                fc=fc, ec=ec, lw=2, zorder=3))
    ax.text((ax0 + ax1) / 2, (ay0 + ay1) / 2, sym, ha="center", va="center", color="white",
            fontsize=13, fontweight="bold", zorder=4)
    pref = {"CInputEntity": "I", "COutputEntity": "Q"}.get(o["kind"], "B")
    name = "%s%d" % (pref, o["id"] - base[pref] + 1) if pref != "B" else \
        "B%03d" % (o["id"] - base["B"] + 1)
    ax.text((ax0 + ax1) / 2, ay1 + 0.1, name, ha="center", va="bottom", fontsize=12,
            fontweight="bold", zorder=4)
    if pref == "I":
        ax.text(ax0 - 0.15, (ay0 + ay1) / 2, IO[o["id"]], ha="right", va="center", fontsize=11)
    elif pref == "Q":
        ax.text(ax1 + 0.15, (ay0 + ay1) / 2, IO[o["id"]], ha="left", va="center", fontsize=11)
    else:
        ax.text((ax0 + ax1) / 2, ay0 - 0.08, NOTES[o["id"]], ha="center", va="top", fontsize=9,
                color="#333333", zorder=4)
        if o["kind"] == "CRSEntity":
            for py, t in ((y1 + 8, "S"), (y1 + 32, "R")):
                ax.text(ax0 + 0.05, P(0, py)[1], t, color="white", fontsize=8, va="center")
for o in objs:
    if o["kind"] != "CLineEntity":
        continue
    xs, ys = zip(*(P(x, y) for x, y in o["pts"]))
    ax.plot(xs, ys, color="#111111", lw=1.8, zorder=2)
    for jx, jy in o["joints"]:
        ax.plot(*P(jx, jy), "o", color="#111111", markersize=6, zorder=5)

tx = fig.add_axes([0, 0, 1, 0.3])
tx.axis("off")
tx.text(0.02, 0.95, "Что с чем соединить", fontsize=17, fontweight="bold", va="top")
links = [
    "B001 «ИЛИ»: I3, B004  → сброс хода вперёд (конец или идёт назад)",
    "B002 «RS»: S ← I1, R ← B001  → M1 «вперёд»",
    "B003 «ИЛИ»: I4, B002  → сброс хода назад (начало или идёт вперёд)",
    "B004 «RS»: S ← I2, R ← B003  → M2 «назад»",
    "B005 «Задержка включения» 3 с: B002 → Q2 (KM1);   B006 то же: B004 → Q3 (KM2)",
    "B007 «ИЛИ»: B002, B004;   B008 «ИЛИ»: B005, B006",
    "B009 «Исключающее ИЛИ»: B007, B008  → Q1 (звонок, пока ход есть, а мотор ещё не включён)",
]
for k, t in enumerate(links):
    tx.text(0.02, 0.83 - k * 0.095, t, fontsize=13, va="top")
tx.text(0.6, 0.95, "Как работает", fontsize=17, fontweight="bold", va="top")
tx.text(0.6, 0.83,
        "ПУСК → 3 с звенит HA, затем KM1 гонит вперёд до SQ1.\n"
        "НАЗАД → 3 с звенит HA, затем KM2 гонит назад до SQ2.\n"
        "Пока идёт один ход, кнопка другого не действует.\n"
        "В конечном положении пуск в ту же сторону невозможен.",
        fontsize=13, va="top", linespacing=1.6)
tx.text(0.6, 0.38, "Та же логика, что в LD на листе:", fontsize=13, fontweight="bold", va="top")
tx.text(0.6, 0.29, "M1 = (I1 + M1) · ¬I3 · ¬M2     M2 = (I2 + M2) · ¬I4 · ¬M1\n"
        "Q2 = T1 = M1 через 3 с         Q3 = T2 = M2 через 3 с\n"
        "Q1 = M1·¬T1 + M2·¬T2  =  (M1 + M2) ⊕ (T1 + T2)",
        fontsize=13, va="top", family="DejaVu Sans Mono", linespacing=1.6)

fig.savefig(HERE / "program.png", facecolor="white")
print(HERE / "program.png")
