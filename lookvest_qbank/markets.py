"""
Lookvest market universe: the top 1,000 global markets.

Built from GeoNames `cities1000` (CC BY 4.0, https://www.geonames.org) so the
list is reproducible rather than hand-typed. Ranking logic:

1. Curated anchors   - global travel / commerce hubs that drive hotel, dining
                       and retail demand regardless of raw population.
2. US metros         - top US cities by population (Lookvest's primary market),
                       filled until the US holds `US_SLOTS` markets.
3. Rest of world     - remaining slots by population, with a per-country cap so
                       the list stays global instead of 40% China/India.

Run `python -m lookvest_qbank.markets` to rebuild data/markets_top1000.csv.
"""

from __future__ import annotations

import csv
import io
import math
import zipfile
from pathlib import Path

import requests

GEONAMES_CITIES = "https://download.geonames.org/export/dump/cities1000.zip"
CITIES_FILE = "cities1000.txt"
GEONAMES_COUNTRIES = "https://download.geonames.org/export/dump/countryInfo.txt"

ROOT = Path(__file__).resolve().parent.parent
MARKETS_CSV = ROOT / "data" / "markets_top1000.csv"

TOTAL_MARKETS = 1000
US_SLOTS = 250
COUNTRY_CAP = {"CN": 45, "IN": 45}
DEFAULT_COUNTRY_CAP = 25

# Feature codes that are neighbourhoods / historical, not markets.
EXCLUDED_FEATURES = {"PPLX", "PPLH", "PPLW", "PPLQ"}
# NYC boroughs are listed separately in GeoNames; NYC itself covers them.
EXCLUDED_NAMES = {("US", "Brooklyn"), ("US", "Queens"), ("US", "Manhattan"),
                  ("US", "The Bronx"), ("US", "Staten Island"),
                  ("HK", "Victoria"), ("HK", "Kowloon"),
                  ("JP", "Aihara")}  # GeoNames carries Sagamihara's population on this district

