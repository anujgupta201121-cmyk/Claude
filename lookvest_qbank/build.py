"""
Build the Lookvest question bank.

    python -m lookvest_qbank.build                 # 10,000 questions (default)
    python -m lookvest_qbank.build --limit 25000   # larger bank

Writes data/lookvest_question_bank.csv (+ .jsonl) and data/summary.json.
Required families (hotel + restaurant for all 1,000 markets, core gift / product /
fashion / streaming / nutrition questions) are always kept; the remaining slots
go to the highest-priority questions.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter

from .markets import MARKETS_CSV, ROOT, build_markets, load_markets, write_markets
from .taxonomy import generate_all

OUT_CSV = ROOT / "data" / "lookvest_question_bank.csv"
OUT_JSONL = ROOT / "data" / "lookvest_question_bank.jsonl"
SUMMARY = ROOT / "data" / "summary.json"

DIMENSIONS = ["geo_scope", "market", "market_rank", "market_tier", "country_code", "continent",
              "age_group", "gender", "recipient", "occasion", "budget", "use_case",
              "product_category", "brand"]
COLUMNS = (["question_id", "question", "category", "subcategory", "family", "priority",
            "required", "answer_entity", "primary_answer_field", "answer_fields",
            "monetization", "refresh_cadence"] + DIMENSIONS + ["question_hash"])

CATEGORY_ORDER = ["Local", "Local Services", "Gifts", "Products", "Fashion", "Health & Nutrition",
                  "Entertainment", "Finance", "Travel", "Autos", "Software & B2B",
                  "Consumer Services", "Education & Careers", "Food & Beverage", "Pets",
                  "Real Estate & Living", "Romance & Dating",
                  "Sexual Wellness", "Parenting", "Medical", "Weddings", "Aging & Senior Care",
                  "Home Improvement", "Legal", "Betting & Gaming"]


def build(limit: int) -> list[dict]:
    if not MARKETS_CSV.exists():
        write_markets(build_markets())
    markets = load_markets()

    seen: set[str] = set()
    rows = []
    for row in generate_all(markets):
        key = row["question"].strip().lower()
        if key in seen:
            continue
        seen.add(key)
        rows.append(row)

    required = [r for r in rows if r["required"]]
    optional = sorted((r for r in rows if not r["required"]),
                      key=lambda r: (-r["priority"], r.get("market_rank") or 0))
    if len(required) > limit:
        raise SystemExit(f"{len(required)} required questions exceed --limit {limit}")
    kept = required + optional[: limit - len(required)]

    kept.sort(key=lambda r: (CATEGORY_ORDER.index(r["category"]), r["subcategory"],
                             r.get("market_rank") or 0, -r["priority"], r["question"]))
    for i, r in enumerate(kept, start=1):
        r["question_id"] = f"LV-{i:05d}"
        # Stable across rebuilds even if ordering changes - use this as the join key.
        r["question_hash"] = hashlib.sha1(r["question"].encode()).hexdigest()[:12]
    print(f"Generated {len(rows):,} candidate questions; kept {len(kept):,} "
          f"({len(required):,} required).")
    return kept


def write(rows: list[dict]) -> None:
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in COLUMNS})
    with OUT_JSONL.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps({c: r.get(c) for c in COLUMNS if r.get(c) not in (None, "")}) + "\n")

    summary = {
        "total": len(rows),
        "by_category": Counter(r["category"] for r in rows),
        "by_family": Counter(r["family"] for r in rows),
        "by_entity": Counter(r["answer_entity"] for r in rows),
        "by_cadence": Counter(r["refresh_cadence"] for r in rows),
        "by_monetization": Counter(r["monetization"] for r in rows),
        "markets_covered": len({r["market"] for r in rows if r.get("geo_scope") == "local"}),
        "by_geo_scope": Counter(r["geo_scope"] for r in rows),
    }
    SUMMARY.write_text(json.dumps(summary, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--limit", type=int, default=10_000)
    args = ap.parse_args()
    rows = build(args.limit)
    write(rows)
    print(json.dumps(json.loads(SUMMARY.read_text())["by_category"], indent=2))


if __name__ == "__main__":
    main()
