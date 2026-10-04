"""
Lookvest question taxonomy.

Every family is a template plus the dimension it expands over (markets, ages x
genders, product categories ...). `generate_all()` yields the full superset;
build.py ranks it by commercial priority and keeps the top N (default 10,000).

Priority (0-100) = how much an LLM consensus answer moves revenue for the
businesses named in it. Local questions lose a little priority as market rank
falls, so trimming removes long-tail market x niche-question pairs first.
"""

from __future__ import annotations

import math
from typing import Iterator

from .fields import fields_for

# --------------------------------------------------------------------------- #
# Row helper
# --------------------------------------------------------------------------- #


def q(question: str, *, category: str, subcategory: str, family: str, entity: str,
      priority: float, monetization: str, cadence: str, required: bool = False,
      **dims) -> dict:
    primary, fields = fields_for(entity)
    return {
        "question": question, "category": category, "subcategory": subcategory,
        "family": family, "answer_entity": entity, "primary_answer_field": primary,
        "answer_fields": fields, "monetization": monetization,
        "refresh_cadence": cadence, "priority": round(priority, 2),
        "required": required, **dims,
    }


# --------------------------------------------------------------------------- #
# 1. LOCAL - markets
# --------------------------------------------------------------------------- #

# (template, subcategory, entity, base priority, monetization, cadence, max market rank, required)
LOCAL_FAMILIES = [
    # Explicitly requested: every one of the 1,000 markets.
    ("What is the best hotel in {m}?", "hotels", "hotel", 100, "booking_commission", "monthly", 1000, True),
    ("What restaurant should I eat at in {m}?", "restaurants", "restaurant", 99, "reservation_fee", "monthly", 1000, True),
    # Top 250 markets.
    ("What is the best luxury hotel in {m}?", "hotels", "hotel", 90, "booking_commission", "monthly", 250, False),
    ("What is the best budget hotel in {m}?", "hotels", "hotel", 88, "booking_commission", "monthly", 250, False),
    ("What is the best family-friendly hotel in {m}?", "hotels", "hotel", 86, "booking_commission", "monthly", 250, False),
    ("What is the best area to stay in {m}?", "hotels", "neighborhood", 85, "booking_commission", "quarterly", 250, False),
    ("What are the best things to do in {m}?", "attractions", "attraction", 87, "ticket_commission", "monthly", 250, False),
    ("What is the best tour or experience to book in {m}?", "attractions", "attraction", 82, "ticket_commission", "monthly", 250, False),
    ("What is the best steakhouse in {m}?", "restaurants", "restaurant", 80, "reservation_fee", "monthly", 250, False),
    ("What is the best pizza in {m}?", "restaurants", "restaurant", 79, "delivery_commission", "monthly", 250, False),
    ("What is the best sushi restaurant in {m}?", "restaurants", "restaurant", 78, "reservation_fee", "monthly", 250, False),
    ("Where is the best brunch in {m}?", "restaurants", "restaurant", 78, "reservation_fee", "monthly", 250, False),
    ("What is the best coffee shop in {m}?", "restaurants", "restaurant", 74, "local_ads", "monthly", 250, False),
    ("What is the best rooftop bar in {m}?", "nightlife", "bar_venue", 75, "reservation_fee", "monthly", 250, False),
    # Top 100 markets.
    ("What is the best fine dining restaurant in {m}?", "restaurants", "restaurant", 77, "reservation_fee", "monthly", 100, False),
    ("What is the most romantic restaurant in {m} for date night?", "restaurants", "restaurant", 76, "reservation_fee", "monthly", 100, False),
    ("What is the best kid-friendly restaurant in {m}?", "restaurants", "restaurant", 70, "reservation_fee", "monthly", 100, False),
    ("What is the best vegan or vegetarian restaurant in {m}?", "restaurants", "restaurant", 68, "reservation_fee", "monthly", 100, False),
    ("What is the best spa in {m}?", "wellness", "local_business", 72, "booking_commission", "quarterly", 100, False),
    ("What is the best hotel near the airport in {m}?", "hotels", "hotel", 74, "booking_commission", "quarterly", 100, False),
    ("What is the best nightclub in {m}?", "nightlife", "bar_venue", 66, "ticket_commission", "monthly", 100, False),
    ("What is the best golf course in {m}?", "attractions", "local_business", 64, "booking_commission", "quarterly", 100, False),
    ("Where is the best place to go shopping in {m}?", "shopping", "local_business", 65, "local_ads", "quarterly", 100, False),
    ("What is the best wedding venue in {m}?", "events", "local_business", 69, "lead_gen", "quarterly", 100, False),
    ("What is the best day trip from {m}?", "attractions", "attraction", 63, "ticket_commission", "quarterly", 100, False),
]

# US-only local services: high-ticket lead-gen categories, top US markets.
US_SERVICE_FAMILIES = [
    ("Who is the best real estate agent in {m}?", "real_estate", 84),
    ("What is the best neighborhood to live in {m}?", "real_estate", 80),
    ("Who is the best personal injury lawyer in {m}?", "legal", 83),
    ("Who is the best dentist in {m}?", "healthcare", 78),
    ("Who is the best plastic surgeon in {m}?", "healthcare", 77),
    ("What is the best med spa in {m}?", "healthcare", 72),
    ("What is the best hospital in {m}?", "healthcare", 75),
    ("What is the best HVAC company in {m}?", "home_services", 76),
    ("What is the best roofing company in {m}?", "home_services", 76),
    ("What is the best plumber in {m}?", "home_services", 74),
    ("What is the best moving company in {m}?", "home_services", 73),
    ("What is the best car dealership in {m}?", "auto", 74),
    ("What is the best private school in {m}?", "education", 70),
    ("What is the best gym in {m}?", "fitness", 68),
    ("What is the best hair salon in {m}?", "beauty", 66),
]
US_SERVICE_MARKETS = 60


def _market_decay(rank: int) -> float:
    # 0 at rank 1, ~8 at rank 100, ~12 at rank 1,000
    return 4.0 * math.log10(max(rank, 1)) + (4.0 if rank > 100 else 0.0)


def gen_local(markets: list[dict]) -> Iterator[dict]:
    for tmpl, sub, entity, base, money, cadence, max_rank, required in LOCAL_FAMILIES:
        for m in markets:
            if m["market_rank"] > max_rank:
                continue
            yield q(tmpl.format(m=m["market_label"]), category="Local", subcategory=sub,
                    family=tmpl, entity=entity, priority=base - _market_decay(m["market_rank"]),
                    monetization=money, cadence=cadence, required=required,
                    geo_scope="local", **_market_dims(m))

    us = [m for m in markets if m["country_code"] == "US"][:US_SERVICE_MARKETS]
    for tmpl, sub, base in US_SERVICE_FAMILIES:
        for us_rank, m in enumerate(us, start=1):
            entity = "neighborhood" if "neighborhood" in tmpl else "local_business"
            yield q(tmpl.format(m=m["market_label"]), category="Local Services", subcategory=sub,
                    family=tmpl, entity=entity, priority=base - _market_decay(us_rank * 2),
                    monetization="lead_gen", cadence="quarterly", geo_scope="local",
                    **_market_dims(m))


def _market_dims(m: dict) -> dict:
    return {"market_rank": m["market_rank"], "market_tier": m["market_tier"],
            "market": m["market_label"], "country_code": m["country_code"],
            "continent": m["continent"]}


# --------------------------------------------------------------------------- #
# 2. GIFTS - ages x genders x occasions x budgets
# --------------------------------------------------------------------------- #

KID_AGES = ["newborn"] + list(range(1, 18))
GIFT_OCCASIONS_KIDS = [("", 95), ("birthday", 92), ("Christmas", 93)]
GIFT_BUDGETS = ["$25", "$50", "$100"]
ADULT_DECADES = ["20s", "30s", "40s", "50s", "60s", "70s", "80s"]

RECIPIENT_OCCASIONS = {
    "my mom": ["birthday", "Christmas", "Mother's Day"],
    "my dad": ["birthday", "Christmas", "Father's Day", "retirement"],
    "my wife": ["birthday", "Christmas", "anniversary", "Valentine's Day", "Mother's Day", "push present"],
    "my husband": ["birthday", "Christmas", "anniversary", "Valentine's Day", "Father's Day"],
    "my girlfriend": ["birthday", "Christmas", "anniversary", "Valentine's Day"],
    "my boyfriend": ["birthday", "Christmas", "anniversary", "Valentine's Day"],
    "my grandma": ["birthday", "Christmas", "Mother's Day"],
    "my grandpa": ["birthday", "Christmas", "Father's Day"],
    "my sister": ["birthday", "Christmas"],
    "my brother": ["birthday", "Christmas"],
    "my best friend": ["birthday", "Christmas"],
    "my mother-in-law": ["birthday", "Christmas", "Mother's Day"],
    "my father-in-law": ["birthday", "Christmas", "Father's Day"],
    "a coworker": ["birthday", "Christmas", "retirement", "Secret Santa under $25", "farewell"],
    "my boss": ["birthday", "Christmas", "Boss's Day"],
    "a teacher": ["Christmas", "end of the school year", "Teacher Appreciation Week"],
    "a nurse": ["Nurses Week", "thank-you"],
    "new parents": ["baby shower", "a new baby"],
    "a couple": ["wedding", "engagement", "housewarming", "anniversary"],
    "a host": ["dinner party", "housewarming"],
    "a college graduate": ["graduation"],
    "a high school graduate": ["graduation"],
    "my son": ["birthday", "Christmas", "graduation"],
    "my daughter": ["birthday", "Christmas", "graduation"],
    "a client": ["Christmas", "thank-you"],
    "my employees": ["Christmas", "work anniversary"],
}

