"""Step 3. Every statistic used on the page, in the paper, the blog post and the collage -> data/results.json.
Also writes data/cast_years.csv, data/founders_by_period.csv, data/countries.csv, data/ring_sizes.csv, data/growth.csv
and the compact map and search data for the page (work/site_data.json).
Run: python3 code/03_analyse.py
"""
import json, os
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
D = lambda f: os.path.join(ROOT, "data", f)
R = pd.read_csv(D("rings.csv"))
B = pd.read_csv(D("bells.csv"), low_memory=False)
FR = pd.read_csv(D("frames.csv"))
C = pd.read_csv(D("counties.csv"))
GEO = json.load(open(os.path.join(ROOT, "work", "geo.json")))
META = json.load(open(os.path.join(ROOT, "work", "meta.json")))
out = {}
r4 = lambda x: round(float(x), 4)

# ---------------- counts ----------------
eng = R.country.eq("England")
out["counts"] = dict(
    rings=len(R), full_circle=int(R.ring_type.eq("Full-circle ring").sum()), lightweight=int(R.ring_type.eq("Lightweight ring").sum()),
    towers=int(R.tower_id.nunique()), towers_two_rings=int((R.groupby("tower_id").size() > 1).sum()),
    bells=int(R.bells.sum()), bell_records=len(B), countries=int(R.country.nunique()),
    england=int(eng.sum()), england_share=r4(eng.mean()), wales=int(R.country.eq("Wales").sum()),
    scotland=int(R.country.eq("Scotland").sum()), ireland=int(R.country.eq("Ireland").sum()),
    england_wales_share=r4(R.country.isin(["England", "Wales"]).mean()),
    outside_british_isles=int((~R.country.isin(["England", "Wales", "Scotland", "Ireland", "Channel Islands", "Isle of Man"])).sum()),
    no_coords=int(R.lat.isna().sum()), retrieved=META["retrieved"][:10],
    retrieved_text=pd.Timestamp(META["retrieved"][:10]).strftime("%-d %B %Y"))
cty = R.groupby("country").agg(rings=("ring_id", "size"), bells=("bells", "sum"), oldest_bell=("oldest_year", "min"),
                               eights_plus=("bells", lambda s: int((s >= 8).sum()))).reset_index().sort_values("rings", ascending=False)
cty.to_csv(D("countries.csv"), index=False)
out["countries"] = [dict(country=r.country, rings=int(r.rings), bells=int(r.bells), oldest_bell=None if pd.isna(r.oldest_bell) else int(r.oldest_bell))
                    for r in cty.itertuples()]
out["by_country"] = {r["country"]: r for r in out["countries"]}

# ---------------- ring sizes ----------------
sz = R.groupby("bells").agg(n=("ring_id", "size"), unringable=("unringable", "sum"), median_tenor=("tenor_lbs", "median")).reset_index()
sz["share"] = sz.n / len(R); sz["ur_share"] = sz.unringable / sz.n
sz.to_csv(D("ring_sizes.csv"), index=False)
out["sizes"] = [dict(bells=int(r.bells), n=int(r.n), share=r4(r.share), unringable=int(r.unringable), ur_share=r4(r.ur_share),
                     median_tenor=float(r.median_tenor)) for r in sz.itertuples()]
S = {r["bells"]: r for r in out["sizes"]}
out["size"] = {str(k): v for k, v in S.items()}
out["size_groups"] = dict(six=S[6]["n"], six_share=S[6]["share"], eight=S[8]["n"], ten=S[10]["n"], twelve=S[12]["n"],
                          ten_plus=int((R.bells >= 10).sum()), eight_plus=int((R.bells >= 8).sum()), eight_plus_share=r4((R.bells >= 8).mean()),
                          over12=int((R.bells > 12).sum()), small=int((R.bells <= 5).sum()), small_share=r4((R.bells <= 5).mean()))
