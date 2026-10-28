"""r/dataisbeautiful collage: reddit/ring_the_changes.png (2400 x 3000), light warm stone and bell bronze.
Every number comes from ../data/results.json and ../data/rings.csv. Fonts: FONT_DIR holding static FrauncesVar.ttf (Fraunces Black),
SourceSerif4-Regular.ttf, IBMPlexMono-Regular.ttf, IBMPlexMono-Medium.ttf.
Run from this folder: FONT_DIR=/path/to/fonts python3 collage.py
"""
import json, math, os
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
FD = os.environ.get("FONT_DIR", "/tmp/claude-0/-home-claude/c232619d-81e0-53f3-9de6-41e973630753/scratchpad/rtc/fonts")
for f in ["FrauncesVar.ttf", "IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf", "SourceSerif4-Regular.ttf"]:
    fm.fontManager.addfont(os.path.join(FD, f))
DISP = fm.FontProperties(fname=os.path.join(FD, "FrauncesVar.ttf"))
SERP = fm.FontProperties(fname=os.path.join(FD, "SourceSerif4-Regular.ttf"))
MONO = "IBM Plex Mono"
BG, FG, MUT, LAND, EDGE, RULE = "#F4EDE0", "#231C14", "#6B6052", "#E8DDC9", "#CDBFA6", "#DCD0BC"
BRZ, DEEP = "#9A5B1E", "#4E240C"
S = ["#E2C796", "#D3A562", "#B5772F", "#86471A", "#4E240C"]
FAMC = {"Whitechapel": "#3E62A8", "Taylor": "#A85A1C", "Rudhall": "#1F9077", "Warner": "#C79A1E", "Gillett & Johnston": "#9150A0",
        "West Country": "#D7735A", "Other founders": "#DCD1BE", "Unknown": "#A79E8F"}
R = json.load(open(os.path.join(ROOT, "data", "results.json")))
RG = pd.read_csv(os.path.join(ROOT, "data", "rings.csv"))
COAST = json.load(open(os.path.join(ROOT, "data", "coast_ne10m.json")))
K = math.cos(math.radians(53.0))
c = R["counts"]

fig = plt.figure(figsize=(12, 15), dpi=200, facecolor=BG)
fig.text(0.045, 0.972, "Ring the changes", fontproperties=DISP, fontsize=60, color=FG, va="top")
fig.text(0.045, 0.905, "Where England's church bells hang, and the years they were cast", fontproperties=SERP, fontsize=22, color=BRZ, va="top")
fig.text(0.045, 0.869, f"Dove's Guide lists {c['rings']:,} rings of bells hung for full-circle change ringing, holding {c['bells']:,} bells. Each dot is one ring;\n"
         f"bigger and darker dots have more bells. The dates on the bells record jubilees, coronations and two world wars.",
         fontproperties=SERP, fontsize=13.5, color=FG, va="top", linespacing=1.45)

# hero map
ax = fig.add_axes([0.0, 0.425, 0.60, 0.395])
for g in COAST:
    for poly in (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]):
        a = np.array(poly[0]); ax.add_patch(Polygon(np.c_[a[:, 0] * K, a[:, 1]], closed=True, fc=LAND, ec=EDGE, lw=.6, zorder=0))
d = RG[RG.lat.between(49.8, 56.2) & RG.lon.between(-10.6, 2)].copy()
d["c"] = d.bells.map(lambda b: 0 if b <= 5 else 1 if b == 6 else 2 if b == 8 else 3 if b == 10 else 4)
for k in range(5):
    q = d[d.c == k]
    ax.scatter(q.lon * K, q.lat, s=2.5 + k * 4.5, c=S[k], lw=0, alpha=.92, zorder=2 + k, rasterized=True)
ax.set_xlim(-5.9 * K, 1.85 * K); ax.set_ylim(49.9, 55.9); ax.set_aspect("equal"); ax.axis("off")
for i, (t, k) in enumerate([("3 to 5 bells", 0), ("6 bells", 1), ("8 bells", 2), ("10 bells", 3), ("12 or more", 4)]):
    y = 55.6 - i * 0.27
    ax.scatter([-5.65 * K], [y], s=14 + k * 14, c=S[k], lw=0); ax.text(-5.47 * K, y, t, va="center", fontsize=11, family=MONO, color=FG)

# headline numbers
tx = fig.add_axes([0.6, 0.415, 0.38, 0.40]); tx.axis("off"); tx.set_xlim(0, 1); tx.set_ylim(0, 1)
cy = R["cast_years"]["top"]
notes = [(f"{round(c['england_share'] * 100)}%", BRZ, f"of the rings are in England.\nWales has {c['wales']}, Scotland just {c['scotland']}."),
         (str(R["oldest_dated_first"]["year"]), DEEP, f"the oldest dated bell still rung,\nthe fourth of six at Cold Ashby,\nNorthamptonshire."),
         (f"{cy[0]['n']}", BRZ, f"bells now in rings were cast in\n1897, Victoria's Diamond Jubilee:\nabout twice the years around it."),
         ("0", DEEP, f"bells now in rings were cast in\n1943 or 1944, when the bells fell\nsilent for the Second World War.")]
for i, (big, col, txt) in enumerate(notes):
    y = 1.0 - i * 0.262
    tx.text(0.02, y, big, fontproperties=DISP, fontsize=42, color=col, va="top")
    tx.text(0.02, y - 0.115, txt, family=MONO, fontsize=11.5, color=FG, va="top", linespacing=1.4)