GIFT_INTERESTS = [
    "gamer", "golfer", "runner", "cyclist", "home cook", "coffee lover", "wine lover",
    "whiskey lover", "beer lover", "tea lover", "traveler", "gardener", "fisherman", "hunter",
    "camper", "hiker", "photographer", "music lover", "book lover", "artist", "knitter",
    "yoga lover", "fitness enthusiast", "skier", "surfer", "dog lover", "cat lover",
    "tech lover", "car enthusiast", "sports fan", "baseball fan", "football fan",
    "basketball fan", "soccer fan", "Disney fan", "Taylor Swift fan", "Star Wars fan",
    "Harry Potter fan", "LEGO fan", "anime fan", "nurse", "teacher", "doctor",
    "new homeowner", "college student", "remote worker", "someone who has everything",
    "person with anxiety", "baker", "grill master", "makeup lover", "skincare lover",
    "sneakerhead", "watch collector", "jewelry lover", "new mom", "new dad", "retiree",
]


def _kid_label(age, gender: str) -> str:
    if age == "newborn":
        return f"a newborn baby {gender}"
    return f"a {age}-year-old {gender}"


def gen_gifts() -> Iterator[dict]:
    common = dict(category="Gifts", entity="gift", monetization="affiliate_retail",
                  geo_scope="national")
    for age in KID_AGES:
        for gender in ("boy", "girl"):
            label = _kid_label(age, gender)
            age_str = "0" if age == "newborn" else str(age)
            for occasion, base in GIFT_OCCASIONS_KIDS:
                text = (f"What should I buy {label} as a gift?" if not occasion
                        else f"What is the best {occasion} gift for {label}?")
                yield q(text, subcategory="kids_by_age", family="gift_kid_age_occasion",
                        priority=base, cadence="monthly", required=not occasion,
                        age_group=age_str, gender=gender, occasion=occasion or "any", **common)
            for budget in GIFT_BUDGETS:
                yield q(f"What is the best gift under {budget} for {label}?",
                        subcategory="kids_by_age_budget", family="gift_kid_age_budget",
                        priority=84, cadence="monthly", age_group=age_str, gender=gender,
                        budget=budget, **common)
        yield q("What is the best gift for a newborn baby?"
                if age == "newborn" else f"What is the best gift for a {age}-year-old?",
                subcategory="kids_by_age", family="gift_kid_age_unisex", priority=86,
                cadence="monthly", age_group="0" if age == "newborn" else str(age),
                gender="any", **common)

    for gender, noun in (("male", "man"), ("female", "woman")):
        for decade in ADULT_DECADES:
            for occasion, base in (("", 90), ("birthday", 87), ("Christmas", 88)):
                text = (f"What is the best gift for a {noun} in their {decade}?" if not occasion
                        else f"What is the best {occasion} gift for a {noun} in their {decade}?")
                yield q(text, subcategory="adults_by_age", family="gift_adult_age_occasion",
                        priority=base, cadence="monthly", required=not occasion,
                        age_group=decade, gender=gender, occasion=occasion or "any", **common)
        for budget in GIFT_BUDGETS:
            yield q(f"What is the best gift for a {noun} under {budget}?",
                    subcategory="adults_budget", family="gift_adult_budget", priority=83,
                    cadence="monthly", gender=gender, budget=budget, **common)
        yield q(f"What is the best luxury gift for a {noun}?", subcategory="adults_budget",
                family="gift_adult_luxury", priority=82, cadence="monthly", gender=gender,
                budget="luxury", **common)

    for teen_gender in ("teen boy", "teen girl"):
        yield q(f"What is the best gift for a {teen_gender}?", subcategory="kids_by_age",
                family="gift_teen", priority=89, cadence="monthly", age_group="13-17",
                gender=teen_gender.split()[1], **common)

    for recipient, occasions in RECIPIENT_OCCASIONS.items():
        yield q(f"What is the best gift for {recipient}?", subcategory="by_recipient",
                family="gift_recipient", priority=89, cadence="monthly",
                recipient=recipient, occasion="any", **common)
        for occ in occasions:
            if occ.startswith("Secret Santa"):
                text = f"What is the best {occ} gift for {recipient}?"
            elif occ in ("a new baby", "thank-you", "farewell"):
                text = f"What is a good {occ.replace('a new baby', 'new baby')} gift for {recipient}?"
            else:
                text = f"What is the best {occ} gift for {recipient}?"
            seasonal = occ in ("Christmas", "Valentine's Day", "Mother's Day", "Father's Day")
            yield q(text, subcategory="by_recipient_occasion", family="gift_recipient_occasion",
                    priority=88 if seasonal else 84, cadence="weekly" if seasonal else "monthly",
                    recipient=recipient, occasion=occ, **common)

    for interest in GIFT_INTERESTS:
        yield q(f"What is the best gift for a {interest}?", subcategory="by_interest",
                family="gift_interest", priority=81, cadence="monthly", recipient=interest,
                **common)

    for text, base in [
        ("What are the hottest toys this holiday season?", 94),
        ("What is the most popular Christmas gift this year?", 94),
        ("What are the best stocking stuffers this year?", 88),
        ("What are the best last-minute gifts I can get delivered quickly?", 87),
        ("What is the best experience gift?", 82),
        ("What is the best subscription box to give as a gift?", 80),
        ("What is the best personalized gift?", 80),
        ("What is the best white elephant gift?", 84),
        ("What are the best gifts under $10?", 80),
        ("What is the best tech gift this year?", 86),
        ("What is the best gift card to give?", 78),
        ("What is the best Eid gift?", 74),
        ("What is the best Hanukkah gift?", 76),
        ("What is the best Diwali gift?", 74),
        ("What is the best Lunar New Year gift?", 72),
        ("What is the best Easter basket gift for kids?", 78),
        ("What is the best Valentine's Day gift for kids?", 74),
        ("What is the best baptism gift?", 70),
        ("What is the best bar mitzvah or bat mitzvah gift?", 70),
        ("What is the best quinceanera gift?", 70),
        ("What is the best sweet 16 gift?", 78),
        ("What is the best 21st birthday gift?", 80),
        ("What is the best 30th birthday gift?", 80),
        ("What is the best 40th birthday gift?", 80),
        ("What is the best 50th birthday gift?", 80),
        ("What is the best 60th birthday gift?", 78),
        ("What is the best 1st anniversary gift?", 80),
        ("What is the best 10th anniversary gift?", 76),
        ("What is the best 25th anniversary gift?", 76),
        ("What is the best 50th anniversary gift?", 74),
        ("What is the best get-well-soon gift?", 74),
        ("What is the best sympathy gift?", 72),
        ("What is the best corporate gift for clients?", 82),
    ]:
        yield q(text, subcategory="seasonal_and_milestone", family="gift_misc", priority=base,
                cadence="weekly" if "this" in text else "monthly", **common)


# --------------------------------------------------------------------------- #
# 3. PRODUCTS - "What is the best X to buy?" with budget + use-case variants
# --------------------------------------------------------------------------- #

