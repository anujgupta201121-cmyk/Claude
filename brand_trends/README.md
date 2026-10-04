# Lookvest · Brand Radar

Brand keywords for spotting **launch-driven virality** on Google Trends, TikTok Creative Center and Pinterest Trends.
The brands are grouped into **competitor sets**, so each brand is always compared with its direct rivals.

| File | What it is |
|---|---|
| `brand_keywords_core.csv` | **The 1,000-keyword core list.** Columns: keyword, industry, competitor_set, set_rank, tier |
| `brand_keywords_all.csv` | Core list plus an extended tier of challenger and niche brands (2,270 unique) |
| `google_trends_batches.json` | Core sets split into groups of 5 terms, each repeating the set leader as an anchor |
| `lookvest_brand_radar.html` | A page to search the list and copy keywords or Google Trends batches |
| `brand_keywords.py` | Source of truth. Edit `BRANDS` here, then run `python brand_keywords.py` to rebuild every file |

**15 industries / 83 competitor sets:** Restaurants · Snacks, Food & Beverage CPG · Retailers · E-commerce & Marketplaces ·
Apparel & Footwear · Luxury & Fashion Houses · Beauty, Fragrance & Personal Care · Toys, Kids & Collectibles ·
Consumer Electronics (incl. smartphones) · PC Hardware & Gaming Hardware · AI Agents & AI Products · Hotels & Travel ·
Entertainment & Experiences · Automotive & Mobility · Financial & Consumer Apps.

## Using it

- **Google Trends** compares at most 5 terms at once. Keep the anchor term in every batch and rescale the
  scores by the anchor so the batches can be combined.
- **TikTok / Pinterest:** add launch words from `LAUNCH_MODIFIERS` to a brand name (`new`, `drop`,
  `restock`, `dupe`, `release date`, `sold out`, ...).
- **A virality signal:** a brand's share of its competitor set rising more than 2× its 90-day baseline
  within 7–14 days of a product launch.

```python
from brand_keywords import trends_batches
for b in trends_batches():            # tier="core" by default; tier=None for everything
    print(b["competitor_set"], b["terms"])
```
