"""Рисует программу ВЭП-600 прямо из vep600.xlg (блоки и линии берутся из файла проекта).

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
    100: "SA «Авто»", 101: "SA «Ручн.»", 102: "SK1 t° бака\n(регулир.)",
    103: "SK2 t° обратки\n(насос)", 104: "SK3 перегрев\n(НЗ, 95 °C)", 105: "SL вода есть",
    106: "KK насоса (НЗ)",
    12000: "KM1 нагрев", 12001: "KM2 насос", 12002: "HL1 «Нагрев»", 12003: "HL2 «Авария»",
}
NOTES = {
    100000: "режим вкл. (M2)", 100001: "перегрев", 100002: "перегрузка",
    100003: "авария", 100004: "SA в «0»", 100005: "M1 авария", 100006: "нет воды",
    100007: "нет аварии", 100008: "авто: t бака", 100009: "", 100010: "нагрев",
    100011: "авто: t обратки", 100012: "", 100013: "насос", 100014: "нет воды в работе",
    100015: "лампа «Авария»",
}
SYM = {"CLogicANDEntity": ("&", "#3d7cc9", "#1f4f8f"), "CLogicOREntity": ("≥1", "#3d7cc9", "#1f4f8f"),
       "CLogicNOTEntity": ("1", "#3d7cc9", "#1f4f8f"), "CRSEntity": ("RS", "#7a5cc4", "#4b3590"),
       "CInputEntity": ("DI", "#1fae4f", "#0b7a32"), "COutputEntity": ("DO", "#1fae4f", "#0b7a32")}

objs, _ = parse((HERE / "vep600.xlg").read_bytes())
S = 1 / 40                                     # пиксели Studio -> единицы рисунка


def P(x, y):
    return x * S, -y * S


fig = plt.figure(figsize=(26, 19), dpi=100)
ax = fig.add_axes([0, 0.27, 1, 0.73])
ax.set_xlim(-3.6, 31.5)
ax.set_ylim(-15.6, 1.4)
ax.axis("off")
ax.add_patch(Rectangle((-3.6, -15.6), 35.1, 16.0, color="#e6e6e6", zorder=0))
for gx in range(-7, 63):
    for gy in range(-31, 1):
        ax.plot(gx / 2, gy / 2, ".", color="#a0a0a0", markersize=1.2, zorder=1)
ax.text(14, 0.9, "Программа реле A1 в ONI PLR Studio (FBD): ВЭП-600 с защитами",
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

tx = fig.add_axes([0, 0, 1, 0.27])
tx.axis("off")
tx.text(0.02, 0.95, "Что с чем соединить", fontsize=17, fontweight="bold", va="top")
links = [
    "B001 «ИЛИ»: I1, I2  → режим включён (M2)",
    "B002 «НЕ»: I5;   B003 «НЕ»: I7;   B004 «ИЛИ»: B002, B003  → авария",
    "B005 «НЕ»: B001  → SA в «0»",
    "B006 «RS»: S ← B004, R ← B005  → M1 «Авария» (защёлка до SA в «0»)",
    "B007 «НЕ»: I6 (нет воды);   B008 «НЕ»: B006 (нет аварии)",
    "B009 «И»: I1, I3;   B010 «ИЛИ»: B009, I2;   B011 «И»: B010, I6, B008  → Q1, Q3",
    "B012 «И»: I1, I4;   B013 «ИЛИ»: B012, I2;   B014 «И»: B013, I6, B008  → Q2",
    "B015 «И»: B001, B007;   B016 «ИЛИ»: B006, B015  → Q4",
]
for k, t in enumerate(links):
    tx.text(0.02, 0.83 - k * 0.095, t, fontsize=13, va="top")
tx.text(0.6, 0.95, "Как работает", fontsize=17, fontweight="bold", va="top")
tx.text(0.6, 0.83,
        "SA «Авто»: нагрев по SK1, насос по SK2.  SA «Ручн.»: нагрев и насос включены.\n"
        "Нет воды (SL) → нагрев и насос стоят, горит HL2; вода появилась — работа сама.\n"
        "Перегрев SK3 или перегрузка KK → всё выкл., горит HL2; защёлка держится,\n"
        "пока SA не поставить в «0».  SK4 отключает KM1 в обход реле.",
        fontsize=13, va="top", linespacing=1.6)
tx.text(0.6, 0.38, "Та же логика, что в LD на листе:", fontsize=13, fontweight="bold", va="top")
tx.text(0.6, 0.29, "M2 = I1 + I2          M1 = (¬I5 + ¬I7 + M1) · M2\n"
        "Q1 = (I1·I3 + I2) · I6 · ¬M1     Q2 = (I1·I4 + I2) · I6 · ¬M1\n"
        "Q3 = Q1               Q4 = M1 + M2 · ¬I6",
        fontsize=13, va="top", family="DejaVu Sans Mono", linespacing=1.6)

fig.savefig(HERE / "program.png", facecolor="white")
print(HERE / "program.png")
