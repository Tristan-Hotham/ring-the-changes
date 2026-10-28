# Ring the changes: where England's bells hang

Every ring of church bells hung for full-circle change ringing in Dove's Guide for Church Bell Ringers: where the rings are, how many bells they have, the heaviest tenors, the oldest bells still rung, the great bell founders, the frames the bells hang in, practice nights, and the years in which the bells now hanging were cast.

**Interactive version:** https://tristan-hotham.github.io/ring-the-changes/

This repository holds the interactive page, derived data and the analysis code for the data study *Ring the Changes: Where England's Bells Hang. A Data Study of Dove's Guide for Church Bell Ringers* by Dr Tristan Hotham (Independent researcher, ORCID 0000-0003-4931-9349). Paper and archived release: https://doi.org/10.5281/zenodo.23729641

## Headline results

- Dove's Guide lists 7,262 rings of three or more bells (7,124 full-circle rings and 138 lightweight rings) holding 45,682 bells, in 7,249 towers. 6,779 rings (93%) are in England, 230 in Wales, 43 on the island of Ireland and 24 in Scotland; 170 are outside the British Isles (74 in Australia, 50 in the USA).
- 40% of the 16,567 Anglican churches mapped in OpenStreetMap in England and Wales have a Dove ring within 150 m: 73% in Northamptonshire and 67% in Devon, but 8% in Northumberland and 6% in Gwynedd. Half of all rings in England and Wales are within 2.3 km of another.
- Six bells is the norm (3,000 rings, 41%); there are 1,956 eights, 317 tens and 153 twelves. 964 rings (13%) are unringable, 86% of them rings of three to five bells.
- Big rings are recent: the median newest bell in a ring of twelve was cast in 1999, and 89% of twelves have a bell cast since 1950.
- The median bell in a ring was cast in 1876; 1,376 bells are dated or judged to be before 1500. The oldest bell with a single cast year is the fourth at Cold Ashby, Northamptonshire, dated 1317.
- The Whitechapel and Taylor foundry families cast 49% of all bells now in rings and 79% of those cast in the twentieth century. Whitechapel's last bells are dated 2017.
- The peak casting years are 1897 (443 bells) and 1887 (388), Victoria's Diamond and Golden Jubilees, each about twice the years around them; 1937 shows the same jump. No bell now in a ring was cast in 1943 or 1944.

## Files

- `index.html`: the interactive page (Leaflet map of every ring with three colour modes, tower and place search, nearest rings, charts and tables).
- `header.png`: social card.
- `data/rings.csv`: one row per ring: Dove ring and tower IDs and link, place, dedication, county, country, coordinates, number of bells, unringable flag, tenor weight (lb, cwt-qr-lb, kg) and note, practice night, ground floor, simulator, listed grade, summary of its bells (oldest, newest and median cast year, medieval bells, main foundry group), main frame date and material, county from ONS boundaries and distance to the nearest other ring.
- `data/bells.csv`: one row per bell in those rings: weight, note, nominal, diameter, material, cast date as Dove gives it and the parsed year with its kind (dated, circa, range, bound), founder and Dove founder group, canons, turnings, cracked or welded, listed.
- `data/frames.csv`: bell frames in towers with a ring: date, materials and material group, maker.
- `data/counties.csv`: rings, density, unringable rings, eights and over, mapped Anglican churches and the share with a ring, medieval bells, by county.
- `data/countries.csv`, `data/ring_sizes.csv`, `data/cast_years.csv`, `data/founders_by_period.csv`, `data/growth.csv`: summary tables behind the charts.
- `data/places_search.json`: OS Open Names cities, towns, villages and suburbs for the page's place search. `data/coast_ne10m.json`: Natural Earth land outline for the figures.
- `data/results.json`: every number quoted on the page, in the paper, the blog post and the collage.
- `code/`: Python scripts, run in order: `01_prepare.py` (clean Dove tables, parse cast dates), `02_geo.py` (counties, OpenStreetMap churches, distances, place list), `03_analyse.py` (all statistics), `04_build_site.py` (page), `05_header.py` (social card), `06_figures.py` (paper and blog figures), `07_paper.py` (paper PDF via xelatex), `08_release.py` (blog post and Zenodo files).
- `release/`: paper PDF and LaTeX source, blog post and figures, Zenodo files. `reddit/`: collage and post text.

