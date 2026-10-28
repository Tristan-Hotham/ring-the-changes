"""Step 6. Static figures for the paper (release/paper/f_*.png) and the blog (release/blog/b_*.png, 1520 px wide).
Every number comes from data/results.json and the data files. Fonts: FONT_DIR holding static instances
FrauncesVar.ttf (Fraunces Black), SourceSerif4-Regular.ttf, IBMPlexMono-Regular.ttf, IBMPlexMono-Medium.ttf.
Run: FONT_DIR=/path/to/fonts python3 code/06_figures.py
"""
import json, math, os
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
FD = os.environ.get("FONT_DIR", "/tmp/claude-0/-home-claude/c232619d-81e0-53f3-9de6-41e973630753/scratchpad/rtc/fonts")
for f in ["IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf", "SourceSerif4-Regular.ttf"]:
    if os.path.exists(os.path.join(FD, f)): fm.fontManager.addfont(os.path.join(FD, f))
MONO = "IBM Plex Mono"
plt.rcParams.update({"font.family": MONO, "font.size": 10, "axes.edgecolor": "#8C8172", "axes.labelcolor": "#231C14", "xtick.color": "#4A4238",
                     "ytick.color": "#4A4238", "axes.spines.top": False, "axes.spines.right": False, "axes.grid": False})
BG, FG, MUT, RULE, LAND, EDGE = "#FBF8F2", "#231C14", "#6B6052", "#DCD2C1", "#ECE4D4", "#CBBDA6"
S = ["#E6D3AE", "#D3A562", "#B5772F", "#86471A", "#4E240C"]
FAMC = {"Whitechapel": "#3E62A8", "Taylor": "#A85A1C", "Rudhall": "#1F9077", "Warner": "#C79A1E", "Gillett & Johnston": "#9150A0",
        "West Country": "#D7735A", "Other founders": "#DCD1BE", "Unknown": "#A79E8F"}
R = json.load(open(os.path.join(ROOT, "data", "results.json")))
RG = pd.read_csv(os.path.join(ROOT, "data", "rings.csv"))
COAST = json.load(open(os.path.join(ROOT, "data", "coast_ne10m.json")))
CS = json.load(open(os.path.join(ROOT, "work", "counties_simpl.json")))
K = math.cos(math.radians(53.5))
P_OUT = os.path.join(ROOT, "release", "paper"); B_OUT = os.path.join(ROOT, "release", "blog")
os.makedirs(P_OUT, exist_ok=True); os.makedirs(B_OUT, exist_ok=True)


def save(fig, name, blog):
    for ax in fig.axes:
        if ax.get_ylabel(): ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, p: f"{v:,.0f}"))
    if blog:
        fig.savefig(os.path.join(B_OUT, f"b_{name}.png"), dpi=200, facecolor=BG)
    else:
        fig.savefig(os.path.join(P_OUT, f"f_{name}.png"), dpi=220, facecolor="white")
    plt.close(fig)


def land(ax, fc=LAND, ec=EDGE):
    for g in COAST:
        for poly in (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]):
            a = np.array(poly[0]); ax.add_patch(Polygon(np.c_[a[:, 0] * K, a[:, 1]], closed=True, fc=fc, ec=ec, lw=.5, zorder=0))


def size_class(b):
    return 0 if b <= 5 else 1 if b == 6 else 2 if b == 8 else 3 if b == 10 else 4


def fig_map(blog):
    w = 7.6 if blog else 6.6
    fig = plt.figure(figsize=(w, w * 1.18), facecolor=BG if blog else "white")
    ax = fig.add_axes([0, 0, 1, 1]); land(ax)
    d = RG[RG.lat.between(49.8, 56.2) & RG.lon.between(-10.6, 2)].copy(); d["c"] = d.bells.map(size_class)
    for c in range(5):
        q = d[d.c == c]
        ax.scatter(q.lon * K, q.lat, s=1.6 + c * 2.4, c=S[c], lw=0, alpha=.9, zorder=2 + c, rasterized=True)
    ur = d[d.unringable]
    ax.set_xlim(-6.3 * K, 1.9 * K); ax.set_ylim(49.85, 56.35); ax.set_aspect("equal"); ax.axis("off")
    labs = [("3 to 5 bells", 0), ("6", 1), ("8", 2), ("10", 3), ("12 or more", 4)]
    for i, (t, c) in enumerate(labs):
        y = 55.75 - i * 0.24
        ax.scatter([-6.0 * K], [y], s=10 + c * 10, c=S[c], lw=0); ax.text(-5.85 * K, y, t, va="center", fontsize=10.5 if blog else 9, color=FG)
    ax.text(-6.05 * K, 56.08, f"{R['site']['points']:,} rings of bells", fontsize=12 if blog else 10, color=FG, weight="medium")
    save(fig, "map", blog)


