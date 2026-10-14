# Atlas 地圖練習室
Buildless static app. Serve `dist/` with any static server.

Data: Natural Earth 1:10m admin-0 countries and admin-1 states/provinces, retrieved 2026-10-13 from https://github.com/nvkelso/natural-earth-vector/tree/master/geojson . Public domain. D3 v7 is distributed under ISC (license in the vendored file).

To regenerate: download `ne_10m_admin_1_states_provinces.geojson` as `admin1.json` and `ne_10m_admin_0_countries.geojson` as `world10.json`, install Python shapely and opencc-python-reimplemented, run `python prepare.py` followed by `python enrich.py`. Generated per-country data is committed. Run `node --check dist/app.js` and `node check.cjs`.

Limitations are shown in-app: dataset snapshot is not a current official register; Vietnam is the old 63-province version; Taiwan source has 21 counties/cities and lacks Kinmen. Some country subdivision levels differ from current legal classifications. France, Italy, Spain, Belgium are dissolved to regions; UK to four constituent countries. Missing translations/native scripts are marked. Boundaries use Natural Earth's de facto dataset.

Specification v1.0 update: collision-aware map labels, manual continue after wrong/skip, 1-second automatic correct-answer advance, persistent completed regions, in-memory round statistics and exit confirmation. Country metadata distinguishes historical boundary version from retrieval date. Browser QA unavailable in managed environment; data geometry and quiz transitions tested with Node.
