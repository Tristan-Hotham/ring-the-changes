"""Step 5. Render ../header.png (1200x630 social card) with Playwright Chromium.

Fonts: FONT_DIR holding Fraunces, Source Serif 4 and IBM Plex Mono (from github.com/google/fonts; the variable
Fraunces[SOFT,WONK,opsz,wght].ttf and SourceSerif4[opsz,wght].ttf work); otherwise system serif is used.
Coastline: data/coast_ne10m.json (Natural Earth 1:10m land, public domain).
Run: FONT_DIR=/path/to/fonts python3 code/05_header.py
"""
import json, math, os
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
S = json.load(open(os.path.join(ROOT, "work", "site_data.json")))
R = json.load(open(os.path.join(ROOT, "data", "results.json")))
FD = os.environ.get("FONT_DIR", "/root/.fonts")
K = math.cos(math.radians(52.5))
X0, X1, Y0, Y1 = -5.9 * K, 1.9 * K, -55.95, -49.85
Hh = 610; Ww = Hh * (X1 - X0) / (Y1 - Y0)
pr = lambda lat, lon: ((lon * K - X0) / (Y1 - Y0) * Hh, (-lat - Y0) / (Y1 - Y0) * Hh)
land = ""
for g in json.load(open(os.path.join(ROOT, "data", "coast_ne10m.json"))):
    for poly in (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]):
        ring = poly[0]
        if max(q[0] for q in ring) < -5.4 and min(q[1] for q in ring) < 55.4: continue
        land += "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in (pr(q[1], q[0]) for q in ring)) + "Z"
COL = {3: "#E2C796", 6: "#CF9A52", 8: "#A9662A", 10: "#7A3D16", 12: "#4A210B"}
c = S["cols"]; dots = ""
for r in sorted(S["rows"], key=lambda r: r[c.index("bells")]):
    la, lo, b = r[0], r[1], r[c.index("bells")]
    if not (49.8 < la < 56 and -6 < lo < 2): continue
    x, y = pr(la, lo); k = 3 if b <= 5 else 6 if b == 6 else 8 if b == 8 else 10 if b == 10 else 12
    dots += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{1.3 + (b - 3) * 0.17:.2f}" fill="{COL[k]}" fill-opacity=".85"/>'
fonts = [("Fraunces", "Fraunces%5BSOFT,WONK,opsz,wght%5D.ttf", "100 900"), ("Source Serif 4", "SourceSerif4%5Bopsz,wght%5D.ttf", "200 900"),
         ("IBM Plex Mono", "IBMPlexMono-Regular.ttf", "400"), ("IBM Plex Mono", "IBMPlexMono-Medium.ttf", "500")]
ff = "".join(f"@font-face{{font-family:'{n}';src:url('file://{FD}/{f}');font-weight:{w};}}" for n, f, w in fonts if os.path.exists(os.path.join(FD, f.replace('%5B', '[').replace('%5D', ']'))) or os.path.exists(os.path.join(FD, f)))
html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{ff}
body{{margin:0;width:1200px;height:630px;background:radial-gradient(circle at 78% 50%,#F8F4EC 0%,#F2ECE0 55%,#E5DBC8 100%);color:#231C14;overflow:hidden;position:relative;font-family:'Source Serif 4',Georgia,serif}}
.k{{position:absolute;left:66px;top:62px;font:500 15px/1 'IBM Plex Mono',monospace;letter-spacing:.14em;text-transform:uppercase;color:#6B6052;display:flex;gap:12px;align-items:center}}
.k b{{background:#9A5B1E;color:#F7F0E4;padding:7px 9px;font-weight:500}}
h1{{position:absolute;left:60px;top:100px;margin:0;font:900 104px/.88 Fraunces,Georgia,serif;letter-spacing:-.02em;width:640px}}
h1 em{{font-style:normal;color:#9A5B1E}}
h2{{position:absolute;left:64px;top:296px;margin:0;font:800 34px/1 Fraunces,Georgia,serif}}
p{{position:absolute;left:66px;top:358px;width:590px;margin:0;font-size:25px;line-height:1.36}}
p b{{color:#9A5B1E}}
.f{{position:absolute;left:66px;bottom:40px;font:400 14px/1 'IBM Plex Mono',monospace;letter-spacing:.12em;text-transform:uppercase;color:#6B6052}}
svg{{position:absolute;right:30px;top:10px}}
</style></head><body>
<div class="k"><b>Data study</b><span>Church bells · 1317 to 2026</span></div>
<h1>Ring the <em>changes</em></h1>
<h2>where England's bells hang</h2>
<p><b>{R['counts']['rings']:,}</b> rings and <b>{R['counts']['bells']:,}</b> bells hung for change ringing, {round(R['counts']['england_share'] * 100)}% of them in England. The oldest dated bell still rung was cast in <b>{R['oldest_dated_first']['year']}</b>.</p>
<div class="f">Dr Tristan Hotham · Independent researcher</div>
<svg width="{Ww:.0f}" height="{Hh}" viewBox="0 0 {Ww:.0f} {Hh}"><path d="{land}" fill="#E6DCC8" stroke="#CDBFA6" stroke-width="1"/>{dots}</svg>
</body></html>"""
os.makedirs(os.path.join(ROOT, "work"), exist_ok=True)
tmp = os.path.join(ROOT, "work", "header.html"); open(tmp, "w").write(html)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1200, "height": 630})
    pg.goto("file://" + os.path.abspath(tmp)); pg.wait_for_timeout(800)
    pg.screenshot(path=os.path.join(ROOT, "header.png")); b.close()
os.remove(tmp)
print("header.png written")
