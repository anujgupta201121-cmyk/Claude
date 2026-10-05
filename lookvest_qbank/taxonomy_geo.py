"""
Country- and state-level questions.

Banks, carriers, insurers and delivery apps are national businesses, so the
consensus answer differs by country (or by US state for insurance, solar,
colleges) rather than by city. Tracking them per city would duplicate the same
answer 1,000 times.
"""

from __future__ import annotations

from typing import Iterator

from .taxonomy import q

COUNTRIES = ["Canada", "the UK", "Germany", "France", "Italy", "Spain", "the Netherlands", "Belgium",
             "Switzerland", "Austria", "Sweden", "Norway", "Denmark", "Finland", "Ireland", "Portugal",
             "Poland", "the Czech Republic", "Greece", "Turkey", "Israel", "the UAE", "Saudi Arabia",
             "Qatar", "Egypt", "South Africa", "Nigeria", "Kenya", "India", "Pakistan", "Bangladesh",
             "China", "Japan", "South Korea", "Taiwan", "Hong Kong", "Singapore", "Malaysia", "Thailand",
             "Vietnam", "Indonesia", "the Philippines", "Australia", "New Zealand", "Mexico", "Brazil",
             "Argentina", "Chile", "Colombia", "Peru"]

# (template, category, subcategory, entity, priority, monetization)
COUNTRY_FAMILIES = [
    ("What is the best bank in {c}?", "Finance", "banking_by_country", "financial_product", 84, "lead_gen_cpa"),
    ("What is the best credit card in {c}?", "Finance", "credit_cards_by_country", "financial_product", 84, "lead_gen_cpa"),
    ("What is the best investing app in {c}?", "Finance", "investing_by_country", "financial_product", 80, "lead_gen_cpa"),
    ("What is the best car insurance in {c}?", "Finance", "insurance_by_country", "financial_product", 82, "lead_gen_cpa"),
    ("What is the best health insurance in {c}?", "Finance", "insurance_by_country", "financial_product", 80, "lead_gen_cpa"),
    ("What is the best mobile carrier in {c}?", "Consumer Services", "telecom_by_country", "service_provider", 82, "lead_gen_cpa"),
    ("What is the best internet provider in {c}?", "Consumer Services", "telecom_by_country", "service_provider", 80, "lead_gen_cpa"),
    ("What is the best online shopping site in {c}?", "Products", "retailers_by_country", "service_provider", 84, "affiliate_retail"),
    ("What is the best food delivery app in {c}?", "Consumer Services", "delivery_by_country", "service_provider", 80, "delivery_commission"),
    ("What is the best ride-hailing app in {c}?", "Consumer Services", "mobility_by_country", "service_provider", 76, "cpa_affiliate"),
    ("What is the best streaming service in {c}?", "Entertainment", "streaming_by_country", "service_provider", 80, "streaming_affiliate"),
    ("What is the best dating app in {c}?", "Romance & Dating", "dating_by_country", "service_provider", 80, "subscription_affiliate"),
    ("What is the best university in {c}?", "Education & Careers", "universities_by_country", "institution", 76, "lead_gen_cpa"),
    ("What is the best hospital in {c}?", "Medical", "hospitals_by_country", "institution", 74, "patient_lead_gen"),
    ("What is the best place to visit in {c}?", "Travel", "destinations_by_country", "destination", 82, "booking_commission"),
]

US_STATES = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
             "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas",
             "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
             "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey",
             "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
             "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah",
             "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]

STATE_FAMILIES = [
    ("What is the best car insurance in {s}?", "Finance", "insurance_by_state", "financial_product", 86, "lead_gen_cpa"),
    ("What is the best homeowners insurance in {s}?", "Finance", "insurance_by_state", "financial_product", 84, "lead_gen_cpa"),
    ("What is the best health insurance in {s}?", "Finance", "insurance_by_state", "financial_product", 82, "lead_gen_cpa"),
    ("What is the best solar company in {s}?", "Home Improvement", "solar_by_state", "service_provider", 80, "lead_gen_cpa"),
    ("What is the best place to live in {s}?", "Real Estate & Living", "where_to_live_by_state", "place_to_live", 80, "real_estate_lead_gen"),
    ("What is the best place to retire in {s}?", "Aging & Senior Care", "retire_by_state", "place_to_live", 78, "real_estate_lead_gen"),
    ("What is the best college in {s}?", "Education & Careers", "colleges_by_state", "institution", 78, "lead_gen_cpa"),
    ("What is the best hospital in {s}?", "Medical", "hospitals_by_state", "institution", 76, "patient_lead_gen"),
    ("What is the best vacation spot in {s}?", "Travel", "destinations_by_state", "destination", 80, "booking_commission"),
]


def gen_geo() -> Iterator[dict]:
    for tmpl, cat, sub, ent, base, money in COUNTRY_FAMILIES:
        for c in COUNTRIES:
            yield q(tmpl.format(c=c), category=cat, subcategory=sub, family=tmpl, entity=ent,
                    priority=base, monetization=money, cadence="quarterly", geo_scope="country",
                    market=c.removeprefix("the "))
    for tmpl, cat, sub, ent, base, money in STATE_FAMILIES:
        for s in US_STATES:
            yield q(tmpl.format(s=s), category=cat, subcategory=sub, family=tmpl, entity=ent,
                    priority=base, monetization=money, cadence="quarterly", geo_scope="state",
                    market=s, country_code="US")