# department -> [(item, has_budget_variant)]
PRODUCTS: dict[str, list[tuple[str, bool]]] = {
    "Computers": [("PC", True), ("laptop", True), ("gaming PC", True), ("gaming laptop", True),
                  ("desktop computer", True), ("all-in-one computer", False), ("MacBook", False),
                  ("Chromebook", True), ("2-in-1 laptop", True), ("tablet", True), ("iPad", False),
                  ("Android tablet", True), ("monitor", True), ("gaming monitor", True),
                  ("4K monitor", True), ("ultrawide monitor", False), ("mechanical keyboard", True),
                  ("wireless keyboard", True), ("gaming mouse", True), ("wireless mouse", True),
                  ("webcam", True), ("printer", True), ("laser printer", False), ("3D printer", True),
                  ("external hard drive", True), ("SSD", True), ("USB-C hub", True),
                  ("Wi-Fi router", True), ("mesh Wi-Fi system", True), ("NAS", False),
                  ("graphics card", True), ("CPU", True), ("docking station", False),
                  ("laptop stand", False), ("e-reader", True)],
    "Phones & Wearables": [("smartphone", True), ("iPhone", False), ("Android phone", True),
                           ("foldable phone", False), ("phone for seniors", True),
                           ("phone for kids", True), ("smartwatch", True), ("Apple Watch", False),
                           ("fitness tracker", True), ("smart ring", False),
                           ("kids smartwatch", True), ("phone case", True),
                           ("portable charger", True), ("wireless charger", True),
                           ("phone screen protector", False), ("phone gimbal", False)],
    "Audio": [("headphones", True), ("wireless earbuds", True), ("noise-cancelling headphones", True),
              ("AirPods alternative", True), ("gaming headset", True), ("Bluetooth speaker", True),
              ("soundbar", True), ("home theater system", True), ("smart speaker", True),
              ("turntable", True), ("bookshelf speakers", True), ("microphone for podcasting", True),
              ("open-ear headphones", False), ("kids headphones", True), ("hearing aids", True)],
    "TV & Home Entertainment": [("TV", True), ("4K TV", True), ("OLED TV", False), ("75-inch TV", True),
                                ("55-inch TV", True), ("projector", True), ("streaming device", True),
                                ("TV antenna", False), ("TV wall mount", False),
                                ("outdoor TV", False)],
    "Gaming": [("gaming console", False), ("PS5 game", False), ("Nintendo Switch 2 game", False),
               ("Xbox game", False), ("VR headset", True), ("gaming chair", True),
               ("handheld gaming PC", False), ("controller", True), ("racing wheel", False),
               ("gaming desk", True)],
    "Cameras & Drones": [("camera", True), ("mirrorless camera", True), ("camera for beginners", True),
                         ("vlogging camera", True), ("action camera", True), ("drone", True),
                         ("instant camera", True), ("security camera", True), ("doorbell camera", True),
                         ("baby monitor", True), ("dash cam", True), ("trail camera", True)],
    "Smart Home": [("smart thermostat", True), ("smart lock", True), ("smart lights", True),
                   ("smart plug", True), ("home security system", True), ("smart display", True),
                   ("robot vacuum", True), ("robot lawn mower", True), ("smart smoke detector", False),
                   ("video doorbell", True), ("smart garage door opener", False)],
    "Kitchen Appliances": [("air fryer", True), ("blender", True), ("coffee maker", True),
                           ("espresso machine", True), ("Instant Pot", False), ("slow cooker", True),
                           ("stand mixer", True), ("food processor", True), ("toaster oven", True),
                           ("microwave", True), ("refrigerator", True), ("dishwasher", True),
                           ("range", True), ("induction cooktop", True), ("wall oven", False),
                           ("range hood", False), ("electric kettle", True), ("juicer", True),
                           ("rice cooker", True), ("waffle maker", True), ("ice maker", True),
                           ("water filter pitcher", True), ("sous vide", True), ("pizza oven", True),
                           ("smoker", True), ("grill", True), ("gas grill", True),
                           ("pellet grill", True), ("griddle", True), ("bread maker", True),
                           ("cold brew maker", True), ("milk frother", True), ("wine fridge", True),
                           ("chest freezer", True)],
    "Cookware & Kitchen": [("cookware set", True), ("nonstick pan", True), ("cast iron skillet", True),
                           ("Dutch oven", True), ("chef's knife", True), ("knife set", True),
                           ("cutting board", False), ("food storage containers", True),
                           ("kitchen scale", False), ("meat thermometer", True),
                           ("water bottle", True), ("travel mug", True), ("dinnerware set", True),
                           ("baking sheet", False), ("salad spinner", False)],
    "Home Appliances": [("washing machine", True), ("dryer", True), ("washer dryer combo", True),
                        ("vacuum cleaner", True), ("cordless vacuum", True), ("carpet cleaner", True),
                        ("steam mop", True), ("air purifier", True), ("humidifier", True),
                        ("dehumidifier", True), ("space heater", True), ("window air conditioner", True),
                        ("portable air conditioner", True), ("ceiling fan", True), ("tower fan", True),
                        ("water softener", False), ("water heater", True), ("tankless water heater", False),
                        ("sewing machine", True), ("iron", True), ("garment steamer", True),
                        ("generator", True), ("portable power station", True), ("heat pump", False)],
    "Home & Furniture": [("mattress", True), ("memory foam mattress", True), ("hybrid mattress", True),
                         ("mattress for back pain", True), ("mattress topper", True), ("pillow", True),
                         ("sheets", True), ("comforter", True), ("weighted blanket", True),
                         ("sofa", True), ("sectional sofa", True), ("sleeper sofa", True),
                         ("recliner", True), ("office chair", True), ("standing desk", True),
                         ("bed frame", True), ("adjustable bed base", False), ("dresser", True),
                         ("rug", True), ("blackout curtains", True), ("bath towels", True),
                         ("shower head", True), ("bidet", True), ("toilet", False),
                         ("paint brand", False), ("paint color for a living room", False),
                         ("paint color for a bedroom", False), ("paint color for a kitchen", False),
                         ("exterior paint color", False), ("flooring", True),
                         ("kitchen countertop material", True), ("patio furniture", True),
                         ("outdoor rug", False), ("hammock", False), ("hot tub", True),
                         ("sauna", True), ("cold plunge tub", True), ("artificial Christmas tree", True)],
    "Tools & Outdoor": [("cordless drill", True), ("power tool brand", False), ("tool set", True),
                        ("lawn mower", True), ("electric lawn mower", True), ("riding lawn mower", True),
                        ("leaf blower", True), ("string trimmer", True), ("chainsaw", True),
                        ("pressure washer", True), ("snow blower", True), ("ladder", False),
                        ("shop vac", True), ("workbench", False), ("garden hose", False),
                        ("raised garden bed", True), ("composter", False), ("grill cover", False),
                        ("fire pit", True), ("outdoor string lights", False), ("solar lights", True)],
    "Sports & Fitness": [("treadmill", True), ("exercise bike", True), ("Peloton alternative", True),
                         ("rowing machine", True), ("elliptical", True), ("home gym", True),
                         ("adjustable dumbbells", True), ("kettlebell", False), ("yoga mat", True),
                         ("massage gun", True), ("foam roller", False), ("running shoes", True),
                         ("running shoes for flat feet", True), ("walking shoes", True),
                         ("trail running shoes", True), ("hiking boots", True), ("golf clubs", True),
                         ("golf driver", True), ("golf balls", True), ("golf rangefinder", True),
                         ("tennis racket", True), ("pickleball paddle", True), ("basketball", False),
                         ("bike", True), ("road bike", True), ("mountain bike", True), ("e-bike", True),
                         ("electric scooter", True), ("kids bike", True), ("bike helmet", True),
                         ("skateboard", True), ("snowboard", True), ("skis", True),
                         ("paddle board", True), ("kayak", True), ("fishing rod", True),
                         ("tent", True), ("sleeping bag", True), ("backpacking backpack", True),
                         ("cooler", True), ("camping stove", True), ("binoculars", True),
                         ("swim goggles", False), ("smart rope", False), ("sports watch", True)],
    "Baby & Kids": [("stroller", True), ("jogging stroller", True), ("car seat", True),
                    ("infant car seat", True), ("convertible car seat", True), ("booster seat", True),
                    ("crib", True), ("crib mattress", True), ("bassinet", True), ("baby carrier", True),
                    ("high chair", True), ("breast pump", True), ("baby bottle", True),
                    ("diapers", True), ("baby wipes", True), ("baby formula", True),
                    ("baby sound machine", True), ("play gym", False), ("baby swing", True),
                    ("kids tablet", True), ("kids camera", True), ("ride-on toy", True),
                    ("LEGO set", True), ("board game", True), ("family board game", True),
                    ("card game", True), ("puzzle", False), ("STEM toy", True), ("dollhouse", True),
                    ("kids art supplies", True), ("backpack for school", True),
                    ("lunch box", True), ("kids water bottle", True), ("trampoline", True),
                    ("swing set", True)],
    "Pets": [("dog food", True), ("puppy food", True), ("senior dog food", True),
             ("dog food for sensitive stomachs", True), ("cat food", True), ("kitten food", True),
             ("cat litter", True), ("self-cleaning litter box", True), ("dog bed", True),
             ("dog crate", True), ("dog harness", True), ("dog leash", False), ("dog toy", True),
             ("dog chew", True), ("flea and tick treatment", True), ("dog GPS tracker", True),
             ("automatic pet feeder", True), ("pet camera", True), ("pet water fountain", True),
             ("cat tree", True), ("pet hair vacuum", True), ("dog shampoo", False),
             ("dental chews for dogs", True), ("calming treats for dogs", True)],
    "Beauty & Skincare": [("moisturizer", True), ("moisturizer for dry skin", True),
                          ("moisturizer for oily skin", True), ("face wash", True),
                          ("face wash for acne", True), ("sunscreen", True), ("sunscreen for face", True),
                          ("retinol serum", True), ("vitamin C serum", True), ("eye cream", True),
                          ("anti-aging cream", True), ("acne treatment", True),
                          ("dark spot corrector", True), ("lip balm", False), ("shampoo", True),
                          ("shampoo for hair loss", True), ("dandruff shampoo", True),
                          ("conditioner", True), ("dry shampoo", True), ("hair dryer", True),
                          ("flat iron", True), ("curling iron", True), ("hair styler", True),
                          ("hair growth serum", True), ("foundation", True),
                          ("foundation for oily skin", True), ("concealer", True), ("mascara", True),
                          ("lipstick", True), ("tinted moisturizer", True), ("setting spray", True),
                          ("perfume for women", True), ("cologne for men", True),
                          ("body wash", True), ("deodorant", True), ("natural deodorant", True),
                          ("self tanner", True), ("nail polish", False), ("LED face mask", True),
                          ("men's skincare routine products", True), ("beard trimmer", True),
                          ("electric razor", True), ("razor for women", True),
                          ("electric toothbrush", True), ("water flosser", True),
                          ("teeth whitening kit", True), ("toothpaste", False)],
    "Health & Medical": [("blood pressure monitor", True), ("pulse oximeter", False),
                         ("thermometer", True), ("continuous glucose monitor", False),
                         ("smart scale", True), ("heating pad", True), ("TENS unit", True),
                         ("CPAP machine", True), ("mobility scooter", True), ("walker", True),
                         ("reading glasses", True), ("blue light glasses", True),
                         ("compression socks", True), ("orthotic insoles", True),
                         ("sleep mask", False), ("white noise machine", True)],
    "Luggage & Travel Gear": [("carry-on luggage", True), ("checked luggage", True),
                              ("luggage set", True), ("travel backpack", True), ("duffel bag", True),
                              ("packing cubes", False), ("travel pillow", False),
                              ("luggage tracker", True), ("travel adapter", False),
                              ("garment bag", False), ("kids luggage", True)],
    "Office & School": [("backpack", True), ("laptop bag", True), ("pen", True), ("notebook", False),
                        ("planner", True), ("label maker", True), ("paper shredder", True),
                        ("desk lamp", True), ("graphing calculator", True), ("headset for work calls", True)],
    "Auto Accessories": [("tires", True), ("all-season tires", True), ("winter tires", True),
                         ("EV charger", True), ("car jump starter", True), ("tire inflator", True),
                         ("car phone mount", False), ("car seat covers", True), ("floor mats", True),
                         ("roof cargo box", True), ("bike rack", True), ("car wax", False),
                         ("motor oil", False), ("car battery", True), ("radar detector", True),
                         ("Apple CarPlay adapter", True)],
    "Jewelry & Watches": [("watch for men", True), ("watch for women", True), ("luxury watch", False),
                          ("dive watch", True), ("engagement ring", True), ("lab-grown diamond", True),
                          ("wedding band", True), ("diamond stud earrings", True),
                          ("tennis bracelet", True), ("gold necklace", True)],
}

