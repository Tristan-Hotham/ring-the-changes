"""Step 4. Build index.html from code/page_template.html.

Every number in the text is a {{path|format}} token filled from data/results.json, so the page cannot drift from the
analysis. The ring data for the map (work/site_data.json, from step 3) and a slim copy of the results are embedded;
the OS Open Names list for the place search (data/places_search.json) is fetched when first needed.
Run: python3 code/04_build_site.py
"""
import json, os, re, shutil

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
R = json.load(open(os.path.join(ROOT, "data", "results.json"), encoding="utf-8"))
WORDS = "zero one two three four five six seven eight nine ten eleven twelve".split()


def get(path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f):
    if f is None or f == "raw": return str(int(v)) if isinstance(v, float) and v.is_integer() else str(v)
    if f == "int": return f"{round(v):,}"
    if f == "pct": return f"{round(v * 100)}%"
    if f == "pct1": return f"{v * 100:.1f}%"
    if f == "f1": return f"{v:.1f}"
    if f == "f2": return f"{v:.2f}"
    if f == "words": return WORDS[int(v)] if int(v) < len(WORDS) else f"{int(v):,}"
    if f == "Words": w = fmt(v, "words"); return w[0].upper() + w[1:]
    raise ValueError(f)


def sub(m):
    return fmt(get(m.group(1)), m.group(3))


# facts the template states in words: check them against the data
assert [c["county"] for c in R["county_most"][:3]] == ["Devon", "Somerset", "Lincolnshire"]
assert [c["county"] for c in R["county_share_top"][:2]] == ["Northamptonshire", "Devon"]
assert R["county_density_bottom"][3]["county"] == "Northumberland"
assert R["geo"]["nn_max_place"] == "Hugh Town"
assert [c["county"] for c in R["ages"]["medieval_top_counties"][:4]] == ["Suffolk", "Norfolk", "Devon", "Somerset"]
assert sorted((x["place"], x["bells"]) for x in R["over12_list"]) == [("Birmingham", 16), ("Dublin", 16), ("Ossett", 15), ("Perth", 16), ("Winchester", 14)]
assert R["heaviest"][0]["place"] == "Liverpool" and R["oldest_dated_first"]["role"] == "4" and R["oldest_dated_first"]["ring_bells"] == 6
assert [e["year"] for e in R["cast_years"]["top"][:2]] == [1897, 1887]
assert R["wars"]["y1943"] == 0 and R["wars"]["y1944"] == 0
assert R["practice"]["top_day"] == "Tue" and R["decades"]["peak_decade"] == 1920
assert R["event"]["2002"]["ratio"] < 1 and R["saints"]["all_saints_rank"] == 4
assert R["abroad"]["oldest_usa"]["place"] == "Boston" and R["abroad"]["oldest_australia"]["place"] == "Perth"
assert R["founders"]["whitechapel_last"] == 2017

if __name__ == "__main__":
    tpl = open(os.path.join(HERE, "page_template.html"), encoding="utf-8").read()
    SITE = open(os.path.join(ROOT, "work", "site_data.json"), encoding="utf-8").read()
    html = re.sub(r"\{\{([^}|]+)(\|(\w+))?\}\}", sub, tpl)
    slim = {k: R[k] for k in ["sizes", "practice", "countries", "counties", "growth", "founders_period", "cast_years", "events", "frames", "heaviest", "oldest_dated"]}
    html = html.replace("/*SITE*/", SITE).replace("/*RESULTS*/", json.dumps(slim, ensure_ascii=False, separators=(",", ":")))
    assert "{{" not in html
    for bad in ("—", "–", "--"):
        assert bad not in SITE, bad
        vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", html, flags=re.S)
        assert bad not in vis, bad
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
    shutil.copy(os.path.join(ROOT, "work", "places_search.json"), os.path.join(ROOT, "data", "places_search.json"))
    print("index.html", len(html.encode()), "bytes")
