# Lookvest · Brand Radar

Brand keywords for spotting **launch-driven virality** on Google Trends, TikTok Creative Center and Pinterest Trends.
The brands are grouped into **competitor sets**, so each brand is always compared with its direct rivals.

| File | What it is |
|---|---|
| `brand_keywords_core.csv` | **The 1,000-keyword core list**, with the exact keyword to paste into each platform (columns below) |
| `brand_keywords_all.csv` | Core list plus an extended tier of challenger and niche brands (2,266 unique) |
| `google_trends_batches.json` | Core sets as groups of 5 Google Trends keywords, each repeating the set leader as an anchor |
| `lookvest_brand_radar.html` | A page to search the list. Switch between Brand, Google, Pinterest and TikTok to see and copy each platform's keyword |
| `brand_keywords.py` | Source of truth. Edit `BRANDS` here, then run `python brand_keywords.py` to rebuild every file |

**15 industries / 83 competitor sets:** Restaurants · Snacks, Food & Beverage CPG · Retailers · E-commerce & Marketplaces ·
Apparel & Footwear · Luxury & Fashion Houses · Beauty, Fragrance & Personal Care · Toys, Kids & Collectibles ·
Consumer Electronics (incl. smartphones) · PC Hardware & Gaming Hardware · AI Agents & AI Products · Hotels & Travel ·
Entertainment & Experiences · Automotive & Mobility · Financial & Consumer Apps.

## Keyword columns

| Column | Use it in | Rule |
|---|---|---|
| `keyword` | (display) | Brand as written, e.g. `Chick-fil-A`, `Disney+`, `M&M's` |
| `google_trends_keyword` | Google Trends | Lowercase, accents and punctuation removed: `chick fil a`, `disney plus`, `mms`, `bath and body works`, `att`, `elf`, `pf changs` |
| `needs_topic` | Google Trends | `True` means the name alone is ambiguous (Ring, Claude, Delta, Stanley...), so pick the brand's **Topic** in the dropdown |
| `pinterest_keyword` | Pinterest Trends | Same as Google, but ambiguous names get a qualifier: `ring doorbell`, `claude ai`, `delta airlines`, `stanley tumbler` |
| `tiktok_hashtag` | TikTok Creative Center | The Pinterest keyword with spaces removed, without `#`: `ringdoorbell`, `claudeai`, `chickfila` |

The punctuation rules are in `clean_keyword()`. Qualifiers are in `QUALIFIED`, platform-wide spelling fixes in
`SEARCH_NAME`, and hashtag exceptions in `TIKTOK_HASHTAG`. The build checks that no two brands end up with the
same keyword on any platform.

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