# Use-case variants for the categories people most often qualify.
USE_CASES: dict[str, list[str]] = {
    "laptop": ["students", "college students", "programming", "video editing", "business",
               "gaming", "graphic design", "seniors", "kids", "data science", "music production",
               "travel", "photo editing", "engineering students", "nursing students"],
    "PC": ["gaming", "video editing", "home office", "streaming", "AI and machine learning",
           "music production", "kids", "seniors", "small business", "3D rendering"],
    "TV": ["gaming", "sports", "bright rooms", "movies", "bedrooms", "seniors"],
    "smartphone": ["photography", "battery life", "gaming", "seniors", "kids", "business",
                   "privacy", "video recording"],
    "headphones": ["running", "travel", "the gym", "working from home", "sleeping",
                   "music production", "small ears"],
    "tablet": ["kids", "drawing", "students", "seniors", "reading", "note-taking"],
    "camera": ["YouTube", "travel", "wildlife photography", "sports photography", "real estate photography"],
    "mattress": ["side sleepers", "back sleepers", "stomach sleepers", "hot sleepers",
                 "couples", "heavy people", "kids"],
    "running shoes": ["beginners", "marathons", "wide feet", "plantar fasciitis",
                      "overpronation", "women", "men"],
    "office chair": ["back pain", "tall people", "short people", "gaming", "long hours"],
    "vacuum cleaner": ["pet hair", "hardwood floors", "carpet", "allergies", "stairs"],
    "air purifier": ["allergies", "smoke", "pet dander", "large rooms", "bedrooms", "mold"],
    "stroller": ["travel", "twins", "city living", "jogging", "newborns"],
    "car seat": ["small cars", "travel", "newborns", "toddlers"],
    "smartwatch": ["iPhone users", "Android users", "fitness", "seniors", "kids", "women"],
    "dog food": ["small breeds", "large breeds", "allergies", "weight loss", "picky eaters"],
    "monitor": ["MacBook", "programming", "photo editing", "office work", "PS5"],
    "Bluetooth speaker": ["the beach", "parties", "the shower", "outdoors"],
    "golf clubs": ["beginners", "seniors", "women", "high handicappers"],
    "e-bike": ["commuting", "seniors", "hills", "off-road", "heavy riders"],
}

PRICE_POINTS: dict[str, list[str]] = {
    "laptop": ["$300", "$500", "$700", "$1,000", "$1,500"],
    "PC": ["$500", "$800", "$1,000", "$1,500", "$2,000"],
    "gaming PC": ["$700", "$1,000", "$1,500", "$2,000"],
    "gaming laptop": ["$800", "$1,000", "$1,500"],
    "TV": ["$300", "$500", "$1,000"],
    "smartphone": ["$300", "$500", "$800"],
    "headphones": ["$50", "$100", "$200"],
    "wireless earbuds": ["$50", "$100"],
    "mattress": ["$500", "$1,000"],
    "espresso machine": ["$200", "$500", "$1,000"],
    "camera": ["$500", "$1,000"],
    "monitor": ["$200", "$300"],
    "office chair": ["$200", "$500"],
    "robot vacuum": ["$200", "$500"],
    "e-bike": ["$1,000", "$2,000"],
    "treadmill": ["$500", "$1,000"],
    "watch for men": ["$200", "$500", "$1,000"],
    "electric car": ["$35,000", "$50,000"],
}

HIGH_INTENT_PRODUCTS = {"PC", "laptop", "TV", "smartphone", "mattress", "headphones",
                        "air fryer", "robot vacuum", "gaming PC", "wireless earbuds", "tablet",
                        "espresso machine", "refrigerator", "washing machine", "stroller", "car seat",
                        "running shoes", "smartwatch", "e-bike", "treadmill", "sofa", "office chair"}


SINGULAR_S = {"tennis", "dress", "bus", "lens"}


def _is_plural(item: str) -> bool:
    head = item.split(" for ")[0].split(" under ")[0]
    last = head.split()[-1]
    return last.endswith("s") and not last.endswith("ss") and last not in SINGULAR_S


def _best(item: str, suffix: str = "", prefix: str = "") -> str:
    verb = "are" if _is_plural(item) else "is"
    return f"What {verb} the best {prefix}{item}{suffix}?"


def gen_products() -> Iterator[dict]:
    common = dict(category="Products", entity="product", monetization="affiliate_retail",
                  geo_scope="national")
    for dept, items in PRODUCTS.items():
        for item, budget in items:
            hi = item in HIGH_INTENT_PRODUCTS
            if item == "PC":
                text = "What is the best PC to buy?"
            elif item.startswith("paint color") or item.startswith("exterior paint") or item in (
                    "power tool brand", "paint brand", "kitchen countertop material", "flooring"):
                text = _best(item)
            else:
                text = _best(item, " to buy")
            yield q(text, subcategory=dept, family="product_best",
                    priority=93 if hi else 85, cadence="monthly", required=hi,
                    product_category=item, **common)
            if budget:
                yield q(_best(item, prefix="budget "), subcategory=dept,
                        family="product_budget", priority=84 if hi else 76, cadence="monthly",
                        product_category=item, budget="budget", **common)
            for use in USE_CASES.get(item, []):
                yield q(_best(item, f" for {use}"), subcategory=dept,
                        family="product_use_case", priority=82 if hi else 77, cadence="monthly",
                        product_category=item, use_case=use, **common)
            for price in PRICE_POINTS.get(item, []):
                yield q(_best(item, f" under {price}"), subcategory=dept,
                        family="product_price_point", priority=83 if hi else 77, cadence="monthly",
                        product_category=item, budget=price, **common)

    for text, sub in [
        ("Should I buy an iPhone or a Samsung Galaxy?", "Phones & Wearables"),
        ("Should I buy a Mac or a Windows PC?", "Computers"),
        ("What is the best Black Friday deal this year?", "Deals"),
        ("What is the best Amazon Prime Day deal right now?", "Deals"),
        ("What are the best deals on TVs right now?", "Deals"),
        ("What are the best deals on laptops right now?", "Deals"),
        ("What is the most reliable appliance brand?", "Home Appliances"),
        ("What is the best place to buy electronics online?", "Retailers"),
        ("What is the best place to buy furniture online?", "Retailers"),
        ("What is the best place to buy a mattress?", "Retailers"),
        ("What is the best place to buy appliances?", "Retailers"),
        ("What is the best online store for cheap clothes?", "Retailers"),
        ("What is the best refurbished electronics store?", "Retailers"),
        ("What are the best Costco buys right now?", "Retailers"),
        ("What are the best Trader Joe's products right now?", "Retailers"),
        ("What are the best Amazon finds right now?", "Retailers"),
        ("What are the best Target finds right now?", "Retailers"),
        ("What are the best IKEA products?", "Retailers"),
    ]:
        yield q(text, subcategory=sub, family="product_misc", priority=86,
                cadence="weekly" if "right now" in text or "deal" in text else "monthly", **common)


# --------------------------------------------------------------------------- #
# 4. FASHION
# --------------------------------------------------------------------------- #

FASHION_ITEMS = {
    "men": ["sneakers", "jeans", "jackets", "shirts", "t-shirts", "hoodies", "boots",
            "dress shoes", "suits", "chinos", "shorts", "sweaters", "watches", "sunglasses",
            "hats", "coats", "loafers", "joggers", "swim trunks", "polo shirts", "belts", "bags",
            "colors", "hairstyles"],
    "women": ["sneakers", "jeans", "dresses", "jackets", "tops", "boots", "handbags", "heels",
              "sandals", "sweaters", "coats", "skirts", "leggings", "swimsuits", "jewelry",
              "sunglasses", "flats", "pants", "blazers", "loafers", "workout clothes", "colors",
              "hairstyles", "nail colors"],
}
FASHION_AUDIENCES = ["men", "women", "teen boys", "teen girls", "boys", "girls",
                     "men over 40", "women over 40", "men over 50", "women over 50",
                     "women over 60", "plus-size women", "big and tall men", "college students"]
SEASONS = ["spring", "summer", "fall", "winter"]
OUTFIT_OCCASIONS = ["a wedding as a guest", "a job interview", "a first date", "a beach vacation",
                    "the office", "a cocktail party", "a graduation", "a funeral", "a concert",
                    "a music festival", "a ski trip", "a holiday party", "a black-tie event",
                    "a business casual office", "Europe in the summer", "a baby shower",
                    "a family photo shoot", "Thanksgiving dinner", "New Year's Eve", "a night out"]
BEST_BRAND_ITEMS = {
    "men": ["jeans", "white sneakers", "running shoes", "t-shirts", "dress shirts", "suits",
            "underwear", "socks", "boots", "winter coats", "rain jackets", "hoodies",
            "athleisure", "workwear", "swim trunks", "chinos", "dress shoes", "sunglasses"],
    "women": ["jeans", "white sneakers", "running shoes", "leggings", "bras", "underwear",
              "winter coats", "rain jackets", "work pants", "dresses", "boots", "swimsuits",
              "handbags", "sports bras", "sandals", "flats", "workwear", "sunglasses"],
}