def fig_years(blog):
    C = R["cast_years"]; y0 = 1800; v = np.array(C["n"][y0 - C["start"]:]); yrs = np.arange(y0, y0 + len(v))
    fig, ax = plt.subplots(figsize=(7.6, 3.9) if blog else (6.6, 3.2), facecolor=BG if blog else "white")
    ax.set_facecolor(BG if blog else "white")
    for a, b in [(1914.5, 1918.5), (1939.5, 1945.5)]: ax.axvspan(a, b, color="#E9E2D4", lw=0, zorder=0)
    ev = {e["year"]: e for e in R["events"]}
    ax.bar(yrs, v, width=.85, color=[("#9A5B1E" if y in ev else "#D3A562") for y in yrs], lw=0, zorder=2)
    for y in [1887, 1897, 1902, 1911, 1937, 1953, 2000]:
        ax.text(y, ev[y]["n"] + 8, str(y), ha="center", fontsize=9 if blog else 7.5, color=FG, weight="medium")
    ax.text(1916.5, max(v) * 0.42, "1914 to 1918", ha="center", va="center", rotation=90, fontsize=8.5 if blog else 7, color=MUT)
    ax.text(1942.5, max(v) * 0.42, "1939 to 1945", ha="center", va="center", rotation=90, fontsize=8.5 if blog else 7, color=MUT)
    ax.set_xlim(1799, 2026); ax.set_ylim(0, max(v) * 1.1); ax.set_ylabel("bells cast in that year")
    ax.yaxis.grid(True, color=RULE, lw=.6); ax.set_axisbelow(True)
    fig.tight_layout(); save(fig, "years", blog)


def fig_founders(blog):
    F = R["founders_period"]; bins = np.array(F["bins"])
    fig, ax = plt.subplots(figsize=(7.6, 4.2) if blog else (6.6, 3.6), facecolor=BG if blog else "white")
    ax.set_facecolor(BG if blog else "white")
    acc = np.zeros(len(bins))
    for f in F["fams"]:
        v = np.array(F["n"][f]); ax.bar(bins + 12.5, v, bottom=acc, width=23, color=FAMC[f], label=f, lw=0); acc += v
    ax.set_xlim(1295, 2030); ax.set_ylabel("bells in rings today"); ax.yaxis.grid(True, color=RULE, lw=.6); ax.set_axisbelow(True)
    ax.set_xticks(range(1300, 2001, 100))
    ax.legend(loc="upper left", frameon=False, fontsize=9 if blog else 7.5, ncol=2)
    fig.tight_layout(); save(fig, "founders", blog)


def fig_share(blog):
    sh = {c["county"]: c["share"] for c in R["counties"] if c["share"] is not None and c["churches"] >= 100 and c["nation"] != "Scotland"}
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("b", ["#F1E6D2", "#D3A562", "#9A5B1E", "#4E240C"])
    w = 7.6 if blog else 6.6
    fig = plt.figure(figsize=(w, w * 1.1), facecolor=BG if blog else "white"); ax = fig.add_axes([0, 0, 1, 1])
    land(ax, fc="#F3EFE8", ec="#D9D0C0")
    for f in CS["features"]:
        nm = f["properties"]["county"]
        if f["properties"]["nation"] == "Scotland": continue
        g = f["geometry"]; polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        col = cmap(sh[nm] / 0.75) if nm in sh else "#E3DED5"
        for poly in polys:
            a = np.array(poly[0]); ax.add_patch(Polygon(np.c_[a[:, 0] * K, a[:, 1]], closed=True, fc=col, ec="white", lw=.5, zorder=1))
    ax.set_xlim(-5.9 * K, 1.9 * K); ax.set_ylim(49.9, 55.9); ax.set_aspect("equal"); ax.axis("off")
    cax = fig.add_axes([0.07, 0.83, 0.32, 0.022])
    cb = fig.colorbar(matplotlib.cm.ScalarMappable(norm=matplotlib.colors.Normalize(0, .75), cmap=cmap), cax=cax, orientation="horizontal")
    cb.set_ticks([0, .25, .5, .75]); cb.set_ticklabels(["0%", "25%", "50%", "75%"]); cb.outline.set_visible(False)
    fig.text(0.07, 0.775, "grey: fewer than 100 mapped\nAnglican churches", fontsize=9 if blog else 7.5, color=MUT, va="top")
    cax.set_title("Anglican churches with a ring", fontsize=10 if blog else 8.5, loc="left", color=FG)
    save(fig, "share", blog)


