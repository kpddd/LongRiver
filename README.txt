            +-----------+
            |Data Source|
            +--^--+-----+
               |  |
+-------+    +-+--v--+    +-------+
|Trigger+---->Fetcher+---->Storage|
+-------+    +-------+    +-^--+--+
                            |  |
                         +--+--v--+
                         |Showcase|
                         +----+---+
                              |
                         +----+------+
                         | User view |
                         +-----------+

----------------------------------------------------------------------

                  +-----------+
                  |Data Source|
                  +--^--+-----+
                     |  |
                 +-----------------------------+
                 |   |  |       Git Repository |
+----------------------------+                 |
| +-----------+  |   |  |    |                 |
| |on:        |  | +-+--v--+ | +-----------+   |
| |  schedule:+---->main.py+--->.json,.csv |   |
| |  - cron   |  | +-------+ | +----+------+   |
| +--+--------+  |           |      |          |
|                |           | +------------+  |
| GitHub Actions |           | | .html,.js  |  |
+----------------------------+ +----+-------+  |
                 |                  |          |
                 +-----------------------------+
                                    |
                                +---v----------+
                                | GitHub Pages |
                                +--------------+
                                
## Collection reliability

Collection fetches up to four sources concurrently, with three attempts per
source and 2/4-second retry delays. Requests use a 10-second connection timeout
and a 30-second read inactivity timeout. Source order still determines which
record wins when station timestamps overlap. Partial source failures allow the
remaining observations to be saved; failure of every source fails the run.

Logs report each attempt, successful observation counts, elapsed time and a
source summary. Actions streams these logs immediately and limits the collection
step to five minutes. Request timeouts are not an overall wall-clock deadline
(DNS, multiple addresses and slow responses can take longer). For eight sources
each failing on a single connection timeout, the expected retry wait is about
72 seconds, excluding overhead. These limits do not restore an unavailable
upstream service; check runner connectivity and source availability if all
sources fail repeatedly.

## Static site

The repository now includes a Vite + TypeScript + ECharts static site in
`site/`. GitHub Actions builds the site and publishes it to GitHub Pages after
each scheduled data collection run:

Target Pages URLs after Pages is enabled:

* overview: https://doradx.github.io/LongRiver/
* station detail: https://doradx.github.io/LongRiver/station/?id=60112200
* data notes: https://doradx.github.io/LongRiver/about/

The browser bundle is generated from the monthly `LongRiver.json` snapshots.
It keeps the latest year of observations in per-station JSON files, while the
raw CSV/JSON archive remains the repository's source data.

To build locally, run `npm install` and `npm run build` from `site/`, then run
`python site/scripts/build_site_data.py --output .codex/outputs/pages/data`
from the repository root.

Read https://xirtam.cxumol.com/long-river-station-data-get-plot/ for technical description in Chinese.
         