## Method in brief

**Rings and bells.** Dove's rings table (rings of three or more bells hung for full-circle ringing) and bells table, restricted to bells in those rings and leaving out sanctus and service bells (45,974 records). Cast dates: a single year (sometimes bracketed) counts as dated; "c" dates as approximate at the year given; ranges at their midpoint. Many medieval bells carry Dove's style dates (278 are "c1499"), so "before 1500" means dated or judged medieval. Foundry families follow the Group column of Dove's founders table.

**When rings reached their present size.** Dove does not record augmentations; the year of a ring's newest bell is an upper bound on when it took its present form (a later recast pushes it forward).

**Places.** Counties by point in polygon with ONS boundaries (ceremonial counties of England, preserved counties of Wales). OpenStreetMap Christian places of worship with an Anglican, Church of England or Church in Wales denomination; a church has a ring if a Dove ring lies within 150 m. Untagged churches are left out, so shares are approximate.

**Caveats.** Dove records bells that exist now, so every historical pattern is a pattern of survival. Founder attributions and groups are Dove's. Practice nights are as towers report them. All results are descriptive.

## How to rerun

Python 3 with pandas, numpy, scipy, shapely, pyproj and matplotlib (Playwright for the header, xelatex for the paper). From the project folder: `python3 code/01_prepare.py && python3 code/02_geo.py && python3 code/03_analyse.py && python3 code/04_build_site.py`, then steps 05 to 08. Inputs are read one folder up and are not included: `_data12/dove_bundle.json.gz` (the Dove CSV downloads), `_data12/wd_osm_bundle12.json.gz` (OpenStreetMap places of worship via QLever), `osnames_gb.tsv` (OS Open Names), `how-roman-is-your-road/data/counties.geojson` (county boundaries from ONS) and `saints-and-wells/data/results.json` (one comparison figure).

## Sources and licence

- Bell data: Dove's Guide for Church Bell Ringers, Central Council of Church Bell Ringers, dove.cccbr.org.uk, CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/). Downloads: https://dove.cccbr.org.uk/downloads, retrieved 28 October 2026. Changes were made: the tables were cleaned (en dashes in date ranges rewritten as "to"), cast dates parsed into years, rings summarised, and counties, distances and church matches added. This work is not endorsed by the Central Council of Church Bell Ringers.
- Churches: © OpenStreetMap contributors, ODbL (https://www.openstreetmap.org/copyright), used for counts only; no OpenStreetMap rows are republished.
- County boundaries: Office for National Statistics, Open Government Licence v3.0; contains OS data © Crown copyright and database right 2026. Place search: OS Open Names, Ordnance Survey, Open Government Licence v3.0, contains OS data © Crown copyright and database right 2026.
- History: English Wikipedia articles "Change ringing", "Church bell", "Ring of bells", "Whitechapel Bell Foundry", "John Taylor & Co" and "Dove's Guide for Church Bell Ringers" (CC BY-SA 4.0).
- Coastline: Natural Earth (public domain). Base map tiles on the page: Esri. Map library: Leaflet.

As Dove's licence requires, the derived data in `data/` and the text of the page are released under CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/). Code is MIT (see `LICENSE`).

Companion study: [Saints and wells](https://tristan-hotham.github.io/saints-and-wells/).

## Citation

Hotham, T. (2026) *Ring the Changes: Where England's Bells Hang. A Data Study of Dove's Guide for Church Bell Ringers*. Zenodo. https://doi.org/10.5281/zenodo.23729641

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
