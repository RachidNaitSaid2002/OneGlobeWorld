# ONE GLOBE — live ranking page

Interactive 3D globe for @oneglobe.world: spin and zoom the Earth, tap a country to see its follower votes, search, and browse the full ranking.

## Run it locally
The page loads its data with `fetch`, so open it through a small web server (not by double-clicking the file):

```bash
cd oneglobe-web
python3 -m http.server 8000
# open http://localhost:8000
```

## Put it online
It is a static site: upload the whole folder to any static host (Netlify, Vercel, Cloudflare Pages, GitHub Pages) or into a folder of your own site. No build step, no backend.

After it is online, open `index.html` and change `content="assets/og.jpg"` to the full address (`https://your-domain/assets/og.jpg`). Instagram and WhatsApp only show the link preview image with a full address.

## Links to one country
Every country has its own link: `https://your-domain/#morocco`, `#south-africa`, `#united-states` (lowercase, spaces become `-`). The page opens on that country with its card. Use these in comment replies.

## Files
| Path | What it is |
|---|---|
| `index.html` | The page (HTML, CSS and JS in one file) |
| `assets/three.min.js` | three.js r128 (bundled, so the page works without a CDN) |
| `assets/earth.jpg` | NASA Blue Marble texture used for restored countries |
| `assets/og.jpg` | Link preview image (1200×630). Re-shoot it when the globe changes a lot |
| `data/geo.json` | Country shapes (Natural Earth 1:50m; Morocco with Sahara; Israel's area shown as Palestine, Golan with Syria) |
| `data/data.json` | Votes per country per day + which day each country rose |
| `tools/update_data.py` | Rebuilds `data/data.json` from `ranking.csv` |
| `tools/detect_country.py` | Country detector used to count comments |
| `tools/build_geo.py` | Rebuilds `data/geo.json` from Natural Earth `ne_50m_admin_0_countries.geojson` with the series' map choices |
| `tools/countries_names.json` | Country names and codes used by the detector |

## Update after each reel
1. Recompute `ranking.csv` (one vote per follower per reel, first country they name).
2. Run: `python3 tools/update_data.py ../ranking.csv "" "after Day 7 (votes from Day 1-6 reels)"`
   The second argument can list risen countries as `Sweden:6,Poland:5,...`; left empty, it reads the `status` column ("risen Day N").
3. Upload `data/data.json` again.

The Day badge, the number of day bars and the tie-break follow the data on their own: nothing in `index.html` needs changing for a new Day.

## Rules shown on the page
One vote per follower per reel (the first country they name). Each day the 2 highest countries still underwater rise. Ties for 2nd place carry to the next day. Israel is not part of the series.