# (GeoNames ascii name, country code[, US state]) in priority order.
ANCHORS: list[tuple] = [
    ("New York City", "US", "NY"), ("London", "GB"), ("Paris", "FR"), ("Tokyo", "JP"),
    ("Dubai", "AE"), ("Los Angeles", "US", "CA"), ("Las Vegas", "US", "NV"),
    ("Orlando", "US", "FL"), ("Miami", "US", "FL"), ("Chicago", "US", "IL"),
    ("San Francisco", "US", "CA"), ("Singapore", "SG"), ("Bangkok", "TH"),
    ("Hong Kong", "HK"), ("Barcelona", "ES"), ("Rome", "IT"), ("Istanbul", "TR"),
    ("Amsterdam", "NL"), ("Toronto", "CA"), ("Sydney", "AU"), ("Mexico City", "MX"),
    ("Cancun", "MX"), ("Boston", "US", "MA"), ("Washington", "US", "DC"),
    ("Seattle", "US", "WA"), ("Austin", "US", "TX"), ("Nashville", "US", "TN"),
    ("New Orleans", "US", "LA"), ("San Diego", "US", "CA"), ("Honolulu", "US", "HI"),
    ("Atlanta", "US", "GA"), ("Dallas", "US", "TX"), ("Houston", "US", "TX"),
    ("Denver", "US", "CO"), ("Phoenix", "US", "AZ"), ("Philadelphia", "US", "PA"),
    ("Madrid", "ES"), ("Berlin", "DE"), ("Munich", "DE"), ("Vienna", "AT"),
    ("Prague", "CZ"), ("Lisbon", "PT"), ("Milan", "IT"), ("Florence", "IT"),
    ("Venice", "IT"), ("Athens", "GR"), ("Dublin", "IE"), ("Edinburgh", "GB"),
    ("Zuerich", "CH"), ("Geneva", "CH"), ("Copenhagen", "DK"), ("Stockholm", "SE"),
    ("Oslo", "NO"), ("Helsinki", "FI"), ("Budapest", "HU"), ("Warsaw", "PL"),
    ("Krakow", "PL"), ("Brussels", "BE"), ("Nice", "FR"), ("Seoul", "KR"),
    ("Osaka", "JP"), ("Kyoto", "JP"), ("Shanghai", "CN"), ("Beijing", "CN"),
    ("Taipei", "TW"), ("Kuala Lumpur", "MY"), ("Ubud", "ID"), ("Denpasar", "ID"),
    ("Jakarta", "ID"), ("Manila", "PH"), ("Ho Chi Minh City", "VN"), ("Hanoi", "VN"),
    ("Phuket", "TH"), ("Mumbai", "IN"), ("New Delhi", "IN"), ("Bengaluru", "IN"),
    ("Abu Dhabi", "AE"), ("Doha", "QA"), ("Riyadh", "SA"), ("Tel Aviv", "IL"),
    ("Cairo", "EG"), ("Marrakesh", "MA"), ("Cape Town", "ZA"), ("Johannesburg", "ZA"),
    ("Nairobi", "KE"), ("Lagos", "NG"), ("Melbourne", "AU"), ("Brisbane", "AU"),
    ("Auckland", "NZ"), ("Vancouver", "CA"), ("Montreal", "CA"), ("Calgary", "CA"),
    ("Sao Paulo", "BR"), ("Rio de Janeiro", "BR"), ("Buenos Aires", "AR"),
    ("Lima", "PE"), ("Bogota", "CO"), ("Medellin", "CO"), ("Cartagena", "CO"),
    ("Santiago", "CL"), ("Punta Cana", "DO"), ("San Juan", "PR"), ("Havana", "CU"),
    ("Playa del Carmen", "MX"), ("Tulum", "MX"), ("Puerto Vallarta", "MX"),
    ("Cabo San Lucas", "MX"), ("Guadalajara", "MX"), ("Monterrey", "MX"),
    ("Charleston", "US", "SC"), ("Savannah", "US", "GA"), ("Scottsdale", "US", "AZ"),
    ("Palm Springs", "US", "CA"), ("Napa", "US", "CA"), ("Key West", "US", "FL"),
    ("Miami Beach", "US", "FL"), ("Fort Lauderdale", "US", "FL"), ("Tampa", "US", "FL"),
    ("Charlotte", "US", "NC"), ("Minneapolis", "US", "MN"), ("Portland", "US", "OR"),
    ("Salt Lake City", "US", "UT"), ("San Antonio", "US", "TX"),
    ("Kansas City", "US", "MO"), ("St. Louis", "US", "MO"), ("Pittsburgh", "US", "PA"),
    ("Baltimore", "US", "MD"), ("Detroit", "US", "MI"), ("Cleveland", "US", "OH"),
    ("Columbus", "US", "OH"), ("Indianapolis", "US", "IN"), ("Raleigh", "US", "NC"),
    ("Sacramento", "US", "CA"), ("San Jose", "US", "CA"), ("Anchorage", "US", "AK"),
    ("Asheville", "US", "NC"), ("Sedona", "US", "AZ"), ("Aspen", "US", "CO"),
    ("Park City", "US", "UT"), ("Myrtle Beach", "US", "SC"), ("Branson", "US", "MO"),
    ("Gatlinburg", "US", "TN"), ("South Lake Tahoe", "US", "CA"),
    ("Santa Barbara", "US", "CA"), ("Santa Fe", "US", "NM"), ("Newport", "US", "RI"),
    ("Bar Harbor", "US", "ME"), ("Portland", "US", "ME"), ("Nantucket", "US", "MA"),
    ("Jackson", "US", "WY"), ("Kailua-Kona", "US", "HI"), ("Lahaina", "US", "HI"),
    ("Kahului", "US", "HI"), ("Reykjavik", "IS"), ("Dubrovnik", "HR"), ("Split", "HR"),
    ("Fira", "GR"), ("Mykonos", "GR"), ("Sevilla", "ES"), ("Valencia", "ES"),
    ("Malaga", "ES"), ("Palma", "ES"), ("Porto", "PT"), ("Lyon", "FR"),
    ("Marseille", "FR"), ("Naples", "IT"), ("Salzburg", "AT"), ("Brugge", "BE"),
    ("Manchester", "GB"), ("Liverpool", "GB"), ("Hamburg", "DE"), ("Frankfurt am Main", "DE"),
    ("Male", "MV"), ("Colombo", "LK"), ("Kathmandu", "NP"),
    ("Chiang Mai", "TH"), ("Siem Reap", "KH"), ("Da Nang", "VN"), ("Fukuoka", "JP"),
    ("Sapporo", "JP"), ("Busan", "KR"), ("Macau", "MO"), ("Queenstown", "NZ"),
    ("Gold Coast", "AU"), ("Perth", "AU"), ("Quebec", "CA"), ("Whistler", "CA"),
    ("Banff", "CA"), ("Nassau", "BS"), ("Montego Bay", "JM"),
    ("Oranjestad", "AW"), ("Bridgetown", "BB"), ("Zanzibar", "TZ"),
    ("Port Louis", "MU"), ("Victoria", "SC"),
]

# GeoNames ascii names -> how travellers actually search for the market.
DISPLAY_NAMES = {("Zuerich", "CH"): "Zurich", ("Sevilla", "ES"): "Seville",
                 ("Brugge", "BE"): "Bruges", ("Fira", "GR"): "Santorini",
                 ("Ubud", "ID"): "Bali (Ubud)", ("Frankfurt am Main", "DE"): "Frankfurt",
                 ("Washington", "US"): "Washington"}

# Only anchors may come from towns under this size; the population fill may not.
MIN_FILL_POPULATION = 15000

# Outside the US, a city within this radius of an already-selected 1M+ city is
# treated as part of that metro (Pudong -> Shanghai, Thane -> Mumbai) and skipped.
METRO_RADIUS_KM = 30
METRO_CORE_POPULATION = 1_000_000


