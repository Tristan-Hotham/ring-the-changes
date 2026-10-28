"""Step 8. Blog post (release/blog/post.html from blog_template.html), blog and Zenodo meta files,
and the Zenodo folder (paper, key CSVs, results.json and a code-and-data zip).
Image placeholders {{IMG|file|alt|caption}} are left for the uploader.
Run: python3 code/08_release.py
"""
import json, os, re, shutil, zipfile
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
spec = importlib.util.spec_from_file_location("b", os.path.join(HERE, "04_build_site.py")); b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
R = b.R
t = open(os.path.join(HERE, "blog_template.html")).read()
t = re.sub(r"\{\{(?!IMG\|)([^{}|]+)(\|(\w+))?\}\}", b.sub, t)
os.makedirs(os.path.join(ROOT, "release", "blog"), exist_ok=True)
open(os.path.join(ROOT, "release", "blog", "post.html"), "w").write(t)
for m in re.findall(r"\{\{IMG\|([^|]+)\|", t):
    assert os.path.exists(os.path.join(ROOT, "release", "blog", m)), m
vis = re.sub(r"<!--.*?-->", "", t, flags=re.S)
for bad in ("—", "–", "--"): assert bad not in vis, bad

c = R["counts"]
meta = dict(
    title="Ring the changes: where England's bells hang",
    slug="ring-the-changes",
    excerpt=(f"Dove's Guide lists {c['rings']:,} rings of church bells hung for change ringing, {round(c['england_share'] * 100)}% of them in England. "
             f"I mapped them all, and found Victoria's jubilees, two world wars and seven centuries of bell founding in the dates on the bells."),
    seo_description=f"Every ring of church bells in Dove's Guide mapped: {c['rings']:,} rings, the oldest bells, the great founders, and the jubilee and wartime years.",
    tags=["church bells", "change ringing", "bell ringing", "Dove's Guide", "churches", "maps", "data", "England"],
    header_alt=(f"Title card reading 'Ring the changes: where England's bells hang' on a warm stone background, beside a map of England and Wales "
                f"covered in bronze dots for rings of bells. Text: {c['rings']:,} rings and {c['bells']:,} bells hung for change ringing; "
                f"the oldest dated bell still rung was cast in {R['oldest_dated_first']['year']}."))
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
json.dump(meta, open(os.path.join(ROOT, "release", "blog", "meta.json"), "w"), indent=2, ensure_ascii=False)

NAME = "Hotham_Ring_the_Changes"
pt = open(os.path.join(ROOT, "release", "paper", NAME + ".tex")).read()
ab = pt.split("\\begin{center}\\textbf{Abstract}\\end{center}")[1].split("\\textbf{Keywords:}")[0].strip()
ab = ab.replace("\\%", "%").replace("\\&", "&")
Z = os.path.join(ROOT, "release", "zenodo"); os.makedirs(Z, exist_ok=True)
zmeta = dict(
    title="Ring the Changes: Where England's Bells Hang. A Data Study of Dove's Guide for Church Bell Ringers",
    description_html=(f"<p>{ab}</p><p>Bell data: Dove's Guide for Church Bell Ringers, Central Council of Church Bell Ringers, dove.cccbr.org.uk, "
                      "CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/). Changes were made: cleaning, parsed cast dates, summaries and counties. "
                      "This work is not endorsed by the Central Council. Churches: OpenStreetMap contributors (ODbL), counts only.</p>"
                      "<p>Interactive version: https://tristan-hotham.github.io/ring-the-changes/. Data and code: https://github.com/Tristan-Hotham/ring-the-changes. Blog post: to follow.</p>"),
    keywords=["church bells", "change ringing", "bell founding", "Dove's Guide", "bell frames", "parish churches", "jubilees", "Second World War", "England", "open data"],
    licence="cc-by-sa-4.0",
    related=[
        dict(identifier="https://github.com/Tristan-Hotham/ring-the-changes", relation="issupplementedby", resource_type="software"),
        dict(identifier="https://tristan-hotham.github.io/ring-the-changes/", relation="issupplementedby", resource_type="other"),
        dict(identifier="https://dove.cccbr.org.uk/downloads", relation="isderivedfrom", resource_type="dataset"),
        dict(identifier="https://www.openstreetmap.org", relation="isderivedfrom", resource_type="dataset"),
        dict(identifier="https://geoportal.statistics.gov.uk", relation="isderivedfrom", resource_type="dataset"),
        dict(identifier="https://www.ordnancesurvey.co.uk/products/os-open-names", relation="isderivedfrom", resource_type="dataset"),
    ])
json.dump(zmeta, open(os.path.join(Z, "meta.json"), "w"), indent=2, ensure_ascii=False)
shutil.copy(os.path.join(ROOT, "release", NAME + ".pdf"), Z)
KEEP = ["rings.csv", "bells.csv", "frames.csv", "counties.csv", "countries.csv", "ring_sizes.csv", "cast_years.csv", "founders_by_period.csv", "growth.csv", "results.json"]
for f in KEEP: shutil.copy(os.path.join(ROOT, "data", f), Z)
with zipfile.ZipFile(os.path.join(Z, "ring-the-changes_code_and_data.zip"), "w", zipfile.ZIP_DEFLATED) as zf:
    for sub in ("code", "data"):
        for f in sorted(os.listdir(os.path.join(ROOT, sub))):
            p = os.path.join(ROOT, sub, f)
            if os.path.isfile(p) and not f.endswith(".pyc"): zf.write(p, f"ring-the-changes/{sub}/{f}")
    for f in ("README.md", "LICENSE"): zf.write(os.path.join(ROOT, f), f"ring-the-changes/{f}")
for f in [os.path.join(ROOT, "release", "blog", "meta.json"), os.path.join(Z, "meta.json")]:
    s = open(f).read(); assert "—" not in s and "–" not in s and "--" not in s, f
print("release files written; post words:", len(re.sub(r"<[^>]+>", " ", re.sub(r"\{\{IMG\|.*?\}\}", "", t, flags=re.S)).split()))
