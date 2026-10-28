"""Step 2. Geography: counties, churches and neighbours.

- Each ring in Great Britain is placed in a county (ceremonial counties of England, preserved counties of Wales, council
  areas of Scotland) by point in polygon, using the county boundaries built for my Roman roads study from ONS local
  authority boundaries (../../how-roman-is-your-road/data/counties.geojson). County areas are measured on the British
  National Grid.
- OpenStreetMap Anglican places of worship (amenity=place_of_worship, religion=christian, denomination containing
  "anglican", or church_of_england / church_in_wales), from ../../_data12/wd_osm_bundle12.json.gz, are placed in the
  same counties, and each is checked for a Dove ring within 150 m. That gives the share of mapped Anglican churches
  that have a ring of bells, by county. Only counts leave this script; no OSM rows are published.
- Distance from every ring to the nearest other ring (England and Wales).
- A slim OS Open Names list of cities, towns, villages and suburbs for the page's "find your tower" search.
Outputs: work/geo.json, data/counties.csv, work/places_search.json, work/counties_simpl.json
Run: python3 code/02_geo.py
"""
import gzip, io, json, os
import numpy as np, pandas as pd
from pyproj import Transformer
from shapely.geometry import shape, Point, mapping
from shapely import wkt as swkt
from shapely.strtree import STRtree
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, ".."); UP = os.path.join(ROOT, "..")
T = Transformer.from_crs(4326, 27700, always_xy=True)
R = pd.read_csv(os.path.join(ROOT, "data", "rings.csv"))

# ---------- counties ----------
G = json.load(open(os.path.join(UP, "how-roman-is-your-road", "data", "counties.geojson")))
polys, names, nations = [], [], []
for f in G["features"]:
    polys.append(shape(f["geometry"])); names.append(f["properties"]["county"]); nations.append(f["properties"]["nation"])
tree = STRtree(polys)


def county_of(lon, lat):
    p = Point(lon, lat)
    for i in tree.query(p):
        if polys[i].contains(p): return int(i)
    return -1


import shapely
area = [shapely.transform(p, lambda c: np.c_[T.transform(c[:, 0], c[:, 1])]).area / 1e6 for p in polys]

has = R.lat.notna() & R.lon.notna()
gb = R.iso.eq("GB") & R.country.isin(["England", "Wales", "Scotland"]) & has
R["cidx"] = -1
R.loc[gb, "cidx"] = [county_of(lo, la) for lo, la in zip(R.loc[gb, "lon"], R.loc[gb, "lat"])]
# rings on the coast just outside the generalised boundary: nearest county
miss = gb & R.cidx.eq(-1)
for i in R.index[miss]:
    p = Point(R.at[i, "lon"], R.at[i, "lat"]); R.at[i, "cidx"] = int(np.argmin([q.distance(p) for q in polys]))
R["gb_county"] = [names[i] if i >= 0 else "" for i in R.cidx]
print("rings outside polygons, snapped:", int(miss.sum()))

# ---------- OSM Anglican churches ----------
bund = json.load(gzip.open(os.path.join(UP, "_data12", "wd_osm_bundle12.json.gz")))
W = pd.read_csv(io.StringIO(bund["results"]["osm_worship"]["tsv"]), sep="\t", low_memory=False)
W.columns = [c.lstrip("?") for c in W.columns]
den = W.denom.fillna("").str.lower()
ang = den.str.contains("anglican") | den.isin(["church_of_england", "church_in_wales"])
W = W[ang].copy()
cent = [swkt.loads(s.strip().strip('"')[: s.strip().strip('"').rfind(")") + 1]).centroid for s in W.wkt]
W["lon"] = [c.x for c in cent]; W["lat"] = [c.y for c in cent]
W["cidx"] = [county_of(lo, la) for lo, la in zip(W.lon, W.lat)]
W = W[W.cidx >= 0]
rx, ry = T.transform(R.lon.fillna(0).values, R.lat.fillna(0).values)
R["x"], R["y"] = rx, ry
ew = (R.country.isin(["England", "Wales"]) & has).values
kt = cKDTree(np.c_[rx[ew], ry[ew]])
wx, wy = T.transform(W.lon.values, W.lat.values)
d, _ = kt.query(np.c_[wx, wy])
W["has_ring"] = d <= 150
# and the other way: rings with a mapped Anglican church within 150 m
kw = cKDTree(np.c_[wx, wy]); d2, _ = kw.query(np.c_[rx[ew], ry[ew]])
ring_near_ang = float((d2 <= 150).mean())