big = R[R.bells > 12].sort_values("bells", ascending=False)
out["over12_list"] = [dict(place=r.place, dedication=r.dedication, country=r.country, bells=int(r.bells), tenor_cwt=r.tenor_cwt) for r in big.itertuples()]
tw = R[R.bells == 12]
out["twelves"] = dict(n=len(tw), england=int(tw.country.eq("England").sum()), abroad=int((~tw.country.isin(["England", "Wales", "Scotland", "Ireland"])).sum()))

# ---------------- unringable, practice, extras ----------------
ur = R.unringable
out["unringable"] = dict(n=int(ur.sum()), share=r4(ur.mean()), small_n=int(ur[R.bells <= 5].sum()), small_share_of_ur=r4(ur[R.bells <= 5].sum() / ur.sum()),
                         three_share=S[3]["ur_share"], six_share=S[6]["ur_share"], eight_share=S[8]["ur_share"])
pdays = R.practice_day.fillna("")
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
ringable = ~ur
out["practice"] = dict(listed=int((pdays != "").sum()), listed_share_ringable=r4((pdays[ringable] != "").mean()),
                       days=[dict(day=d, n=int((pdays == d).sum())) for d in days])
out["practice"]["top_day"] = max(out["practice"]["days"], key=lambda x: x["n"])["day"]
out["practice"]["midweek_share"] = r4(pdays.isin(["Mon", "Tue", "Wed", "Thu"]).sum() / (pdays.isin(days)).sum())
out["extras"] = dict(ground_floor=int(R.ground_floor.sum()), ground_floor_share=r4(R.ground_floor.mean()), simulator=int(R.simulator.sum()),
                     grade1=int(R.listed_grade.eq("I").sum()), grade1_share_eng=r4(R[eng].listed_grade.eq("I").mean()),
                     grade2s=int(R.listed_grade.eq("II*").sum()), listed_share_eng=r4(R[eng].listed_grade.isin(["I", "II*", "II"]).mean()),
                     cracked_bells=int(B.cracked.eq("cracked").sum()), welded_bells=int(B.cracked.eq("welded").sum()))

# dedications (England), Dove's bare dedications grouped for St Mary
ded = R[eng].dedication.fillna("").str.replace(r"^(Cath Ch of |Priory Ch of |Abbey Ch of |Minster Ch of |former ch of )", "", regex=True)
mary = ded.str.match(r"^(S Mary|BVM|Blessed Virgin Mary)\b") & ~ded.str.contains("Magd")
out["dedications"] = dict(mary=int(mary.sum()), all_saints=int(ded.eq("All Saints").sum()), peter=int(ded.eq("S Peter").sum()),
                          mary_share=r4(mary.mean()))

SW = os.path.join(ROOT, "..", "saints-and-wells", "data", "results.json")
if os.path.exists(SW):
    sw = json.load(open(SW))["by_country"]["GB"]
    out["saints"] = dict(mary_share=r4(sw["share_mary"]), all_saints_rank=1 + [t["key"] for t in sw["top"]].index("All Saints"))

# ---------------- tenors ----------------
fc = R[R.ring_type == "Full-circle ring"]
hv = fc.sort_values("tenor_lbs", ascending=False).head(12)
def kg(l): return int(round(l * 0.45359237))
out["heaviest"] = [dict(place=r.place, dedication=r.dedication, country=r.country, bells=int(r.bells), tenor_cwt=r.tenor_cwt, tenor_lbs=int(r.tenor_lbs),
                        tenor_kg=kg(r.tenor_lbs), note=r.tenor_note, approx=bool(r.tenor_approx)) for r in hv.itertuples()]
out["tenor"] = dict(median_lbs=float(fc.tenor_lbs.median()), median_cwt=pd.Series([fc.tenor_lbs.median()]).map(lambda l: f"{int(l // 112)}").iloc[0],
                    median_kg=kg(fc.tenor_lbs.median()), over_ton=int((fc.tenor_lbs >= 2240).sum()), over_2ton=int((fc.tenor_lbs >= 4480).sum()),
                    under_5cwt=int((fc.tenor_lbs < 560).sum()), heaviest_kg=kg(hv.iloc[0].tenor_lbs),
                    lightweight_max_lbs=float(R[R.ring_type == "Lightweight ring"].tenor_lbs.max()))