def fig_sizes(blog):
    sz = [s for s in R["sizes"] if s["bells"] <= 12]
    fig, ax = plt.subplots(figsize=(7.6, 3.4) if blog else (6.6, 2.9), facecolor=BG if blog else "white"); ax.set_facecolor(BG if blog else "white")
    x = np.arange(len(sz)); ok = [s["n"] - s["unringable"] for s in sz]; ur = [s["unringable"] for s in sz]
    cols = [S[size_class(s["bells"])] for s in sz]
    ax.bar(x, ok, color=cols, width=.7, lw=0, label="ringable"); ax.bar(x, ur, bottom=ok, color=cols, alpha=.35, width=.7, lw=0, hatch="///", edgecolor="#8C8172", label="unringable")
    for i, s in enumerate(sz): ax.text(i, s["n"] + 40, f"{s['n']:,}", ha="center", fontsize=9, color=FG)
    ax.set_xticks(x); ax.set_xticklabels([f"{s['bells']}" for s in sz]); ax.set_xlabel("bells in the ring"); ax.set_ylabel("rings")
    ax.set_ylim(0, 3300); ax.legend(frameon=False, fontsize=9); ax.yaxis.grid(True, color=RULE, lw=.6); ax.set_axisbelow(True)
    fig.tight_layout(); save(fig, "sizes", blog)


def fig_growth(blog):
    G = R["growth"]; yrs = np.array(G["years"])
    fig, ax = plt.subplots(figsize=(7.6, 3.6) if blog else (6.6, 3.0), facecolor=BG if blog else "white"); ax.set_facecolor(BG if blog else "white")
    for s, c, ls in [(8, S[2], "-"), (10, S[3], "--"), (12, S[4], "-.")]:
        g = R["growth_by"][str(s)]; ax.plot(yrs, g["cum"], color=c, lw=2.2, ls=ls)
        ax.text(2028, g["cum"][-1], f"{s} bells: {g['cum'][-1]:,}", va="center", fontsize=9, color=FG)
    ax.set_xlim(1700, 2060); ax.set_ylabel("present rings complete"); ax.yaxis.grid(True, color=RULE, lw=.6); ax.set_axisbelow(True)
    ax.set_xticks(range(1700, 2026, 50)); fig.tight_layout(); save(fig, "growth", blog)


def fig_frames(blog):
    F = R["frames"]; bins = np.array(F["bins"])
    fig, ax = plt.subplots(figsize=(7.6, 3.4) if blog else (6.6, 2.8), facecolor=BG if blog else "white"); ax.set_facecolor(BG if blog else "white")
    acc = np.zeros(len(bins))
    for k, c, h in [("timber", "#B5772F", None), ("cast iron", "#231C14", None), ("steel", "#3E62A8", "..")]:
        v = np.array(F["n_by"][k]); ax.bar(bins + 12.5, v, bottom=acc, width=22, color=c, label=k, lw=0, hatch=h, edgecolor="white" if h else None); acc += v
    ax.legend(frameon=False, fontsize=9, loc="upper left"); ax.set_ylabel("frames"); ax.yaxis.grid(True, color=RULE, lw=.6); ax.set_axisbelow(True)
    fig.tight_layout(); save(fig, "frames", blog)


if __name__ == "__main__":
    for blog in (False, True):
        fig_map(blog); fig_years(blog); fig_founders(blog); fig_share(blog); fig_sizes(blog); fig_growth(blog)
    fig_frames(False)
    print("figures written")
