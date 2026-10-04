"""Render web/lookvest_explorer.html - a searchable, Lookvest-branded view of the bank."""

import csv
import json

from .build import CATEGORY_ORDER, OUT_CSV, ROOT
from .fields import ANSWER_SCHEMAS

TEMPLATE = ROOT / "lookvest_qbank" / "explorer_template.html"
OUT = ROOT / "web" / "lookvest_explorer.html"


def main() -> None:
    rows = list(csv.DictReader(OUT_CSV.open(encoding="utf-8")))
    cats = [c for c in CATEGORY_ORDER if any(r["category"] == c for r in rows)]
    ents = sorted({r["answer_entity"] for r in rows})
    subs = sorted({r["subcategory"] for r in rows})
    cad = sorted({r["refresh_cadence"] for r in rows})
    data = {
        "cats": cats, "ents": ents, "subs": subs, "cad": cad,
        "fields": {e: ANSWER_SCHEMAS[e][1] for e in ents},
        "rows": [[r["question_id"], r["question"], cats.index(r["category"]),
                  subs.index(r["subcategory"]), ents.index(r["answer_entity"]),
                  cad.index(r["refresh_cadence"]), r["market_tier"] or "",
                  1 if r["required"] == "True" else 0] for r in rows],
    }
    html = TEMPLATE.read_text().replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":")))
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html)
    print(f"Wrote {OUT} ({OUT.stat().st_size / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
