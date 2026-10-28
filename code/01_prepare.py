"""Step 1. Read Dove's Guide (CSV files bundled in ../../_data12/dove_bundle.json.gz) and write clean derived tables.

Outputs (data/):
  rings.csv   one row per ring of 3 or more bells hung for full-circle ringing (Dove's dove.csv), with tenor weight
              converted to cwt-qr-lb and kg, practice day, unringable flag and a summary of the ring's bells
              (oldest and newest cast year, number of medieval bells, main founder group, frame material and date).
  bells.csv   one row per bell in those rings (Dove's bells.csv), with the cast date parsed to a year and the kind of date.
  frames.csv  one row per bell frame in those towers (Dove's frames.csv): date, material group, maker.
Ranges in Dove's text use an en dash; they are rewritten here as "1590 to 1620".
Run: python3 code/01_prepare.py
"""
import gzip, io, json, os, re
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
SRC = os.path.join(ROOT, "..", "_data12", "dove_bundle.json.gz")
os.makedirs(os.path.join(ROOT, "data"), exist_ok=True); os.makedirs(os.path.join(ROOT, "work"), exist_ok=True)

bundle = json.load(gzip.open(SRC))
F = {k: pd.read_csv(io.StringIO(v), low_memory=False) for k, v in bundle["files"].items()}
META = {"retrieved": bundle["retrieved"], "licence": bundle["licence"]}
dv, bells, founders, frames = F["dove.csv"], F["bells.csv"], F["founders.csv"], F["frames.csv"]


def clean(s):
    """Dove text with en and em dashes replaced (house style), whitespace tidied."""
    if pd.isna(s): return s
    s = str(s).replace("–", " to ").replace("—", ", ").replace("--", " to ")
    return re.sub(r"\s+", " ", s).strip()


# ---------- cast dates ----------
def parse_year(raw):
    """Return (year, kind). kind: dated (a year, as Dove gives it, possibly bracketed), circa, range (midpoint), bound, none."""
    if pd.isna(raw): return (np.nan, "none")
    s = str(raw).strip()
    m = re.fullmatch(r"(\d{4})(?: \((\d{4})\))?", s)
    if m: return (int(m.group(1)), "dated")
    m = re.fullmatch(r"\((\d{4})\)", s)
    if m: return (int(m.group(1)), "dated")
    m = re.fullmatch(r"c(\d{4})", s)
    if m: return (int(m.group(1)), "circa")
    m = re.fullmatch(r"\[(\d{4})\s*[–\-]\s*(\d{4})\]", s)
    if m: return ((int(m.group(1)) + int(m.group(2))) / 2, "range")
    m = re.fullmatch(r"\[(?:from|to) (\d{4})\]", s)
    if m: return (int(m.group(1)), "bound")
    m = re.fullmatch(r"\[(\d{4})\]", s)
    if m: return (int(m.group(1)), "dated")
    return (np.nan, "none")


# founder groups as Dove's founders table defines them (Group column); a founder with no group is its own group
fg = founders.dropna(subset=["Group"]).drop_duplicates("Name").set_index("Name")["Group"]
GROUP_LABEL = {"Loughborough": "Taylor (Loughborough)", "Whitechapel": "Whitechapel (London)", "Rudhall": "Rudhall (Gloucester)",
               "Warner": "Warner (London)", "Gillett": "Gillett & Johnston (Croydon)", "West Country": "West Country founders",
               "Eijsbouts": "Eijsbouts (Netherlands)"}

rb = bells[bells["Ring ID"].isin(dv.RingID)].copy()
rb = rb[~rb["Bell Role"].astype(str).isin(["Sanctus", "Service"])]
yk = rb["Cast Date"].map(parse_year)
rb["year"] = [a for a, _ in yk]; rb["year_kind"] = [b for _, b in yk]
rb["cast_date"] = rb["Cast Date"].map(clean)
rb["founder"] = rb["Founder"].map(clean)
rb["founder_group"] = [fg.get(f, f) if isinstance(f, str) else np.nan for f in rb["Founder"]]
rb["founder_uncertain"] = rb["Founder Uncertain"].eq("Y")
B = pd.DataFrame({
    "bell_id": rb["Bell ID"], "ring_id": rb["Ring ID"], "tower_id": rb["Tower ID"], "place": rb["Place"].map(clean),
    "dedication": rb["Dedication"].map(clean), "role": rb["Bell Role"].astype(str), "weight_lbs": rb["Weight (lbs)"],
    "weight_approx": rb["Weight (approx)"].notna(), "note": rb["Note"], "nominal_hz": rb["Nominal (Hz)"], "diameter_in": rb["Diameter (in)"],
    "material": rb["Material"], "cast_date": rb["cast_date"], "year": rb["year"], "year_kind": rb["year_kind"],
    "founder": rb["founder"], "founder_group": rb["founder_group"].map(clean), "founder_uncertain": rb["founder_uncertain"],
    "canons": rb["Canons"], "turnings": rb["Turnings"], "cracked": rb["Cracked"], "listed": rb["Listed"].eq("Y")})
B = B.sort_values(["ring_id", "bell_id"])