# ---------- nearest other ring (England and Wales) ----------
dd, _ = kt.query(np.c_[rx[ew], ry[ew]], k=2)
nn = dd[:, 1] / 1000
R.loc[ew, "nearest_ring_km"] = np.round(nn, 2)

# ---------- county table ----------
rows = []
for i, (nm, na) in enumerate(zip(names, nations)):
    rr = R[R.cidx == i]; ww = W[W.cidx == i]
    rows.append(dict(county=nm, nation=na, area_km2=round(area[i], 1), rings=len(rr), bells=int(rr.bells.sum()),
                     rings_per_100km2=round(len(rr) / area[i] * 100, 3), unringable=int(rr.unringable.sum()),
                     eights_plus=int((rr.bells >= 8).sum()), anglican_churches_osm=len(ww), anglican_with_ring=int(ww.has_ring.sum()),
                     share_with_ring=round(ww.has_ring.mean(), 4) if len(ww) else None,
                     median_tenor_lbs=float(rr.tenor_lbs.median()) if len(rr) else None,
                     medieval_bells=int(rr.n_medieval.sum())))
C = pd.DataFrame(rows).sort_values("rings_per_100km2", ascending=False)
C.to_csv(os.path.join(ROOT, "data", "counties.csv"), index=False)
R.drop(columns=["cidx", "x", "y"]).to_csv(os.path.join(ROOT, "data", "rings.csv"), index=False)

# ---------- simplified county outlines for the page and figures ----------
simp = []
for p, nm, na in zip(polys, names, nations):
    s = p.simplify(0.004, preserve_topology=True)
    if s.geom_type == "GeometryCollection":
        from shapely.geometry import MultiPolygon
        s = MultiPolygon([g for g in s.geoms if g.geom_type == "Polygon"] + [q for g in s.geoms if g.geom_type == "MultiPolygon" for q in g.geoms])
    gj = mapping(s)
    def rnd(c):
        return [rnd(x) for x in c] if isinstance(c[0], (list, tuple)) else [round(c[0], 3), round(c[1], 3)]
    gj = {"type": gj["type"], "coordinates": rnd(gj["coordinates"])}
    simp.append({"type": "Feature", "properties": {"county": nm, "nation": na}, "geometry": gj})
json.dump({"type": "FeatureCollection", "features": simp}, open(os.path.join(ROOT, "work", "counties_simpl.json"), "w"), separators=(",", ":"))

# ---------- OS Open Names places for the search ----------
o = pd.read_csv(os.path.join(UP, "osnames_gb.tsv"), sep="\t", usecols=["name1", "type", "local_type", "lat", "lon", "county", "district"], low_memory=False)
o = o[(o.type == "populatedPlace") & o.local_type.isin(["City", "Town", "Village", "Suburban Area"])]
o = o.drop_duplicates(["name1", "county"])
ps = [[n, round(la, 4), round(lo, 4), (c if isinstance(c, str) else (dz if isinstance(dz, str) else ""))] for n, la, lo, c, dz in zip(o.name1, o.lat, o.lon, o.county, o.district)]
json.dump({"rows": ps}, open(os.path.join(ROOT, "work", "places_search.json"), "w"), separators=(",", ":"), ensure_ascii=False)

geo = dict(anglican_osm=int(len(W)), anglican_with_ring=int(W.has_ring.sum()), anglican_share=round(float(W.has_ring.mean()), 4),
           ring_near_anglican_share=round(ring_near_ang, 4), n_ew=int(ew.sum()),
           nn_median_km=round(float(np.median(nn)), 2), nn_mean_km=round(float(np.mean(nn)), 2),
           nn_within2=round(float((nn <= 2).mean()), 4), nn_within3=round(float((nn <= 3).mean()), 4), nn_over5=round(float((nn > 5).mean()), 4),
           nn_max_km=round(float(nn.max()), 1), nn_max_place=R.loc[ew].iloc[int(np.argmax(nn))]["place"],
           snapped=int(miss.sum()), places_search=len(ps))
json.dump(geo, open(os.path.join(ROOT, "work", "geo.json"), "w"), indent=1)
print(json.dumps(geo, indent=1))
print(C.head(12).to_string()); print(C[C.nation != "Scotland"].sort_values("share_with_ring").head(8).to_string())
