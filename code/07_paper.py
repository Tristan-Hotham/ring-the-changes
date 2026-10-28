"""Step 7. Build the paper PDF: fill paper_template.tex with numbers and tables from data/results.json,
write release/paper/Hotham_Ring_the_Changes.tex and compile it with xelatex (figures from 06_figures.py).
Placeholders: {{path|fmt}} as in 04_build_site.py, with % escaped for LaTeX.
Run: python3 code/07_paper.py
"""
import json, os, re, shutil, subprocess

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
R = json.load(open(os.path.join(ROOT, "data", "results.json")))
OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_Ring_the_Changes"
WORDS = "zero one two three four five six seven eight nine ten eleven twelve".split()


def get(path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f):
    if f == "int": return f"{int(round(v)):,}"
    if f == "pct0": return f"{v * 100:.0f}\\%"
    if f == "pct1": return f"{v * 100:.1f}\\%"
    if f == "f1": return f"{v:.1f}"
    if f == "f2": return f"{v:.2f}"
    if f == "words": return WORDS[int(v)] if int(v) < len(WORDS) else f"{int(v):,}"
    return str(int(v)) if isinstance(v, float) and v.is_integer() else str(v)


def sub(m):
    path, _, f = m.group(1).partition("|")
    return fmt(get(path.strip()), f.strip() or "raw")


tex = lambda s: str(s).replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#")
rows = "".join(f"{s['bells']} & {s['n']:,} & {s['share'] * 100:.1f} & {s['unringable']:,} & {s['ur_share'] * 100:.0f} & {s['median_tenor']:,.0f}\\\\\n" for s in R["sizes"])
TS = ("\\begin{table}[tbp]\\centering\\small\\caption{Rings by number of bells. Unringable: marked u/r in Dove. Tenor: median weight of the heaviest bell, lb.}\\label{tab:sizes}"
      "\\begin{tabular}{rrrrrr}\\toprule Bells & Rings & \\% of rings & Unringable & \\% unringable & Median tenor (lb)\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
rows = "".join(f"{b['year']} & {tex(b['place'])} & {tex(b['county'] or b['country'])} & {tex(b['founder'])} & {tex(b['role'])} of {b['ring_bells']}\\\\\n" for b in R["oldest_dated"])
TO = ("\\begin{table}[tbp]\\centering\\small\\caption{The oldest bells in rings with a single cast year in Dove's Guide (one row per ring and year).}\\label{tab:oldest}"
      "\\begin{tabular}{rlllr}\\toprule Year & Tower & County & Founder (Dove) & Bell\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
rows = "".join(f"{e['year']} & {tex(e['label'])} & {e['n']:,} & {e['base']:.0f} & {e['ratio']:.2f}\\\\\n" for e in R["events"])
TE = ("\\begin{table}[tbp]\\centering\\small\\caption{Dated bells in rings cast in national commemoration years, against the mean of the three years either side.}\\label{tab:events}"
      "\\begin{tabular}{rlrrr}\\toprule Year & Occasion & Bells & Neighbours' mean & Ratio\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
s = open(os.path.join(HERE, "paper_template.tex")).read()
s = s.replace("{{TABLE_SIZES}}", TS).replace("{{TABLE_OLDEST}}", TO).replace("{{TABLE_EVENTS}}", TE)
s = re.sub(r"\{\{(.+?)\}\}", sub, s)
assert "{{" not in s and "--" not in s and "–" not in s and "—" not in s
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".tex"), "w").write(s)
for _ in range(2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
print(r.stdout[-400:])
for ext in (".aux", ".log", ".out"):
    p = os.path.join(OUT, NAME + ext)
    if os.path.exists(p): os.remove(p)
shutil.move(os.path.join(OUT, NAME + ".pdf"), os.path.join(ROOT, "release", NAME + ".pdf"))