out["tenor"]["by_size"] = {str(int(k)): float(v) for k, v in fc.groupby("bells").tenor_lbs.median().items()}
notes = fc.tenor_note.value_counts()
out["tenor"]["top_notes"] = [dict(note=k, n=int(v)) for k, v in notes.head(5).items()]

# ---------------- bell ages ----------------
yr = B.year
out["ages"] = dict(with_year=int(yr.notna().sum()), dated=int(B.year_kind.eq("dated").sum()), circa=int(B.year_kind.eq("circa").sum()),
                   median_year=int(yr.median()), before1500=int((yr < 1500).sum()), before1500_share=r4((yr < 1500).mean()),
                   before1600=int((yr < 1600).sum()), before1700=int((yr < 1700).sum()), before1800_share=r4((yr < 1800).mean()),
                   c19=int(((yr >= 1800) & (yr < 1900)).sum()), c20=int(((yr >= 1900) & (yr < 2000)).sum()), c21=int((yr >= 2000).sum()),
                   since1900_share=r4((yr >= 1900).mean()), c1499=int(B.cast_date.eq("c1499").sum()))
med = B[yr < 1500]
out["ages"]["medieval_rings"] = int(med.ring_id.nunique())
mc = R.assign(m=R.n_medieval).groupby("country").m.sum()
out["ages"]["medieval_england"] = int(mc.get("England", 0))
cm = R[eng].groupby("county").n_medieval.sum().sort_values(ascending=False)
out["ages"]["medieval_top_counties"] = [dict(county=k, n=int(v)) for k, v in cm.head(6).items()]
od = B[B.year_kind.eq("dated") & B.cast_date.str.fullmatch(r"\d{4}")].sort_values(["year", "bell_id"]).copy()
rr = R.set_index("ring_id")
def bell_row(b):
    r = rr.loc[b.ring_id]
    return dict(year=int(b.year), place=b.place, dedication=b.dedication, county=r.county, country=r.country, founder=b.founder if isinstance(b.founder, str) else "",
                role=b.role, ring_bells=int(r.bells), weight_lbs=None if pd.isna(b.weight_lbs) else int(b.weight_lbs))
out["oldest_dated"] = [bell_row(b) for b in od.drop_duplicates(["ring_id", "year"]).head(12).itertuples()]
out["oldest_dated_first"] = out["oldest_dated"][0]
out["dated_before1450"] = int((od.year < 1450).sum())

# ---------------- casting years ----------------
dy = B[B.year_kind.eq("dated")].groupby("year").size()
yrs = pd.Series(0, index=range(1550, 2026)); yrs.update(dy.reindex(yrs.index).fillna(0)); yrs = yrs.astype(int)
pd.DataFrame({"year": yrs.index, "dated_bells": yrs.values}).to_csv(D("cast_years.csv"), index=False)
out["cast_years"] = dict(start=1550, end=2025, n=[int(v) for v in yrs.values])
top = yrs.sort_values(ascending=False).head(10)
out["cast_years"]["top"] = [dict(year=int(k), n=int(v)) for k, v in top.items()]
out["cast_years"]["peak_year"] = int(top.index[0]); out["cast_years"]["peak_n"] = int(top.iloc[0])
EV = [(1887, "Victoria's Golden Jubilee"), (1897, "Victoria's Diamond Jubilee"), (1902, "Coronation of Edward VII"),
      (1911, "Coronation of George V"), (1935, "Silver Jubilee of George V"), (1937, "Coronation of George VI"),
      (1953, "Coronation of Elizabeth II"), (1977, "Silver Jubilee of Elizabeth II"), (2000, "The Millennium"),
      (2002, "Golden Jubilee of Elizabeth II"), (2012, "Diamond Jubilee of Elizabeth II")]
ev = []
for y, lab in EV:
    base = yrs.reindex([q for q in range(y - 3, y + 4) if q != y]).mean()
    ev.append(dict(year=y, label=lab, n=int(yrs[y]), base=round(float(base), 1), ratio=round(float(yrs[y] / base), 2)))