def gen_fashion() -> Iterator[dict]:
    common = dict(category="Fashion", entity="apparel", monetization="affiliate_retail",
                  geo_scope="national")
    yield q("What clothes are in style right now?", subcategory="trends", family="fashion_trend",
            priority=95, cadence="weekly", required=True, **common)
    yield q("What are the biggest fashion trends this season?", subcategory="trends",
            family="fashion_trend", priority=92, cadence="weekly", **common)
    for aud in FASHION_AUDIENCES:
        yield q(f"What clothes are in style right now for {aud}?", subcategory="trends",
                family="fashion_trend_audience", priority=91, cadence="weekly",
                required=aud in ("men", "women"), gender=aud, **common)
    for gender, items in FASHION_ITEMS.items():
        for item in items:
            yield q(f"What {item} are in style right now for {gender}?", subcategory="trending_items",
                    family="fashion_item_trend", priority=86, cadence="weekly", gender=gender,
                    product_category=item, **common)
    for gender in ("men", "women"):
        for season in SEASONS:
            yield q(f"What should {gender} wear this {season}?", subcategory="seasonal",
                    family="fashion_season", priority=84, cadence="quarterly", gender=gender,
                    occasion=season, **common)
            for decade in ("20s", "30s", "40s", "50s", "60s"):
                noun = "a man" if gender == "men" else "a woman"
                yield q(f"What should {noun} in their {decade} wear this {season}?",
                        subcategory="seasonal_by_age", family="fashion_season_age", priority=78,
                        cadence="quarterly", gender=gender, age_group=decade, occasion=season, **common)
        for occ in OUTFIT_OCCASIONS:
            yield q(f"What should {gender} wear to {occ}?", subcategory="occasion_outfits",
                    family="fashion_occasion", priority=80, cadence="quarterly", gender=gender,
                    occasion=occ, **common)
        for item in BEST_BRAND_ITEMS[gender]:
            yield q(f"What is the best brand of {item} for {gender}?", subcategory="best_brand",
                    family="fashion_best_brand", priority=83, cadence="monthly", gender=gender,
                    product_category=item, **common)
    for text in ["What are the most popular sneakers right now?",
                 "What is the hottest handbag right now?",
                 "What is the most popular clothing brand right now?",
                 "What is the best affordable clothing brand?",
                 "What is the best sustainable clothing brand?",
                 "What is the best luxury fashion brand?",
                 "What is the best online clothing store?",
                 "What is the best clothing subscription box?",
                 "What is the best place to buy designer clothes for less?",
                 "What is the best resale site for designer clothes?",
                 "What is the best capsule wardrobe to buy?",
                 "What are the must-have wardrobe basics?",
                 "What kids clothes brand is best?",
                 "What is the best maternity clothing brand?",
                 "What is the best athleisure brand?",
                 "What is the best workwear brand for women?",
                 "What is the best men's grooming brand?"]:
        yield q(text, subcategory="brands_retailers", family="fashion_misc", priority=85,
                cadence="monthly", **common)


# --------------------------------------------------------------------------- #
# 5. HEALTH & NUTRITION
# --------------------------------------------------------------------------- #

HEALTH_GOALS = [
    "lose weight", "lose belly fat", "build muscle", "gain weight", "lower cholesterol",
    "lower blood pressure", "manage type 2 diabetes", "improve gut health", "boost energy",
    "sleep better", "reduce inflammation", "get clearer skin", "boost immunity",
    "improve memory and focus", "support a healthy pregnancy", "ease menopause symptoms",
    "improve heart health", "strengthen bones", "recover after a workout", "grow healthier hair",
    "reduce bloating", "boost fertility", "support liver health", "support kidney health",
    "reduce anxiety", "manage PCOS", "support thyroid health", "protect eye health",
    "lower blood sugar", "improve digestion", "relieve constipation", "reduce acid reflux",
    "manage arthritis pain", "increase testosterone", "balance hormones", "boost metabolism",
    "reduce sugar cravings", "stay full longer", "get more protein without meat",
    "eat healthy on a budget", "fuel for a marathon", "lose weight on GLP-1 medication",
    "keep muscle on GLP-1 medication", "live longer", "reduce migraines",
]

DIETS = ["weight loss", "muscle gain", "heart health", "diabetes", "longevity", "gut health",
         "beginners", "busy people", "women over 50", "men over 40", "athletes", "vegetarians",
         "inflammation", "PCOS", "high blood pressure"]

HEALTHIEST = ["snack", "breakfast", "cereal", "bread", "yogurt", "protein bar", "granola",
              "peanut butter", "frozen meal", "fast food meal", "Starbucks drink", "energy drink",
              "sports drink", "chips", "ice cream", "pasta", "milk alternative", "cooking oil",
              "sweetener", "salad dressing", "coffee creamer", "kids snack", "lunch for work",
              "dinner", "Chipotle order", "Chick-fil-A order", "Subway sandwich", "pizza chain order"]

SUPPLEMENTS = ["protein powder", "whey protein", "plant-based protein powder", "creatine",
               "multivitamin", "multivitamin for women", "multivitamin for men", "prenatal vitamin",
               "vitamin D", "magnesium", "magnesium for sleep", "omega-3 fish oil", "collagen",
               "probiotic", "melatonin", "electrolyte powder", "pre-workout", "ashwagandha",
               "fiber supplement", "greens powder", "iron supplement", "vitamin B12",
               "zinc supplement", "turmeric supplement", "biotin", "kids multivitamin",
               "sleep supplement", "berberine", "NAD+ supplement", "glucosamine",
               "testosterone booster", "nootropic", "meal replacement shake", "protein shake",
               "weight loss supplement"]

HEALTH_PROGRAMS = [
    "weight loss program", "weight loss app", "GLP-1 telehealth provider", "calorie counting app",
    "fitness app", "home workout program", "running app", "strength training app",
    "meditation app", "sleep app", "online therapy service", "telehealth service",
    "meal delivery service for weight loss", "healthy meal kit", "intermittent fasting app",
    "diabetes management program", "physical therapy app", "menopause telehealth provider",
    "men's health telehealth provider", "online personal trainer service", "dietitian service",
    "at-home blood test", "full-body MRI scan service", "longevity clinic", "hair loss treatment",
    "online pharmacy", "acne telehealth service", "online eye exam and glasses retailer",
    "contact lens retailer", "hearing test and hearing aid provider",
]


def gen_health() -> Iterator[dict]:
    common = dict(category="Health & Nutrition", geo_scope="national")
    for goal in HEALTH_GOALS:
        hi = goal in ("lose weight", "lose belly fat", "build muscle", "lower cholesterol")
        yield q(f"What foods should I eat to {goal}?", subcategory="foods_for_goal",
                family="health_foods_goal", entity="food_list", priority=90 if hi else 82,
                monetization="grocery_and_cpg", cadence="quarterly", required=hi,
                use_case=goal, **common)
        yield q(f"What foods should I avoid to {goal}?", subcategory="foods_to_avoid",
                family="health_foods_avoid", entity="food_list", priority=76,
                monetization="grocery_and_cpg", cadence="quarterly", use_case=goal, **common)
    yield q("What types of foods should I eat to lose weight?", subcategory="foods_for_goal",
            family="health_foods_goal", entity="food_list", priority=95,
            monetization="grocery_and_cpg", cadence="quarterly", required=True,
            use_case="lose weight", **common)
    for d in DIETS:
        yield q(f"What is the best diet for {d}?", subcategory="diets", family="health_diet",
                entity="diet_program", priority=80, monetization="subscription_affiliate",
                cadence="quarterly", use_case=d, **common)
    for h in HEALTHIEST:
        yield q(f"What is the healthiest {h}?", subcategory="healthiest_choice",
                family="health_healthiest", entity="product", priority=79,
                monetization="grocery_and_cpg", cadence="quarterly", product_category=h, **common)
    for s in SUPPLEMENTS:
        yield q(_best(s, " to buy"), subcategory="supplements",
                family="health_supplement", entity="supplement", priority=84,
                monetization="affiliate_retail", cadence="monthly", product_category=s, **common)
    for p in HEALTH_PROGRAMS:
        yield q(f"What is the best {p}?", subcategory="programs_and_services",
                family="health_program", entity="diet_program", priority=83,
                monetization="subscription_affiliate", cadence="monthly", product_category=p, **common)
    for text in ["What is the best workout to lose weight?", "What is the best workout to build muscle at home?",
                 "What is the best high-protein snack?", "What is the best low-carb snack?",
                 "What fruits are best for weight loss?", "What vegetables are healthiest?",
                 "What is the best breakfast for weight loss?", "What is the best drink for hydration?",
                 "What is the best coffee for health?", "What is the best tea for weight loss?",
                 "What is the best cooking oil for health?", "What is the best fish to eat?",
                 "What are the best anti-inflammatory foods?", "What are the best high-fiber foods?",
                 "What are the best foods for kids' brain development?",
                 "What are the best superfoods?", "What are the best foods to eat before bed?",
                 "What are the best foods to eat before a workout?"]:
        yield q(text, subcategory="foods_misc", family="health_misc", entity="food_list",
                priority=80, monetization="grocery_and_cpg", cadence="quarterly", **common)


# --------------------------------------------------------------------------- #
# 6. ENTERTAINMENT
# --------------------------------------------------------------------------- #

STREAMERS = ["Netflix", "Max", "Prime Video", "Disney+", "Hulu", "Apple TV+", "Peacock",
             "Paramount+", "YouTube", "Tubi", "Crunchyroll", "BritBox"]
GENRES = ["comedy", "drama", "thriller", "horror", "action", "sci-fi", "fantasy", "romance",
          "romantic comedy", "crime", "true crime", "documentary", "animated", "family", "mystery",
          "war", "western", "musical", "reality", "anime", "K-drama", "British", "sports",
          "superhero", "historical", "psychological thriller", "teen", "stand-up comedy"]
AUDIENCES = ["my kids", "the whole family", "date night", "teens", "a girls' night",
             "my parents", "a rainy day", "a binge this weekend", "a long flight",
             "someone who loved Breaking Bad", "someone who loved The Office",
             "someone who loved Game of Thrones", "someone who loved Succession",
             "someone who loved Stranger Things", "someone who loved Yellowstone",
             "someone who loved Friends", "someone who loved The Bear",
             "someone who loved Severance", "someone who loved Squid Game"]
BOOK_GENRES = ["fiction", "thriller", "mystery", "romance", "romantasy", "fantasy", "sci-fi",
               "horror", "historical fiction", "literary fiction", "memoir", "biography",
               "self-help", "business", "personal finance", "productivity", "history",
               "true crime", "young adult", "middle grade", "children's picture", "audiobook",
               "book club", "beach read", "nonfiction", "parenting", "health", "cookbook",
               "leadership", "AI"]