# years chart
ay = fig.add_axes([0.07, 0.25, 0.89, 0.135]); ay.set_facecolor(BG)
C = R["cast_years"]; y0 = 1800; v = np.array(C["n"][y0 - C["start"]:]); yrs = np.arange(y0, y0 + len(v))
ev = {e["year"]: e for e in R["events"]}
for a, b in [(1914.5, 1918.5), (1939.5, 1945.5)]: ay.axvspan(a, b, color="#E6DCCB", lw=0, zorder=0)
ay.bar(yrs, v, width=.82, color=[(BRZ if y in ev else "#D6AE73") for y in yrs], lw=0, zorder=2)
for y in [1887, 1897, 1902, 1911, 1937, 2000]:
    ay.text(y, ev[y]["n"] + 10, str(y), ha="center", fontsize=10.5, family=MONO, color=FG, weight="medium")
ay.text(1916.5, 300, "1914 to 1918", rotation=90, ha="center", va="center", fontsize=9.5, family=MONO, color=MUT)
ay.text(1942.5, 300, "1939 to 1945", rotation=90, ha="center", va="center", fontsize=9.5, family=MONO, color=MUT)
for s in ("top", "right"): ay.spines[s].set_visible(False)
ay.spines["left"].set_color(EDGE); ay.spines["bottom"].set_color(EDGE)
ay.tick_params(colors=FG, labelsize=10.5); ay.set_xlim(1799, 2026); ay.set_ylim(0, 480)
ay.yaxis.grid(True, color=RULE, lw=.6); ay.set_axisbelow(True)
fig.text(0.045, 0.405, "Bells in rings today, by the year they were cast", fontproperties=SERP, fontsize=17, color=FG)
fig.text(0.045, 0.392, "Darker: jubilee, coronation and Millennium years. Shaded: the world wars.", family=MONO, fontsize=10.5, color=MUT)

# small multiples: founders and ring sizes
fig.text(0.045, 0.207, "Who cast them", fontproperties=SERP, fontsize=17, color=FG)
fig.text(0.045, 0.193, f"Bells by 25 years of casting. Whitechapel and Taylor: {round(R['founders']['big2_share'] * 100)}% of all.", family=MONO, fontsize=10, color=MUT)
af = fig.add_axes([0.07, 0.108, 0.42, 0.078]); af.set_facecolor(BG)
F = R["founders_period"]; bins = np.array(F["bins"]); acc = np.zeros(len(bins))
for f in F["fams"]:
    vv = np.array(F["n"][f]); af.bar(bins + 12.5, vv, bottom=acc, width=22, color=FAMC[f], lw=0); acc += vv
af.set_xlim(1300, 2030); af.set_yticks([]); af.set_xticks([1400, 1600, 1800, 2000])
for s in ("top", "right", "left"): af.spines[s].set_visible(False)
af.spines["bottom"].set_color(EDGE); af.tick_params(colors=FG, labelsize=10)
for i, (f, lab) in enumerate([("Whitechapel", "Whitechapel"), ("Taylor", "Taylor"), ("Rudhall", "Rudhall"), ("Other founders", "others")]):
    yy = acc.max() * (0.95 - i * 0.22)
    af.add_patch(matplotlib.patches.Rectangle((1310, yy - acc.max() * 0.11), 22, acc.max() * 0.1, color=FAMC[f], lw=0))
    af.text(1345, yy, lab, color=FG, fontsize=10, family=MONO, va="top")

fig.text(0.54, 0.207, "How many bells", fontproperties=SERP, fontsize=17, color=FG)
fig.text(0.54, 0.193, f"Rings by size. {R['unringable']['n']:,} ({round(R['unringable']['share'] * 100)}%) are unringable (hatched).", family=MONO, fontsize=10, color=MUT)
asz = fig.add_axes([0.56, 0.108, 0.40, 0.078]); asz.set_facecolor(BG)
sz = [s for s in R["sizes"] if s["bells"] <= 12]
xs = np.arange(len(sz)); okv = [s["n"] - s["unringable"] for s in sz]; urv = [s["unringable"] for s in sz]
cols = [S[0 if s["bells"] <= 5 else 1 if s["bells"] == 6 else 2 if s["bells"] == 8 else 3 if s["bells"] == 10 else 4] for s in sz]
asz.bar(xs, okv, color=cols, width=.72, lw=0); asz.bar(xs, urv, bottom=okv, color=cols, alpha=.4, hatch="///", edgecolor="#8C8172", width=.72, lw=0)
for i, s in enumerate(sz): asz.text(i, s["n"] + 60, f"{s['n']:,}", ha="center", fontsize=9.5, family=MONO, color=FG)
asz.set_xticks(xs); asz.set_xticklabels([str(s["bells"]) for s in sz]); asz.set_yticks([]); asz.set_ylim(0, 3500)
for s in ("top", "right", "left"): asz.spines[s].set_visible(False)
asz.spines["bottom"].set_color(EDGE); asz.tick_params(colors=FG, labelsize=10.5)

# footer
fig.add_artist(plt.Line2D([0.045, 0.955], [0.078, 0.078], color=FG, lw=1.2))
fig.text(0.045, 0.070, "Source: Dove's Guide for Church Bell Ringers, Central Council of Church Bell Ringers, dove.cccbr.org.uk,\n"
         f"CC BY-SA 4.0 (changes made: cast dates parsed, rings summarised; not endorsed by the CCCBR), retrieved {c['retrieved_text']}.\n"
         "Year chart: dated bells only. These are the bells that survive in rings today, not all bells ever cast.\n"
         "Coastline: Natural Earth. Analysis and chart: Tristan Hotham, with Python and matplotlib.",
         family=MONO, fontsize=9.2, color=MUT, va="top", linespacing=1.45)
fig.savefig(os.path.join(HERE, "ring_the_changes.png"), dpi=200, facecolor=BG)
print("written")
