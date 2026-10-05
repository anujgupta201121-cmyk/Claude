# Lookvest: LLM Consensus Question Bank

There are 10,000 questions here that consumers ask AI assistants, where the answer sends money to a specific business. Lookvest asks every question to each LLM, pulls the named business, product or title out of the answer along with where to buy or book it, and tracks the **consensus answer** over time.

| Question | What Lookvest extracts |
|---|---|
| What is the best hotel in Boston, MA? | hotel_name, brand, neighborhood, price_band, **booking_source**, booking_url |
| What should I buy a 10-year-old boy as a gift? | product_name, brand, gift_category, price, **retailer**, product_url |
| What restaurant should I eat at in Austin, TX? | restaurant_name, cuisine, neighborhood, **reservation_source**, reservation_url |
| What clothes are in style right now? | item, **brand_manufacturer**, style_trend, price, **retailer**, product_url |
| What types of foods should I eat to lose weight? | foods, food_group, key_nutrient, reasoning_source |
| What should I watch on streaming right now? | title, format, genre, **streaming_service**, where_to_watch_url |
| What is the best PC to buy? | product_name, brand, **model**, price, **retailer**, product_url |

## What's in the 10,000

| Vertical | Count | Expands over |
|---|---:|---|
| Local | 4,150 | Best hotel + restaurant in all **1,000 markets**; luxury/budget hotel, things to do, where to stay and brunch in the top 250; family and romantic hotels, date-night restaurant, steakhouse, pizza, sushi, rooftop bar, spa and wedding venue in the top 100 |
| Local Services | 389 | Realtor, injury lawyer, dentist, plastic surgeon, med spa, HVAC, roofer, plumber, movers, dealerships in the top 40 US metros |
| Products | 1,074 | ~400 product categories × budget, use case and price point, plus the best shopping site in 50 countries |
| Finance | 523 | Cards, banks, investing, lending, insurance; bank/card/insurance by country; car, home and health insurance by US state |
| Medical | 496 | 90 conditions × best treatment / OTC medicine / home remedy or Rx / online care; kids and pregnancy treatments; procedures and providers; hospitals by specialty, state and country |
| Gifts | 478 | Newborn to 17 × boy/girl × any/birthday/Christmas × budget; adults by decade × gender; recipients × occasions; interests |
| Entertainment | 341 | Streaming by service, genre, format and audience; books, podcasts, games; streaming service by country |
| Consumer Services | 273 | National services plus mobile carrier, internet, food delivery and ride-hailing by country |
| Travel | 261 | Airlines, hotel brands, cruises, destinations by type/month/region, best place to visit by country and US state |
| Parenting | 259 | Books, educational toys, apps, activities, party ideas, bikes, board games and phones by child age; homeschool and tutoring by grade; help for specific needs (ADHD, anxiety, dyslexia...); baby and kid products |
| Software & B2B | 255 | 85 software categories × best / small business / free |
| Health & Nutrition | 217 | Foods to eat and avoid for 45 goals, diets, healthiest picks, supplements, programs |
| Fashion | 205 | What's in style by audience, trending items, season × age, occasion outfits, best brands |
| Education & Careers | 186 | Colleges by major, programs, careers; best university by country; best college by US state |
| Romance & Dating | 174 | Dating apps by audience and country, matchmaking, couples therapy, date ideas, romantic getaways by month and occasion, love-language gifts, romantic watches |
| Autos | 164 | 35 vehicle segments × new / used / most reliable / lease, plus by price |
| Food & Beverage | 104 | Chains, brands, wine by varietal, spirits, what to order |
| Home Improvement | 97 | Materials and brands (roofing, windows, flooring, HVAC, solar), remodel ideas, solar company by US state |
| Aging & Senior Care | 81 | Medical alerts, stair lifts, senior living, in-home care; best place to retire by US state |
| Sexual Wellness (18+) | 80 | Toys, lubricants, condoms, lingerie, ED/libido/menopause treatments, STI tests, birth control, sex therapy |
| Real Estate & Living | 75 | Best place to live in the US for different needs and in each state; best country to live in |
| Weddings | 41 | Dresses, suits, bands, invitations, planners, seasonal ideas, bachelor/bachelorette trips |
| Legal | 35 | LLC formation, wills, trusts, divorce, immigration, injury and employment lawyers |
| Betting & Gaming (21+) | 22 | Sportsbooks, DFS, online casinos, poker, prediction markets |
| Pets | 20 | Best dog and cat breeds |

Near-duplicate local questions were removed: "tour or experience" overlapped "things to do", "fine dining" overlapped the main restaurant and date-night questions, and "nightclub" overlapped "rooftop bar". Businesses that operate nationally (banks, carriers, insurers, delivery apps) are asked once per country or US state rather than once per city.

Each row has: `question_id`, `question`, `category`, `subcategory`, `family` (the template), `priority`, `required`, `answer_entity`, `primary_answer_field`, `answer_fields`, `monetization`, `refresh_cadence`, the dimension columns (`market`, `market_rank`, `market_tier`, `country_code`, `age_group`, `gender`, `recipient`, `occasion`, `budget`, `use_case`, `product_category`, `brand`) and `question_hash`, which is a stable join key that survives rebuilds.

## Files

```
data/lookvest_question_bank.csv    # the 10,000 questions (also .jsonl)
data/markets_top1000.csv           # the 1,000 markets with rank, tier, country, lat/lon
data/summary.json                  # counts by category / family / entity / cadence
sql/snowflake_lookvest.sql         # tables + consensus and share-of-voice views
web/lookvest_explorer.html         # searchable browser for the bank
lookvest_qbank/                    # generator: markets, taxonomy*.py (core, life-stage, country/state), answer schemas, build
```

## Rebuild or resize

```bash
pip install requests
python -m lookvest_qbank.markets             # refresh the 1,000 markets from GeoNames
python -m lookvest_qbank.build               # 10,000 questions
python -m lookvest_qbank.build --limit 25000 # or any size; lowest-priority rows are trimmed first
python -m lookvest_qbank.explorer            # regenerate the HTML explorer
```

To add a question family, add a template to `lookvest_qbank/taxonomy.py`, `taxonomy_life.py` or `taxonomy_geo.py`. To add an answer type, add an entry to `lookvest_qbank/fields.py`.

**How markets are chosen:** the list is built from GeoNames (CC BY 4.0). It starts with about 195 curated travel and commerce hubs (NYC, Paris, Cancun, Aspen, Santorini and similar), then the US is filled to 250 markets by population. The rest of the world is filled by population, with a cap of 25 markets per country (45 for China and India). Suburbs within 30 km of a 1M+ city are merged into that city. Tiers are T1 (ranks 1 to 100), T2 (101 to 250) and T3 (251 to 1,000).

## Load into Snowflake / Databricks

Snowflake: run `sql/snowflake_lookvest.sql`, then `PUT` and `COPY INTO QUESTION_BANK`. `V_CONSENSUS_DAILY` returns the top pick for each question each day, with the share of models that agree. `V_SHARE_OF_VOICE` shows how often each brand or business is recommended.

Databricks:

```python
qb = (spark.read.option("header", True).option("inferSchema", True)
      .csv("/Volumes/lookvest/consensus/raw/lookvest_question_bank.csv"))
qb.write.mode("overwrite").saveAsTable("lookvest.consensus.question_bank")
```