PODCAST_TOPICS = ["overall", "comedy", "true crime", "news", "business", "investing",
                  "history", "science", "sports", "health", "self-improvement", "technology",
                  "AI", "politics", "parenting", "pop culture", "interview", "storytelling",
                  "entrepreneurship", "relationships", "kids"]
GAME_PLATFORMS = ["PS5", "Xbox Series X", "Nintendo Switch 2", "PC", "iPhone", "Android",
                  "Meta Quest", "Steam Deck"]
GAME_GENRES = ["overall", "RPG", "shooter", "open-world", "co-op", "multiplayer", "racing",
               "sports", "puzzle", "horror", "family", "indie", "strategy", "free-to-play"]


def gen_entertainment() -> Iterator[dict]:
    common = dict(category="Entertainment", geo_scope="national")
    media = dict(entity="media_title", monetization="streaming_affiliate", **common)
    yield q("What should I watch on streaming right now?", subcategory="streaming",
            family="ent_stream_now", priority=96, cadence="weekly", required=True, **media)
    for fmt in ("movie", "TV show"):
        yield q(f"What is the best {fmt} to stream right now?", subcategory="streaming",
                family="ent_stream_format", priority=94, cadence="weekly", required=True,
                product_category=fmt, **media)
        yield q(f"What is the best new {fmt} this week?", subcategory="streaming",
                family="ent_stream_new", priority=92, cadence="weekly", product_category=fmt, **media)
        for s in STREAMERS:
            yield q(f"What is the best {fmt} on {s} right now?", subcategory="streaming_by_service",
                    family="ent_stream_service", priority=91 if s in STREAMERS[:8] else 82,
                    cadence="weekly", product_category=fmt, brand=s, **media)
        for g in GENRES:
            yield q(f"What is the best {g} {fmt} to stream right now?", subcategory="streaming_by_genre",
                    family="ent_stream_genre", priority=85, cadence="weekly",
                    product_category=fmt, use_case=g, **media)
    for a in AUDIENCES:
        yield q(f"What should I watch tonight with {a}?" if a.startswith(("my", "the", "teens"))
                else f"What should I watch for {a}?", subcategory="streaming_by_audience",
                family="ent_stream_audience", priority=84, cadence="weekly", use_case=a, **media)
    for text in ["What movie should I see in theaters this weekend?",
                 "What is the best movie of the year so far?",
                 "What is the best TV show of the year so far?",
                 "What is the most popular show on Netflix right now?",
                 "Which streaming service has the best shows right now?",
                 "Which streaming service is worth paying for?",
                 "What is the best live TV streaming service?",
                 "What is the best streaming bundle?",
                 "What is the best free streaming service?",
                 "What is the best streaming service for sports?",
                 "What is the best streaming service for kids?",
                 "What is the best streaming service for movies?",
                 "What is the best music streaming service?",
                 "What is the best audiobook service?"]:
        ent = "service_provider" if "service" in text or "bundle" in text else "media_title"
        yield q(text, subcategory="streaming_misc", family="ent_misc", entity=ent, priority=89,
                monetization="streaming_affiliate", cadence="weekly", **common)
    for g in BOOK_GENRES:
        yield q(f"What is the best {g} book to read right now?", subcategory="books",
                family="ent_book", entity="book", priority=78, monetization="affiliate_retail",
                cadence="monthly", use_case=g, **common)
    for t in PODCAST_TOPICS:
        text = ("What is the best podcast to listen to right now?" if t == "overall"
                else f"What is the best {t} podcast right now?")
        yield q(text, subcategory="podcasts", family="ent_podcast", entity="podcast", priority=74,
                monetization="audio_ads", cadence="monthly", use_case=t, **common)
    for p in GAME_PLATFORMS:
        for g in GAME_GENRES:
            text = (f"What is the best game on {p} right now?" if g == "overall"
                    else f"What is the best {g} game on {p}?")
            yield q(text, subcategory="video_games", family="ent_game", entity="video_game",
                    priority=82 if g == "overall" else 74, monetization="affiliate_retail",
                    cadence="monthly", brand=p, use_case=g, **common)
    for text in ["What is the best new album right now?", "What is the best new song right now?",
                 "What concert tour should I see this year?", "What is the best music festival to attend?",
                 "What Broadway show should I see?", "What is the best comedy special to watch?",
                 "What is the best YouTube channel to watch?", "What is the best mobile game right now?",
                 "What is the best board game for adults?", "What is the best party game?"]:
        ent = ("media_title" if "album" in text or "song" in text or "special" in text or "channel" in text
               else "video_game" if "game" in text else "attraction")
        yield q(text, subcategory="music_and_live", family="ent_misc", entity=ent, priority=78,
                monetization="ticket_commission" if ent == "attraction" else "affiliate_retail",
                cadence="monthly", **common)


# --------------------------------------------------------------------------- #
# 7. FINANCE
# --------------------------------------------------------------------------- #

FINANCE = {
    "credit_cards": ["credit card", "travel credit card", "cash back credit card",
                     "balance transfer credit card", "credit card for students",
                     "credit card for bad credit", "credit card to build credit",
                     "first credit card", "small business credit card", "airline credit card",
                     "hotel credit card", "no annual fee credit card", "credit card for groceries",
                     "credit card for gas", "credit card for dining", "premium travel credit card",
                     "0% APR credit card", "credit card with no foreign transaction fees",
                     "secured credit card", "Amazon credit card alternative"],
    "banking": ["bank", "checking account", "high-yield savings account", "CD rate",
                "online bank", "bank for small business", "bank account for kids",
                "bank account for teens", "bank for students", "money market account",
                "credit union", "bank for international travel"],
    "investing": ["brokerage account", "investing app for beginners", "robo-advisor",
                  "Roth IRA provider", "IRA provider", "S&P 500 index fund", "dividend ETF",
                  "bond ETF", "crypto exchange", "crypto wallet", "gold IRA company",
                  "place to buy gold and silver", "529 plan", "HSA provider",
                  "financial advisor", "fee-only financial planner", "retirement planning tool",
                  "stock research tool", "options trading platform", "day trading platform",
                  "AI stock picking tool", "Treasury bond platform"],
    "lending": ["mortgage lender", "mortgage lender for first-time buyers", "refinance lender",
                "HELOC lender", "personal loan", "debt consolidation loan",
                "student loan refinance lender", "private student loan", "auto loan lender",
                "small business loan", "SBA lender", "buy now pay later app", "VA loan lender",
                "FHA loan lender", "reverse mortgage lender"],
    "insurance": ["car insurance", "car insurance for young drivers", "car insurance for seniors",
                  "home insurance", "renters insurance", "term life insurance",
                  "whole life insurance", "pet insurance", "travel insurance",
                  "health insurance for self-employed", "dental insurance", "umbrella insurance",
                  "small business insurance", "motorcycle insurance", "flood insurance",
                  "long-term care insurance", "disability insurance", "Medicare Advantage plan",
                  "Medicare supplement plan", "landlord insurance"],
    "money_tools": ["budgeting app", "tax software", "tax preparer service", "credit monitoring service",
                    "identity theft protection", "money transfer app", "international money transfer service",
                    "debt payoff app", "net worth tracker", "bill negotiation service",
                    "credit repair company", "will and estate planning service",
                    "payroll service", "business accounting software", "invoice app",
                    "expense tracking app", "savings app", "kids allowance app"],
}


def gen_finance() -> Iterator[dict]:
    for sub, items in FINANCE.items():
        for item in items:
            hi = item in ("credit card", "travel credit card", "high-yield savings account",
                          "car insurance", "mortgage lender", "brokerage account", "bank")
            yield q(f"What is the best {item}?", category="Finance", subcategory=sub,
                    family="finance_best", entity="financial_product" if sub != "money_tools" else "software",
                    priority=92 if hi else 84, monetization="lead_gen_cpa", cadence="monthly",
                    required=hi, product_category=item, geo_scope="national")
    for text in ["What is the best credit card right now?", "Which bank has the highest savings rate right now?",
                 "What are the best stocks to buy right now?", "What is the best ETF to buy right now?",
                 "What is the best way to invest $10,000?", "What is the best way to invest $1,000?",
                 "What is the best way to save for retirement?", "What is the best way to build credit?",
                 "What is the best way to pay off credit card debt?", "What is the best cryptocurrency to buy?",
                 "What is the best mortgage rate right now?", "What is the best car insurance for families?",
                 "What is the best way to save for a house?", "What is the best way to send money abroad?",
                 "What is the best side hustle right now?", "What is the best way to make passive income?"]:
        yield q(text, category="Finance", subcategory="money_questions", family="finance_misc",
                entity="financial_product", priority=86, monetization="lead_gen_cpa",
                cadence="weekly" if "right now" in text else "monthly", geo_scope="national")


# --------------------------------------------------------------------------- #
# 8. TRAVEL (non-local)
# --------------------------------------------------------------------------- #