# ---------- frames ----------
tid = set(dv.TowerID)
fr = frames[frames["Tower ID"].isin(tid)].copy()
def frame_year(s):
    m = re.search(r"(\d{4})", str(s)); return int(m.group(1)) if m else np.nan
def mat_group(s):
    s = str(s).lower()
    if s == "nan": return "unknown"
    if "steel" in s and "iron" not in s and "oak" not in s and "timber" not in s: return "steel"
    if "iron" in s and not any(w in s for w in ("oak", "timber", "steel")): return "cast iron"
    if s in ("oak", "timber", "teak", "iroko", "elm", "wood", "jarrah", "greenheart") or (("oak" in s or "timber" in s) and not any(w in s for w in ("iron", "steel"))): return "timber"
    if any(w in s for w in ("iron", "steel")) and any(w in s for w in ("oak", "timber")): return "mixed"
    if "iron;steel" in s or ("iron" in s and "steel" in s): return "iron and steel"
    return "other"
FR = pd.DataFrame({"frame_id": fr["Frame ID"], "tower_id": fr["Tower ID"], "place": fr["Place"].map(clean), "frame_number": fr["Frame Number"],
                   "frame_date": fr["Frame Date"].map(clean), "year": fr["Frame Date"].map(frame_year), "materials": fr["Materials"],
                   "material_group": fr["Materials"].map(mat_group), "maker": fr["Maker"].map(clean)})

# ---------- rings ----------
def cwt(lbs):
    if pd.isna(lbs): return ""
    lbs = int(round(lbs)); c, r = divmod(lbs, 112); q, l = divmod(r, 28); return f"{c}-{q}-{l}"
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
def pday(s):
    if pd.isna(s): return ""
    m = re.match(r"(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b", str(s)); return m.group(1) if m else "other"
COUNTRY = {"United States of America": "USA", "Island of Ireland": "Ireland"}

g = B.groupby("ring_id")
summ = pd.DataFrame({
    "n_bell_records": g.size(),
    "oldest_year": g["year"].min(), "newest_year": g["year"].max(), "median_year": g["year"].median(),
    "n_dated": g["year"].count(), "n_medieval": g["year"].apply(lambda s: int((s < 1500).sum())),
    "oldest_dated_year": B[B.year_kind == "dated"].groupby("ring_id")["year"].min(),
    "n_cracked": g["cracked"].apply(lambda s: int(s.eq("cracked").sum())),
})
def main_group(df):
    s = df["founder_group"].dropna()
    s = s[s != "(unidentified)"]
    return s.value_counts().index[0] if len(s) else ""
summ["main_founder_group"] = g.apply(main_group)
summ["groups"] = g["founder_group"].apply(lambda s: "; ".join(f"{k} ({v})" for k, v in s.dropna().value_counts().items()))
fmain = FR.sort_values(["tower_id", "frame_number"]).drop_duplicates("tower_id").set_index("tower_id")

R = pd.DataFrame({
    "ring_id": dv.RingID, "tower_id": dv.TowerID, "dove_url": "https://dove.cccbr.org.uk/tower/" + dv.TowerID.astype(str),
    "ring_type": dv.RingType, "place": dv.Place.map(clean), "place2": dv.Place2.map(clean), "dedication": dv.Dedicn.map(clean),
    "tower_status": dv.TowerStatus.map(clean), "ring_name": dv.RingName.map(clean), "county": dv.County.map(clean),
    "region": dv.Region.map(clean), "historic_county": dv.HistRegion.map(clean), "country": dv.Country.replace(COUNTRY), "iso": dv.ISO3166code,
    "diocese": dv.Diocese.map(clean), "lat": dv.Lat, "lon": dv.Long, "bells": dv.Bells, "unringable": dv.UR.eq("u/r"),
    "semitones": dv.Semitones, "tenor_lbs": dv.Wt, "tenor_approx": dv.App.eq("app"), "tenor_cwt": dv.Wt.map(cwt),
    "tenor_kg": (dv.Wt * 0.45359237).round(0), "tenor_note": dv.Note, "tenor_hz": dv.Hz, "ground_floor": dv.GF.eq("GF"),
    "simulator": dv.Simulator.eq("T"), "practice": dv.Practice.map(clean), "practice_day": dv.Practice.map(pday),
    "listed_grade": dv.LGrade, "overhaul": dv.OvhaulYr.map(clean), "contractor": dv.Contractor.map(clean),
    "extra_info": dv.ExtraInfo.map(clean)})
R = R.join(summ, on="ring_id")
R["frame_year"] = R.tower_id.map(fmain["year"]); R["frame_material"] = R.tower_id.map(fmain["material_group"])
R["frame_maker"] = R.tower_id.map(fmain["maker"])
R = R.sort_values(["country", "county", "place", "ring_id"])

for df, name in [(R, "rings.csv"), (B, "bells.csv"), (FR, "frames.csv")]:
    for c in df.columns:
        if df[c].dtype == object:
            assert not df[c].astype(str).str.contains("[–—]|--", regex=True).any(), (name, c)
    df.to_csv(os.path.join(ROOT, "data", name), index=False)
    print(name, len(df), os.path.getsize(os.path.join(ROOT, "data", name)))
json.dump(META, open(os.path.join(ROOT, "work", "meta.json"), "w"))
print(B.year_kind.value_counts().to_dict())