def _km(a: dict, b: dict) -> float:
    lat1, lon1, lat2, lon2 = map(math.radians, (float(a["lat"]), float(a["lon"]),
                                                float(b["lat"]), float(b["lon"])))
    h = (math.sin((lat2 - lat1) / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2)
    return 6371 * 2 * math.asin(math.sqrt(h))

CSV_FIELDS = ["market_rank", "market_tier", "market_name", "market_label",
              "admin1", "country_code", "country_name", "continent",
              "population", "latitude", "longitude", "geonameid", "source"]


def _download_rows() -> tuple[list[list[str]], dict[str, tuple[str, str]]]:
    zbytes = requests.get(GEONAMES_CITIES, timeout=120).content
    with zipfile.ZipFile(io.BytesIO(zbytes)) as zf:
        text = zf.read(CITIES_FILE).decode("utf-8")
    rows = [line.split("\t") for line in text.splitlines() if line]

    countries = {}
    for line in requests.get(GEONAMES_COUNTRIES, timeout=60).text.splitlines():
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split("\t")
        countries[parts[0]] = (parts[4], parts[8])  # name, continent
    return rows, countries


def build_markets(total: int = TOTAL_MARKETS) -> list[dict]:
    rows, countries = _download_rows()

    # GeoNames columns: 0 id, 2 asciiname, 4 lat, 5 lon, 7 feature, 8 cc, 10 admin1, 14 pop
    cities = []
    for r in rows:
        if r[7] in EXCLUDED_FEATURES or (r[8], r[2]) in EXCLUDED_NAMES:
            continue
        cities.append({"geonameid": r[0], "name": r[2], "lat": r[4], "lon": r[5],
                       "cc": r[8], "admin1": r[10], "pop": int(r[14] or 0)})
    cities.sort(key=lambda c: -c["pop"])

    # Largest entry per (name, country, admin1) wins; Portland OR vs ME stay distinct.
    by_key: dict[tuple, dict] = {}
    for c in cities:
        by_key.setdefault((c["name"], c["cc"], c["admin1"] if c["cc"] == "US" else ""), c)
    cities = list(by_key.values())
    cities.sort(key=lambda c: -c["pop"])

    selected: list[tuple[dict, str]] = []
    seen: set[str] = set()

    def add(city: dict, source: str) -> None:
        if city["geonameid"] not in seen:
            seen.add(city["geonameid"])
            selected.append((city, source))

    for anchor in ANCHORS:
        name, cc = anchor[0], anchor[1]
        state = anchor[2] if len(anchor) > 2 else None
        match = next((c for c in cities if c["name"] == name and c["cc"] == cc
                      and (state is None or c["admin1"] == state)), None)
        if match:
            add(match, "anchor")

    us_count = sum(1 for c, _ in selected if c["cc"] == "US")
    for c in cities:
        if us_count >= US_SLOTS:
            break
        if c["pop"] < MIN_FILL_POPULATION:
            break
        if c["cc"] == "US" and c["geonameid"] not in seen:
            add(c, "us_population")
            us_count += 1

    per_country: dict[str, int] = {}
    for c, _ in selected:
        per_country[c["cc"]] = per_country.get(c["cc"], 0) + 1
    for c in cities:
        if len(selected) >= total or c["pop"] < MIN_FILL_POPULATION:
            break
        if c["cc"] == "US" or c["geonameid"] in seen:
            continue
        cap = COUNTRY_CAP.get(c["cc"], DEFAULT_COUNTRY_CAP)
        if per_country.get(c["cc"], 0) >= cap:
            continue
        if any(s["cc"] == c["cc"] and s["pop"] >= METRO_CORE_POPULATION
               and _km(s, c) < METRO_RADIUS_KM for s, _ in selected):
            continue
        add(c, "global_population")
        per_country[c["cc"]] = per_country.get(c["cc"], 0) + 1

    # Anchors keep their curated order; everything else ranks by population.
    anchors = [s for s in selected if s[1] == "anchor"]
    rest = sorted((s for s in selected if s[1] != "anchor"), key=lambda s: -s[0]["pop"])

    markets = []
    for rank, (c, source) in enumerate(anchors + rest, start=1):
        country_name, continent = countries.get(c["cc"], (c["cc"], ""))
        name = DISPLAY_NAMES.get((c["name"], c["cc"]), c["name"])
        label = f'{name}, {c["admin1"]}' if c["cc"] == "US" else f'{name}, {country_name}'
        markets.append({
            "market_rank": rank,
            "market_tier": "T1" if rank <= 100 else "T2" if rank <= 250 else "T3",
            "market_name": name, "market_label": label,
            "admin1": c["admin1"], "country_code": c["cc"],
            "country_name": country_name, "continent": continent,
            "population": c["pop"], "latitude": c["lat"], "longitude": c["lon"],
            "geonameid": c["geonameid"], "source": source,
        })
    return markets


def write_markets(markets: list[dict], path: Path = MARKETS_CSV) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(markets)


def load_markets(path: Path = MARKETS_CSV) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["market_rank"] = int(r["market_rank"])
    return rows


if __name__ == "__main__":
    m = build_markets()
    write_markets(m)
    print(f"Wrote {len(m)} markets -> {MARKETS_CSV}")