out["events"] = ev; out["event"] = {str(e["year"]): e for e in ev}
out["wars"] = dict(pre1=round(float(yrs.loc[1910:1914].mean()), 1), ww1=round(float(yrs.loc[1915:1918].mean()), 1), y1918=int(yrs[1918]),
                   pre2=round(float(yrs.loc[1934:1939].mean()), 1), ww2=round(float(yrs.loc[1940:1945].mean()), 1),
                   y1941=int(yrs[1941]), y1942=int(yrs[1942]), y1943=int(yrs[1943]), y1944=int(yrs[1944]), y1946=int(yrs[1946]),
                   ww2_total=int(yrs.loc[1940:1945].sum()))
dec = B[B.year_kind.eq("dated")].assign(dec=lambda d: (d.year // 10 * 10).astype(int)).groupby("dec").size()
out["decades"] = dict(peak_decade=int(dec.idxmax()), peak_n=int(dec.max()), d1900s=int(dec.get(1900, 0)), d2010s=int(dec.get(2010, 0)),
                      d1990s=int(dec.get(1990, 0)), d2000s=int(dec.get(2000, 0)), d1880s=int(dec.get(1880, 0)), d1890s=int(dec.get(1890, 0)))

# ---------------- founders ----------------
FAM = {"Loughborough": "Taylor", "Whitechapel": "Whitechapel", "Rudhall": "Rudhall", "Warner": "Warner", "Gillett": "Gillett & Johnston", "West Country": "West Country"}
B["fam"] = B.founder_group.map(FAM).fillna("Other founders")
B.loc[B.founder_group.isna() | B.founder_group.isin(["(unidentified)", "Unidentified (blank)"]), "fam"] = "Unknown"
B["bin"] = (B.year // 25 * 25)
fb = pd.crosstab(B.bin, B.fam).reindex(columns=["Whitechapel", "Taylor", "Rudhall", "Warner", "Gillett & Johnston", "West Country", "Other founders", "Unknown"], fill_value=0)
fb = fb.loc[1300:2000]
fb.index = fb.index.astype(int)
fb.reset_index().rename(columns={"bin": "from_year"}).to_csv(D("founders_by_period.csv"), index=False)
out["founders_period"] = dict(bins=[int(i) for i in fb.index], fams=list(fb.columns), n={c: [int(v) for v in fb[c]] for c in fb.columns})
fam_tot = B.fam.value_counts()
c20 = B[(B.year >= 1900) & (B.year < 2000)]
since = B[B.year >= 2018]
w = B[B.fam == "Whitechapel"]; t = B[B.fam == "Taylor"]
out["founders"] = dict(
    taylor=int(fam_tot["Taylor"]), whitechapel=int(fam_tot["Whitechapel"]), taylor_share=r4(fam_tot["Taylor"] / len(B)), whitechapel_share=r4(fam_tot["Whitechapel"] / len(B)),
    big2_share=r4((fam_tot["Taylor"] + fam_tot["Whitechapel"]) / len(B)), rudhall=int(fam_tot["Rudhall"]), warner=int(fam_tot["Warner"]),
    gillett=int(fam_tot["Gillett & Johnston"]),
    c20_big2_share=r4(c20.fam.isin(["Taylor", "Whitechapel"]).mean()), c20_taylor_share=r4(c20.fam.eq("Taylor").mean()),
    since2018_taylor_share=r4(since.fam.eq("Taylor").mean()), since2018_n=len(since),
    whitechapel_last=int(w.year.max()), whitechapel_first=int(w.year.min()), taylor_first=int(t.year.min()),
    n_founders=int(B.founder.nunique()), unknown=int(fam_tot.get("Unknown", 0)),
    rudhall_peak=int(B[B.fam == "Rudhall"].year.median()))
tf = B[B.founder.notna() & ~B.founder.isin(["(unidentified)", "Unidentified (blank)"])].founder.value_counts().head(10)
out["top_founders"] = [dict(founder=k, n=int(v)) for k, v in tf.items()]
# Whitechapel vs Taylor lead by quarter century
lead = []
for b in fb.index:
    if b >= 1750: lead.append(dict(bin=int(b), whitechapel=int(fb.loc[b, "Whitechapel"]), taylor=int(fb.loc[b, "Taylor"])))
out["lead"] = lead

# ---------------- growth of big rings ----------------
# for each present ring, the year its newest bell was cast (all bells with a year): the earliest the ring could have had its present form
g = []
for n in (6, 8, 10, 12):
    s = R[(R.bells == n) & R.newest_year.notna()].newest_year
    cum = [int((s <= y).sum()) for y in range(1600, 2026, 5)]
    g.append(dict(bells=n, n=int(len(s)), median_newest=int(s.median()), before1800=int((s < 1800).sum()), before1900=int((s < 1900).sum()),
                  since1950=int((s >= 1950).sum()), share_since1950=r4((s >= 1950).mean()), share_before1900=r4((s < 1900).mean()), cum=cum))
out["growth"] = dict(years=list(range(1600, 2026, 5)), sizes=g)
out["growth_by"] = {str(x["bells"]): x for x in g}
pd.DataFrame({"year": list(range(1600, 2026, 5)), **{f"rings_of_{x['bells']}": x["cum"] for x in g}}).to_csv(D("growth.csv"), index=False)

# ---------------- frames ----------------
fr = FR[FR.year.notna() & FR.material_group.isin(["timber", "cast iron", "steel", "iron and steel", "mixed"])].copy()
fr["mg"] = fr.material_group.replace({"iron and steel": "steel", "mixed": "cast iron"})
fr["bin"] = (fr.year // 25 * 25).astype(int)
ft = pd.crosstab(fr.bin, fr.mg).loc[1500:2000]
out["frames"] = dict(n=len(fr), bins=[int(i) for i in ft.index], n_by={c: [int(v) for v in ft[c]] for c in ["timber", "cast iron", "steel"]},
                     first_iron=int(fr[fr.mg == "cast iron"].year.min()), timber_share_pre1850=r4((fr[fr.year < 1850].mg == "timber").mean()),
                     iron_share_1875_1950=r4((fr[(fr.year >= 1875) & (fr.year < 1950)].mg == "cast iron").mean()),
                     steel_share_since1975=r4((fr[fr.year >= 1975].mg == "steel").mean()),
                     timber_share_since1975=r4((fr[fr.year >= 1975].mg == "timber").mean()))

# ---------------- geography ----------------
out["geo"] = GEO
cc = C[C.nation.isin(["England", "Wales"])].copy()
big_c = cc[cc.area_km2 >= 1000].sort_values("rings_per_100km2", ascending=False)
out["county_density_top"] = [dict(county=r.county, rings=int(r.rings), per100=round(r.rings_per_100km2, 2)) for r in big_c.head(6).itertuples()]
out["county_density_bottom"] = [dict(county=r.county, rings=int(r.rings), per100=round(r.rings_per_100km2, 2)) for r in big_c.tail(5).itertuples()]
sh = cc[cc.anglican_churches_osm >= 100].sort_values("share_with_ring", ascending=False)
out["county_share_top"] = [dict(county=r.county, share=r4(r.share_with_ring), churches=int(r.anglican_churches_osm)) for r in sh.head(6).itertuples()]
out["county_share_bottom"] = [dict(county=r.county, share=r4(r.share_with_ring), churches=int(r.anglican_churches_osm)) for r in sh.tail(6).itertuples()]
most = cc.sort_values("rings", ascending=False)
out["county_most"] = [dict(county=r.county, rings=int(r.rings)) for r in most.head(6).itertuples()]
out["county_n"] = dict(eng_wales=len(cc), with_share=len(sh))
out["counties"] = [dict(county=r.county, nation=r.nation, rings=int(r.rings), per100=round(r.rings_per_100km2, 2), churches=int(r.anglican_churches_osm),
                        share=None if pd.isna(r.share_with_ring) else r4(r.share_with_ring), medieval=int(r.medieval_bells), eights=int(r.eights_plus))
                   for r in C.sort_values("county").itertuples()]
ewm = R[R.country.isin(["England", "Wales"])]
out["regions_ns"] = dict(south_of_52=r4((ewm.lat < 52.5).mean()))

# ---------------- the world beyond ----------------
ab = R[~R.country.isin(["England", "Wales", "Scotland", "Ireland", "Channel Islands", "Isle of Man"])]
out["abroad"] = dict(n=len(ab), countries=int(ab.country.nunique()), australia=int(R.country.eq("Australia").sum()), usa=int(R.country.eq("USA").sum()),
                     canada=int(R.country.eq("Canada").sum()), nz=int(R.country.eq("New Zealand").sum()), sa=int(R.country.eq("South Africa").sum()),
                     eights_plus_share=r4((ab.bells >= 8).mean()), twelves=int((ab.bells == 12).sum()),
                     median_newest=int(ab.newest_year.median()))
for c in ("USA", "Australia"):
    s = B[B.ring_id.isin(R[R.country == c].ring_id)].sort_values("year").iloc[0]
    out["abroad"][f"oldest_{c.lower()}"] = dict(year=int(s.year), place=s.place, dedication=s.dedication)
abr = R[R.country.isin(["USA", "Australia"])]
out["abroad"]["usa_states"] = int(R[R.country == "USA"].county.nunique())

# ---------------- compact site data ----------------
pts = R[R.lat.notna()].copy()
counties = sorted(pts.county.fillna("").unique().tolist()); countries = sorted(pts.country.unique().tolist())
groups = sorted(pts.main_founder_group.fillna("").unique().tolist())
cI = {c: i for i, c in enumerate(counties)}; nI = {c: i for i, c in enumerate(countries)}; gI = {c: i for i, c in enumerate(groups)}
def nz(v, d=None): return d if pd.isna(v) else v
rows = []
for r in pts.itertuples():
    rows.append([round(r.lat, 5), round(r.lon, 5), r.place + (f", {r.place2}" if isinstance(r.place2, str) else ""), nz(r.dedication, ""),
                 cI[nz(r.county, "")], nI[r.country], int(r.bells), nz(r.tenor_cwt, ""), nz(r.tenor_note, ""), int(r.unringable),
                 nz(r.practice, ""), None if pd.isna(r.oldest_year) else int(r.oldest_year), int(nz(r.n_medieval, 0)), gI[nz(r.main_founder_group, "")],
                 int(r.tower_id), int(r.ring_type == "Lightweight ring"), int(r.ground_floor), None if pd.isna(r.newest_year) else int(r.newest_year),
                 None if pd.isna(r.tenor_lbs) else int(r.tenor_lbs)])
site = dict(cols=["lat", "lon", "place", "ded", "county", "country", "bells", "cwt", "note", "ur", "practice", "oldest", "medieval", "group", "tid", "light", "gf", "newest", "lbs"],
            counties=counties, countries=countries, groups=groups, rows=rows)
json.dump(site, open(os.path.join(ROOT, "work", "site_data.json"), "w"), separators=(",", ":"), ensure_ascii=False)
out["site"] = dict(points=len(rows))

json.dump(out, open(D("results.json"), "w"), indent=1, ensure_ascii=False)
s = json.dumps(out, ensure_ascii=False)
assert "–" not in s and "—" not in s
print("results.json", len(s))
for k in ["counts", "size_groups", "unringable", "practice", "extras", "tenor", "ages", "wars", "decades", "founders", "frames", "abroad", "dedications", "twelves"]:
    print(k, json.dumps(out[k], ensure_ascii=False)[:900])
print(out["events"]); print(out["oldest_dated"][:6]); print([ (x["bells"], x["n"], x["median_newest"], x["share_since1950"], x["share_before1900"]) for x in g])
print(out["county_density_top"], out["county_share_top"], out["county_share_bottom"], out["heaviest"][:4], out["top_founders"])