TRAVEL_BRANDS = {
    "airlines": ["airline", "airline in the US", "international airline", "airline for business class",
                 "airline for first class", "budget airline", "airline for long-haul flights",
                 "airline to fly to Europe", "airline to fly to Asia", "airline to fly to Hawaii",
                 "airline for families", "airline loyalty program", "airline for legroom in economy"],
    "hotel_brands": ["hotel chain", "luxury hotel brand", "budget hotel chain", "extended-stay hotel brand",
                     "hotel loyalty program", "all-inclusive resort brand", "boutique hotel brand",
                     "family-friendly hotel brand"],
    "booking": ["hotel booking site", "flight booking site", "vacation rental site", "cruise booking site",
                "car rental company", "travel agency", "luxury travel agency", "travel app",
                "flight deal alert service", "travel rewards program", "eSIM for international travel",
                "airport lounge program", "TSA PreCheck alternative", "travel insurance company",
                "tour operator", "group tour company", "RV rental company"],
    "cruises": ["cruise line", "cruise line for families", "cruise line for couples", "luxury cruise line",
                "cruise line for first-timers", "adults-only cruise line", "river cruise line",
                "Alaska cruise", "Caribbean cruise", "Mediterranean cruise", "expedition cruise",
                "Disney cruise alternative", "cruise for seniors", "cruise for young adults"],
    "theme_parks": ["theme park", "theme park for little kids", "theme park for thrill seekers",
                    "water park", "Disney park", "Universal park", "ski resort", "ski resort for beginners",
                    "golf resort", "wellness retreat", "dude ranch", "safari company", "summer camp for kids"],
}
DESTINATION_TYPES = ["vacation destination", "beach vacation", "ski trip", "honeymoon destination",
                     "family vacation", "solo travel destination", "girls trip destination",
                     "bachelor party destination", "bachelorette party destination", "budget vacation",
                     "luxury vacation", "adventure vacation", "foodie destination", "wine region to visit",
                     "spring break destination", "fall foliage trip", "Christmas market trip",
                     "national park to visit", "road trip", "weekend getaway", "babymoon destination",
                     "all-inclusive resort", "all-inclusive resort in Mexico",
                     "all-inclusive resort in the Caribbean", "all-inclusive resort for families",
                     "adults-only all-inclusive resort", "overwater bungalow resort",
                     "island to visit", "European city to visit", "Asian country to visit",
                     "place to see the Northern Lights", "place to retire abroad",
                     "digital nomad destination", "place to travel with a dog",
                     "destination for a family reunion", "destination for a 40th birthday trip",
                     "destination wedding location", "cheap international destination",
                     "US city for a weekend trip", "US beach town"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"]


def gen_travel() -> Iterator[dict]:
    common = dict(category="Travel", geo_scope="global", monetization="booking_commission")
    for sub, items in TRAVEL_BRANDS.items():
        for item in items:
            yield q(f"What is the best {item}?", subcategory=sub, family="travel_brand",
                    entity="travel_brand", priority=86, cadence="monthly", product_category=item, **common)
    for d in DESTINATION_TYPES:
        yield q(f"What is the best {d}?", subcategory="destinations", family="travel_destination",
                entity="destination" if "resort" not in d else "hotel", priority=88,
                cadence="monthly", required=d == "vacation destination", use_case=d, **common)
    for m in MONTHS:
        yield q(f"Where should I go on vacation in {m}?", subcategory="destinations_by_month",
                family="travel_month", entity="destination", priority=87, cadence="monthly",
                occasion=m, **common)
        yield q(f"What is the best beach destination in {m}?", subcategory="destinations_by_month",
                family="travel_month_beach", entity="destination", priority=80, cadence="monthly",
                occasion=m, **common)
    for region in ["Europe", "the Caribbean", "Mexico", "Asia", "South America", "Africa",
                   "the Middle East", "Australia and New Zealand", "Hawaii", "Florida",
                   "California", "Canada", "the Mediterranean", "Southeast Asia", "Japan", "Italy",
                   "Greece", "Spain", "France", "Portugal"]:
        yield q(f"What is the best place to visit in {region}?", subcategory="destinations_by_region",
                family="travel_region", entity="destination", priority=84, cadence="quarterly",
                use_case=region, **common)
        yield q(f"What is the best resort in {region}?", subcategory="resorts_by_region",
                family="travel_region_resort", entity="hotel", priority=85, cadence="quarterly",
                use_case=region, **common)


# --------------------------------------------------------------------------- #
# 9. AUTOS
# --------------------------------------------------------------------------- #

VEHICLE_SEGMENTS = ["car", "SUV", "compact SUV", "subcompact SUV", "midsize SUV", "3-row SUV",
                    "full-size SUV", "luxury SUV", "sedan", "compact car", "luxury sedan",
                    "sports car", "pickup truck", "midsize truck", "full-size truck", "minivan",
                    "electric car", "electric SUV", "electric truck", "hybrid car", "hybrid SUV",
                    "plug-in hybrid", "first car for a teenager", "family car", "commuter car",
                    "car for seniors", "off-road vehicle", "convertible", "luxury car",
                    "car for towing", "car for snow", "fuel-efficient car", "car for Uber drivers",
                    "car for tall people", "car for dogs"]


def gen_auto() -> Iterator[dict]:
    common = dict(category="Autos", entity="vehicle", geo_scope="national",
                  monetization="dealer_lead_gen")
    for seg in VEHICLE_SEGMENTS:
        hi = seg in ("car", "SUV", "electric car", "pickup truck", "compact SUV", "hybrid car")
        yield q(f"What is the best {seg} to buy?", subcategory="new", family="auto_best",
                priority=92 if hi else 86, cadence="quarterly", required=hi, product_category=seg, **common)
        yield q(f"What is the best used {seg} to buy?", subcategory="used", family="auto_used",
                priority=84, cadence="quarterly", product_category=seg, **common)
        yield q(f"What is the most reliable {seg}?", subcategory="reliability", family="auto_reliable",
                priority=82, cadence="quarterly", product_category=seg, **common)
        yield q(f"What is the best {seg} to lease right now?", subcategory="lease", family="auto_lease",
                priority=80, cadence="monthly", product_category=seg, **common)
    for price in ["$20,000", "$30,000", "$40,000", "$50,000", "$75,000"]:
        yield q(f"What is the best car under {price}?", subcategory="by_price", family="auto_price",
                priority=86, cadence="quarterly", budget=price, **common)
        yield q(f"What is the best SUV under {price}?", subcategory="by_price", family="auto_price",
                priority=85, cadence="quarterly", budget=price, **common)
    for text, ent in [("What is the most reliable car brand?", "vehicle"),
                      ("What is the best place to buy a used car?", "service_provider"),
                      ("What is the best website to sell my car?", "service_provider"),
                      ("What is the best extended car warranty?", "service_provider"),
                      ("What is the best motorcycle for beginners?", "vehicle"),
                      ("What is the best touring motorcycle?", "vehicle"),
                      ("What is the best RV to buy?", "vehicle"),
                      ("What is the best camper van?", "vehicle"),
                      ("What is the best boat for families?", "vehicle"),
                      ("What is the best golf cart?", "vehicle"),
                      ("What is the best car subscription service?", "service_provider"),
                      ("What is the best car detailing product?", "product"),
                      ("Should I buy an EV or a hybrid?", "vehicle"),
                      ("What is the best Tesla alternative?", "vehicle")]:
        yield q(text, subcategory="auto_misc", family="auto_misc", entity=ent, priority=82,
                cadence="quarterly", **{k: v for k, v in common.items() if k != "entity"})


# --------------------------------------------------------------------------- #
# 10. SOFTWARE / B2B
# --------------------------------------------------------------------------- #

SOFTWARE = ["CRM", "project management software", "accounting software", "payroll software",
            "HR software", "website builder", "e-commerce platform", "email marketing platform",
            "social media scheduling tool", "VPN", "password manager", "antivirus software",
            "cloud storage service", "note-taking app", "AI chatbot", "AI image generator",
            "AI video generator", "AI writing tool", "AI coding assistant", "AI meeting notetaker",
            "AI agent platform", "video conferencing software", "team chat app", "help desk software",
            "POS system", "invoicing software", "expense management software", "e-signature tool",
            "survey tool", "web hosting provider", "domain registrar", "data warehouse",
            "BI tool", "ETL tool", "data observability tool", "customer data platform",
            "web analytics tool", "SEO tool", "form builder", "scheduling app", "VoIP phone system",
            "applicant tracking system", "learning management system", "marketing automation platform",
            "ad management platform", "landing page builder", "podcast hosting platform",
            "video editing software", "photo editing software", "graphic design tool",
            "screen recording tool", "PDF editor", "to-do list app", "calendar app", "email app",
            "browser", "parental control app", "backup software", "cybersecurity platform",
            "endpoint security software", "identity and access management tool",
            "customer support chatbot", "call center software", "field service software",
            "inventory management software", "restaurant POS system", "property management software",
            "dental practice software", "legal practice management software",
            "construction management software", "nonprofit CRM", "church management software",
            "real estate CRM", "salon booking software", "gym management software",
            "web scraping tool", "proxy provider", "vector database", "LLM observability tool",
            "data catalog", "feature store", "notebook platform for data science",
            "workflow orchestration tool", "reverse ETL tool", "product analytics tool"]


def gen_software() -> Iterator[dict]:
    common = dict(category="Software & B2B", entity="software", geo_scope="global",
                  monetization="saas_affiliate")
    for s in SOFTWARE:
        yield q(f"What is the best {s}?", subcategory="software", family="software_best",
                priority=86, cadence="monthly", product_category=s, **common)
        yield q(f"What is the best {s} for small business?", subcategory="software_smb",
                family="software_smb", priority=82, cadence="monthly", product_category=s,
                use_case="small business", **common)
        yield q(f"What is the best free {s}?", subcategory="software_free", family="software_free",
                priority=76, cadence="monthly", product_category=s, budget="free", **common)


# --------------------------------------------------------------------------- #
# 11. CONSUMER SERVICES
# --------------------------------------------------------------------------- #

SERVICES = ["meal kit", "grocery delivery service", "food delivery app", "home security company",
            "internet provider", "cell phone carrier", "prepaid phone plan", "family phone plan",
            "home warranty company", "pest control company", "lawn care service", "moving company",
            "long-distance moving company", "storage company", "solar company", "home solar battery",
            "online therapy platform", "dating app", "dating app for over 50", "job search site",
            "freelance marketplace", "resume writing service", "online course platform",
            "language learning app", "DNA test", "photo printing service", "photo book service",
            "online florist", "gift basket company", "wine club", "coffee subscription",
            "razor subscription", "clothing rental service", "kids subscription box",
            "laundry service", "house cleaning service", "babysitting app", "nanny agency",
            "senior care service", "home health aide agency", "dog walking app", "pet sitting app",
            "dog food delivery service", "wedding registry", "wedding planning app",
            "printing service for small business", "shipping carrier", "mail forwarding service",
            "rideshare app", "car wash membership", "gym membership", "boutique fitness studio chain",
            "streaming TV service", "home internet for rural areas", "satellite internet provider",
            "electric company", "home energy audit service", "window replacement company",
            "bathroom remodeling company", "kitchen remodeling company", "roofing company",
            "gutter company", "HVAC brand", "garage door company", "pool builder",
            "fence company", "landscaping company", "home builder", "real estate brokerage",
            "home buying site", "apartment search site", "iBuyer", "flat-fee realtor"]


def gen_services() -> Iterator[dict]:
    for s in SERVICES:
        yield q(f"What is the best {s}?", category="Consumer Services", subcategory="services",
                family="service_best", entity="service_provider", priority=82,
                monetization="lead_gen_cpa", cadence="monthly", product_category=s,
                geo_scope="national")


# --------------------------------------------------------------------------- #
# 12. EDUCATION & CAREERS
# --------------------------------------------------------------------------- #

MAJORS = ["computer science", "business", "engineering", "nursing", "medicine (pre-med)", "law",
          "economics", "finance", "psychology", "biology", "data science", "artificial intelligence",
          "mechanical engineering", "electrical engineering", "architecture", "film", "music",
          "art and design", "journalism", "education", "political science", "marketing",
          "accounting", "physics", "chemistry", "environmental science", "hospitality",
          "fashion design", "game design", "kinesiology", "public health", "aviation",
          "culinary arts", "cybersecurity", "supply chain management"]

EDU_PROGRAMS = ["MBA program", "online MBA", "executive MBA", "online bachelor's degree",
                "online master's degree", "community college", "liberal arts college",
                "public university", "college for the money", "HBCU", "coding bootcamp",
                "data science bootcamp", "UX design bootcamp", "cybersecurity certification",
                "AI certification", "project management certification", "online certificate program",
                "SAT prep course", "ACT prep course", "LSAT prep course", "MCAT prep course",
                "GMAT prep course", "online tutoring service", "math tutoring app",
                "online high school", "boarding school", "study abroad program",
                "trade school", "nursing school", "law school", "medical school",
                "kids coding program", "reading app for kids", "learning app for preschoolers",
                "college admissions consultant", "career coaching service", "summer program for teens"]

CAREERS = ["What is the best job for the future?", "What is the best high-paying job without a degree?",
           "What is the best career for introverts?", "What is the best remote job?",
           "What is the best trade to learn?", "What is the best certification to get a job in tech?",
           "What is the best side job for teachers?", "What is the best job for college students?",
           "What is the best AI skill to learn?", "What is the best programming language to learn?",
           "What is the best company to work for?", "What is the best tech company to work for?",
           "What is the best city for jobs?", "What is the best career change at 40?"]


def gen_education() -> Iterator[dict]:
    common = dict(category="Education & Careers", geo_scope="national", monetization="lead_gen_cpa")
    for m in MAJORS:
        yield q(f"What is the best college for {m}?", subcategory="colleges_by_major",
                family="edu_college_major", entity="institution", priority=80, cadence="quarterly",
                use_case=m, **common)
    for p in EDU_PROGRAMS:
        yield q(f"What is the best {p}?", subcategory="programs", family="edu_program",
                entity="institution", priority=80, cadence="quarterly", product_category=p, **common)
    for text in CAREERS:
        yield q(text, subcategory="careers", family="edu_career", entity="institution",
                priority=74, cadence="quarterly", **common)


# --------------------------------------------------------------------------- #
# 13. FOOD & BEVERAGE (national brands / chains)
# --------------------------------------------------------------------------- #

WINE_VARIETALS = ["cabernet sauvignon", "pinot noir", "chardonnay", "sauvignon blanc", "rosé",
                  "prosecco", "champagne", "malbec", "red blend", "pinot grigio", "riesling",
                  "zinfandel", "merlot", "sparkling wine"]
FOOD_BEV = ["fast food chain", "fast food burger", "fast food fries", "chicken sandwich",
            "chicken nuggets", "pizza chain", "coffee chain", "Starbucks drink",
            "Dunkin' drink", "fast casual restaurant chain", "sit-down restaurant chain",
            "steakhouse chain", "breakfast chain", "taco chain", "wing chain", "sandwich chain",
            "donut chain", "ice cream chain", "grocery store", "frozen pizza", "frozen meal",
            "bourbon under $50", "bourbon", "tequila", "vodka", "gin", "rum", "scotch",
            "Japanese whisky", "beer", "light beer", "IPA", "non-alcoholic beer",
            "non-alcoholic spirit", "hard seltzer", "canned cocktail", "energy drink",
            "sparkling water", "protein bar", "coffee beans", "K-Cup coffee", "olive oil",
            "hot sauce", "BBQ sauce", "chocolate", "ice cream brand", "cereal", "potato chips",
            "plant-based meat", "plant-based milk", "pasta sauce", "boxed mac and cheese",
            "coffee creamer", "kombucha", "steak to order online", "seafood delivery",
            "meat delivery service", "Thanksgiving turkey to order", "birthday cake to order",
            "snack subscription box"]


def gen_food_bev() -> Iterator[dict]:
    common = dict(category="Food & Beverage", geo_scope="national", monetization="affiliate_retail")
    for v in WINE_VARIETALS:
        yield q(f"What is the best {v} under $20?", subcategory="wine", family="fb_wine",
                entity="product", priority=76, cadence="quarterly", product_category=v,
                budget="$20", **common)
        yield q(f"What is the best {v} to buy?", subcategory="wine", family="fb_wine",
                entity="product", priority=76, cadence="quarterly", product_category=v, **common)
    for f in FOOD_BEV:
        chain = "chain" in f or "restaurant" in f
        yield q(_best(f), subcategory="chains" if chain else "brands",
                family="fb_best", entity="restaurant" if chain else "product",
                priority=84 if chain else 78, cadence="monthly", product_category=f, **common)
    for text in ["What is the best thing to order at McDonald's?", "What is the best thing to order at Chick-fil-A?",
                 "What is the best thing to order at Taco Bell?", "What is the best thing to order at Chipotle?",
                 "What is the best thing to order at Starbucks?", "What is the best thing to buy at Costco?",
                 "What is the best thing to buy at Trader Joe's?", "What is the best new fast food item right now?",
                 "What is the best Thanksgiving side dish?", "What is the best recipe for dinner tonight?",
                 "What is the best easy weeknight dinner?", "What is the best air fryer recipe?",
                 "What is the best cocktail to make at home?", "What is the best wine for Thanksgiving?",
                 "What is the best wine to bring to a dinner party?", "What is the best champagne for New Year's Eve?"]:
        yield q(text, subcategory="what_to_order", family="fb_misc", entity="product", priority=80,
                cadence="monthly", **common)


# --------------------------------------------------------------------------- #
# 14. HOME, PETS, LIVING & HEALTHCARE PROVIDERS
# --------------------------------------------------------------------------- #

DOG_BREED_FOR = ["families", "apartments", "first-time owners", "people with allergies", "seniors",
                 "kids", "runners", "guarding a home", "busy people", "small spaces", "cold climates",
                 "hot climates", "therapy and emotional support", "low shedding", "smart and easy to train"]
LIVE_FOR = ["families", "retirees", "young professionals", "remote workers", "low cost of living",
            "safety", "public schools", "outdoor lovers", "great weather", "LGBTQ+ people",
            "first-time home buyers", "job growth", "no state income tax", "affordable beach living",
            "tech jobs", "singles", "buying a house right now", "raising kids", "walkability",
            "food lovers"]
HOSPITAL_FOR = ["cancer treatment", "heart surgery", "orthopedics", "neurology", "pediatrics",
                "maternity care", "transplants", "spine surgery", "eye care", "mental health",
                "cardiology", "diabetes care", "fertility treatment", "plastic surgery", "rehabilitation"]


def gen_living() -> Iterator[dict]:
    for b in DOG_BREED_FOR:
        yield q(f"What is the best dog breed for {b}?", category="Pets", subcategory="breeds",
                family="pet_breed", entity="pet_breed", priority=74, monetization="pet_lead_gen",
                cadence="yearly", use_case=b, geo_scope="national")
    for b in ["What is the best cat breed for families?", "What is the best cat breed for apartments?",
              "What is the best hypoallergenic cat breed?", "What is the best pet for kids?",
              "What is the best small pet for apartments?"]:
        yield q(b, category="Pets", subcategory="breeds", family="pet_breed", entity="pet_breed",
                priority=70, monetization="pet_lead_gen", cadence="yearly", geo_scope="national")
    for l in LIVE_FOR:
        yield q(f"What is the best place to live in the US for {l}?", category="Real Estate & Living",
                subcategory="where_to_live", family="living_where", entity="place_to_live", priority=80,
                monetization="real_estate_lead_gen", cadence="quarterly", use_case=l, geo_scope="national")
    for l in ["retirees", "remote workers", "families", "Americans moving abroad", "low cost of living"]:
        yield q(f"What is the best country to live in for {l}?", category="Real Estate & Living",
                subcategory="where_to_live", family="living_country", entity="place_to_live",
                priority=74, monetization="real_estate_lead_gen", cadence="quarterly",
                use_case=l, geo_scope="global")
    for h in HOSPITAL_FOR:
        yield q(f"What is the best hospital in the US for {h}?", category="Healthcare Providers",
                subcategory="hospitals", family="health_hospital", entity="institution", priority=78,
                monetization="patient_lead_gen", cadence="yearly", use_case=h, geo_scope="national")


# --------------------------------------------------------------------------- #

def generate_all(markets: list[dict]) -> Iterator[dict]:
    yield from gen_local(markets)
    yield from gen_gifts()
    yield from gen_products()
    yield from gen_fashion()
    yield from gen_health()
    yield from gen_entertainment()
    yield from gen_finance()
    yield from gen_travel()
    yield from gen_auto()
    yield from gen_software()
    yield from gen_services()
    yield from gen_education()
    yield from gen_food_bev()
    yield from gen_living()
