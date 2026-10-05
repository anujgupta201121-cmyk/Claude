"""
Life-stage and personal verticals: romance & dating, sexual wellness,
parenting, medical, weddings, aging, home improvement, legal, betting.

These are the questions people ask an assistant privately rather than search
publicly. They still resolve to a business: a dating app, a telehealth
provider, a drug brand, a curriculum, a retailer.
"""

from __future__ import annotations

from typing import Iterator

from .taxonomy import _best, q

# --------------------------------------------------------------------------- #
# ROMANCE & DATING
# --------------------------------------------------------------------------- #

DATING_AUDIENCES = ["serious relationships", "marriage", "casual dating", "people over 40",
                    "people over 50", "seniors", "single parents", "gay men", "lesbians",
                    "LGBTQ+ people", "Christians", "Jewish singles", "Muslim singles",
                    "Black singles", "Asian singles", "Latino singles", "professionals",
                    "introverts", "college students", "men", "women", "small towns",
                    "people who want kids", "divorced people", "millionaires", "farmers",
                    "nerds and gamers", "fitness lovers", "vegans", "Indian singles"]

ROMANCE_PRODUCTS = [
    ("dating app", "service_provider"), ("free dating app", "service_provider"),
    ("dating site", "service_provider"), ("matchmaking service", "service_provider"),
    ("speed dating company", "service_provider"), ("dating coach", "service_provider"),
    ("online couples therapy service", "service_provider"), ("relationship app for couples", "software"),
    ("long-distance relationship app", "software"), ("couples game", "product"),
    ("relationship book", "book"), ("book about love languages", "book"),
    ("book for couples", "book"), ("romance novel", "book"),
    ("date night subscription box", "service_provider"), ("couples cooking class", "experience"),
    ("couples massage", "experience"), ("hot air balloon ride company", "experience"),
    ("place to propose in the US", "destination"), ("place to propose in the world", "destination"),
    ("proposal planning service", "service_provider"), ("online engagement ring retailer", "product"),
    ("romantic getaway in the US", "destination"), ("romantic getaway in Europe", "destination"),
    ("romantic getaway in the Caribbean", "destination"), ("romantic weekend getaway near New York", "destination"),
    ("romantic weekend getaway near Los Angeles", "destination"), ("romantic weekend getaway near Chicago", "destination"),
    ("romantic weekend getaway near Dallas", "destination"), ("romantic weekend getaway near Atlanta", "destination"),
    ("romantic cabin rental", "hotel"), ("couples resort", "hotel"), ("anniversary trip", "destination"),
    ("Valentine's Day dinner reservation app", "service_provider"), ("flower delivery for Valentine's Day", "service_provider"),
    ("love letter or custom song service", "service_provider"), ("couples photoshoot company", "service_provider"),
]

DATE_IDEAS = ["first date idea", "cheap date idea", "at-home date night idea", "rainy day date idea",
              "winter date idea", "summer date idea", "fall date idea", "spring date idea",
              "anniversary date idea", "Valentine's Day date idea", "date idea for married couples",
              "adventurous date idea", "double date idea", "date idea for introverts",
              "creative date idea", "outdoor date idea", "date idea for parents with young kids"]


def gen_romance() -> Iterator[dict]:
    common = dict(category="Romance & Dating", geo_scope="national")
    yield q("What is the best dating app right now?", subcategory="dating_apps", family="romance_dating_app",
            entity="service_provider", priority=94, monetization="subscription_affiliate",
            cadence="monthly", required=True, **common)
    for a in DATING_AUDIENCES:
        yield q(f"What is the best dating app for {a}?", subcategory="dating_apps",
                family="romance_dating_app_audience", entity="service_provider", priority=86,
                monetization="subscription_affiliate", cadence="monthly", use_case=a, **common)
    for item, ent in ROMANCE_PRODUCTS:
        money = {"service_provider": "subscription_affiliate", "software": "subscription_affiliate",
                 "book": "affiliate_retail", "product": "affiliate_retail",
                 "experience": "ticket_commission"}.get(ent, "booking_commission")
        yield q(_best(item), subcategory="relationships", family="romance_best", entity=ent,
                priority=82, monetization=money, cadence="monthly", product_category=item, **common)
    for idea in DATE_IDEAS:
        yield q(f"What is the best {idea}?", subcategory="date_ideas", family="romance_date_idea",
                entity="experience", priority=78, monetization="ticket_commission", cadence="quarterly",
                use_case=idea, **common)
    for lang in ["words of affirmation", "quality time", "acts of service", "physical touch", "receiving gifts"]:
        yield q(f"What is the best gift for a partner whose love language is {lang}?",
                subcategory="romantic_gifts", family="romance_love_language_gift", entity="gift",
                priority=80, monetization="affiliate_retail", cadence="quarterly", use_case=lang, **common)
    for genre in ["romantic movie", "romantic comedy", "romance series", "romantic movie for date night",
                  "romantic movie on Netflix", "romantic K-drama", "romantic anime"]:
        yield q(f"What is the best {genre} to watch right now?", subcategory="romantic_entertainment",
                family="romance_watch", entity="media_title", priority=80, monetization="streaming_affiliate",
                cadence="monthly", use_case=genre, **common)
    for occasion in ["first anniversary", "fifth anniversary", "tenth anniversary", "Valentine's Day",
                     "birthday", "proposal", "babymoon", "honeymoon"]:
        yield q(f"What is the best romantic trip for a {occasion}?", subcategory="romantic_travel",
                family="romance_trip_occasion", entity="destination", priority=80,
                monetization="booking_commission", cadence="quarterly", occasion=occasion, **common)
    for m in ["January", "February", "March", "April", "May", "June", "July", "August",
              "September", "October", "November", "December"]:
        yield q(f"Where is the best romantic getaway in {m}?", subcategory="romantic_travel",
                family="romance_getaway_month", entity="destination", priority=80,
                monetization="booking_commission", cadence="monthly", occasion=m, **common)
    for text in ["What is the best way to meet someone without dating apps?",
                 "What is the best dating profile photo service?",
                 "What is the best AI dating assistant?",
                 "What is the best background check site for online dating?",
                 "What is the best place to meet singles in my 30s?",
                 "What is the best book to fix a struggling marriage?",
                 "What is the best marriage retreat?",
                 "What is the best premarital counseling program?"]:
        yield q(text, subcategory="relationships", family="romance_misc", entity="service_provider",
                priority=78, monetization="subscription_affiliate", cadence="quarterly", **common)


# --------------------------------------------------------------------------- #
# SEXUAL WELLNESS (adult, non-explicit, commercial)
# --------------------------------------------------------------------------- #

SEX_WELLNESS_PRODUCTS = [
    "vibrator", "vibrator for beginners", "wand massager", "couples vibrator", "app-controlled toy",
    "sex toy for women", "sex toy for men", "sex toy for couples", "sex toy brand",
    "body-safe sex toy brand", "personal lubricant", "water-based lubricant", "silicone lubricant",
    "natural lubricant", "condoms", "ultra-thin condoms", "large condoms", "latex-free condoms",
    "massage oil for couples", "lingerie brand", "plus-size lingerie brand", "men's underwear brand",
    "Kegel trainer", "pelvic floor trainer", "vaginal moisturizer", "libido supplement for women",
    "libido supplement for men", "adult board game for couples", "sex toy cleaner",
    "discreet adult store online", "sex education book for adults", "couples intimacy app",
]

SEX_HEALTH_SERVICES = [
    "erectile dysfunction treatment", "online ED prescription service", "premature ejaculation treatment",
    "testosterone therapy provider", "at-home STI test", "STI testing clinic chain",
    "birth control delivery service", "birth control method", "emergency contraception",
    "fertility tracking app", "ovulation test", "pregnancy test", "period tracking app",
    "online sex therapist", "sexual health telehealth service", "PrEP provider",
    "low libido treatment for women", "menopause treatment for low libido",
    "vasectomy provider", "male fertility test",
]


SEX_TOY_AUDIENCES = ["women over 50", "long-distance couples", "travel", "first-time buyers",
                     "couples trying something new", "solo use", "people with arthritis",
                     "postpartum women", "men over 50", "LGBTQ+ couples"]
SEX_CONDITIONS = ["vaginal dryness", "low sex drive in women", "low sex drive in men", "pain during sex",
                  "delayed ejaculation", "performance anxiety", "erectile dysfunction after 50",
                  "loss of libido during menopause", "low libido on antidepressants", "Peyronie's disease"]


def gen_sexual_wellness() -> Iterator[dict]:
    common = dict(category="Sexual Wellness", geo_scope="national", age_group="18+")
    for aud in SEX_TOY_AUDIENCES:
        yield q(f"What is the best sex toy for {aud}?", subcategory="products", family="sexwell_audience",
                entity="product", priority=80, monetization="affiliate_retail", cadence="monthly",
                use_case=aud, **common)
    for cond in SEX_CONDITIONS:
        yield q(f"What is the best treatment for {cond}?", subcategory="sexual_health",
                family="sexwell_condition", entity="treatment", priority=84,
                monetization="telehealth_cpa", cadence="quarterly", use_case=cond, **common)
    for item in SEX_WELLNESS_PRODUCTS:
        yield q(_best(item, " to buy"), subcategory="products", family="sexwell_product", entity="product",
                priority=84, monetization="affiliate_retail", cadence="monthly", product_category=item, **common)
    for budget_item in ["vibrator", "couples vibrator", "lingerie brand", "sex toy for men"]:
        yield q(_best(budget_item, prefix="budget "), subcategory="products", family="sexwell_budget",
                entity="product", priority=78, monetization="affiliate_retail", cadence="monthly",
                product_category=budget_item, budget="budget", **common)
    for item in SEX_HEALTH_SERVICES:
        ent = "treatment" if any(w in item for w in ("treatment", "method", "contraception", "therapy")) \
            else "service_provider"
        yield q(_best(item), subcategory="sexual_health", family="sexwell_health", entity=ent,
                priority=86, monetization="telehealth_cpa", cadence="monthly", product_category=item, **common)
    for text in ["What is the best way to spice up a relationship?",
                 "What is the best gift for a couple's intimacy?",
                 "What is the best Valentine's Day gift for the bedroom?",
                 "What is the best anniversary gift for a romantic night in?"]:
        yield q(text, subcategory="intimacy", family="sexwell_misc", entity="product", priority=80,
                monetization="affiliate_retail", cadence="quarterly", **common)


# --------------------------------------------------------------------------- #
# PARENTING
# --------------------------------------------------------------------------- #

CHILD_AGES = list(range(0, 13))
GRADES = ["kindergarten"] + [f"{n}{'st' if n == 1 else 'nd' if n == 2 else 'rd' if n == 3 else 'th'} grade"
                             for n in range(1, 13)]

PARENTING_PRODUCTS = [
    "pregnancy app", "pregnancy pillow", "maternity support belt", "postpartum recovery kit",
    "nursing bra", "nipple cream", "baby registry", "baby name app", "baby food brand",
    "organic baby food", "baby food maker", "formula for colic", "formula for reflux",
    "formula for gas", "overnight diapers", "cloth diapers", "swaddle", "sleep sack",
    "pacifier", "teething toy", "bottle sterilizer", "diaper bag", "diaper pail",
    "baby bathtub", "baby gate", "baby-proofing kit", "potty training seat", "potty training book",
    "toddler bed", "toddler car seat", "kids multivitamin", "kids toothpaste", "kids sunscreen",
    "kids shoes", "kids rain boots", "kids winter coat", "kids GPS tracker", "first phone for a child",
    "parental control app", "screen time app", "kids e-reader", "kids headphones with volume limit",
    "chore chart app", "family organizer app", "family calendar app", "kids allowance card",
    "baby sleep app", "white noise machine for babies", "sleep training method",
    "sleep training book", "parenting book", "parenting book for toddlers", "parenting book for teens",
    "positive discipline book", "co-parenting app", "babysitter booking app", "daycare chain",
    "Montessori school chain", "preschool curriculum", "homeschool curriculum", "online homeschool program",
    "reading program for kids", "math program for kids", "kids coding app", "kids language app",
    "kids YouTube alternative", "family streaming plan", "kids meal delivery", "kids lunch box idea",
    "family photographer service", "kids birthday party venue chain", "kids birthday party theme",
    "summer camp", "sleepaway camp", "day camp", "kids swim school chain", "kids martial arts program",
    "kids music lessons app", "kids tutoring service", "driving school for teens",
    "teen skincare routine products", "teen deodorant", "teen car", "college savings app",
    "college planning service", "family travel insurance", "family-friendly cruise line",
]


CHILD_NEEDS = ["ADHD", "anxiety", "autism", "dyslexia", "speech delay", "picky eating", "bedwetting",
               "sleep problems", "big emotions", "a new sibling", "divorce", "grief", "bullying",
               "screen time addiction", "low confidence", "social skills"]


def _age_noun(age: int) -> str:
    return "a newborn" if age == 0 else f"a {age}-year-old"


def gen_parenting() -> Iterator[dict]:
    common = dict(category="Parenting", geo_scope="national")
    for age in CHILD_AGES:
        a = _age_noun(age)
        for text, fam, ent, base, money in [
            (f"What are the best books for {a}?", "parent_books_age", "book", 84, "affiliate_retail"),
            (f"What is the best educational toy for {a}?", "parent_edu_toy_age", "product", 84, "affiliate_retail"),
            (f"What is the best learning app for {a}?", "parent_app_age", "software", 80, "subscription_affiliate"),
            (f"What are the best activities for {a}?", "parent_activity_age", "experience", 76, "ticket_commission"),
        ]:
            if age == 0 and fam in ("parent_app_age", "parent_activity_age"):
                continue
            yield q(text, subcategory="by_child_age", family=fam, entity=ent, priority=base,
                    monetization=money, cadence="quarterly", age_group=str(age), **common)
    for age in range(1, 18):
        a = _age_noun(age)
        if age <= 12:
            yield q(f"What is the best birthday party idea for {a}?", subcategory="by_child_age",
                    family="parent_party_age", entity="experience", priority=78,
                    monetization="ticket_commission", cadence="quarterly", age_group=str(age), **common)
        if 2 <= age <= 12:
            yield q(f"What is the best bike for {a}?", subcategory="by_child_age", family="parent_bike_age",
                    entity="product", priority=78, monetization="affiliate_retail", cadence="yearly",
                    age_group=str(age), **common)
        if 3 <= age <= 12:
            yield q(f"What is the best board game for {a}?", subcategory="by_child_age",
                    family="parent_board_game_age", entity="product", priority=78,
                    monetization="affiliate_retail", cadence="quarterly", age_group=str(age), **common)
        if age >= 8:
            yield q(f"What is the best phone for {a}?", subcategory="by_child_age", family="parent_phone_age",
                    entity="product", priority=80, monetization="affiliate_retail", cadence="quarterly",
                    age_group=str(age), **common)
        if age >= 13:
            yield q(f"What are the best books for {a}?", subcategory="by_child_age", family="parent_books_age",
                    entity="book", priority=80, monetization="affiliate_retail", cadence="quarterly",
                    age_group=str(age), **common)
    for need in CHILD_NEEDS:
        yield q(f"What is the best book to help a child with {need}?", subcategory="child_needs",
                family="parent_need_book", entity="book", priority=78, monetization="affiliate_retail",
                cadence="yearly", use_case=need, **common)
        yield q(f"What is the best program or therapy for a child with {need}?", subcategory="child_needs",
                family="parent_need_program", entity="service_provider", priority=80,
                monetization="lead_gen_cpa", cadence="yearly", use_case=need, **common)
    for g in GRADES:
        yield q(f"What is the best homeschool curriculum for {g}?", subcategory="education",
                family="parent_homeschool_grade", entity="product", priority=76,
                monetization="affiliate_retail", cadence="yearly", age_group=g, **common)
        yield q(f"What is the best tutoring program for {g} math?", subcategory="education",
                family="parent_tutor_grade", entity="service_provider", priority=74,
                monetization="lead_gen_cpa", cadence="yearly", age_group=g, **common)
    for item in PARENTING_PRODUCTS:
        ent = ("book" if "book" in item else "software" if item.endswith("app") else
               "treatment" if "method" in item else
               "service_provider" if any(w in item for w in ("service", "chain", "camp", "program",
                                                               "school", "registry", "plan", "insurance",
                                                               "cruise", "card")) else "product")
        yield q(_best(item), subcategory="products_and_services", family="parent_best", entity=ent,
                priority=82, monetization="affiliate_retail" if ent in ("product", "book") else "lead_gen_cpa",
                cadence="quarterly", product_category=item, **common)
    for trimester in ("first", "second", "third"):
        yield q(f"What should I buy in my {trimester} trimester of pregnancy?", subcategory="pregnancy",
                family="parent_trimester", entity="product", priority=82, monetization="affiliate_retail",
                cadence="quarterly", occasion=f"{trimester} trimester", **common)
    for text in ["What do I need to buy before the baby arrives?", "What are the must-have baby products?",
                 "What baby products are a waste of money?", "What is the best baby product of the year?",
                 "What is the best family vacation with a toddler?", "What is the best family vacation with teens?",
                 "What is the best family car for three kids?", "What is the best way to save for my child's college?",
                 "What is the best app to keep track of my teen driver?", "What is the best age to give a child a phone?",
                 "What is the best treatment for a baby with a cold?", "What is the best diaper rash cream?",
                 "What is the best children's pain reliever?", "What is the best lice treatment?"]:
        ent = "treatment" if any(w in text for w in ("cold", "rash", "pain", "lice")) else \
            "destination" if "vacation" in text else "product"
        yield q(text, subcategory="parenting_questions", family="parent_misc", entity=ent, priority=82,
                monetization="affiliate_retail", cadence="quarterly", **common)


# --------------------------------------------------------------------------- #
# MEDICAL
# --------------------------------------------------------------------------- #

# (condition, has OTC option, has online/telehealth care)
CONDITIONS = [
    ("headaches", True, False), ("migraines", True, True), ("back pain", True, True),
    ("neck pain", True, False), ("knee pain", True, False), ("arthritis", True, True),
    ("plantar fasciitis", True, False), ("sciatica", True, True), ("muscle soreness", True, False),
    ("seasonal allergies", True, True), ("a cold", True, True), ("the flu", True, True),
    ("a sinus infection", True, True), ("a sore throat", True, True), ("a cough", True, False),
    ("COVID", True, True), ("acid reflux", True, True), ("heartburn", True, False),
    ("constipation", True, False), ("diarrhea", True, False), ("IBS", True, True),
    ("bloating", True, False), ("nausea", True, False), ("hemorrhoids", True, False),
    ("a UTI", False, True), ("a yeast infection", True, True), ("bacterial vaginosis", False, True),
    ("insomnia", True, True), ("anxiety", False, True), ("depression", False, True),
    ("ADHD in adults", False, True), ("ADHD in children", False, True), ("panic attacks", False, True),
    ("PTSD", False, True), ("OCD", False, True), ("burnout", False, True),
    ("acne", True, True), ("adult acne", True, True), ("eczema", True, True), ("psoriasis", True, True),
    ("rosacea", True, True), ("dandruff", True, False), ("hair loss in men", True, True),
    ("hair loss in women", True, True), ("wrinkles", True, True), ("dark spots", True, True),
    ("toenail fungus", True, True), ("athlete's foot", True, False), ("cold sores", True, True),
    ("warts", True, False), ("dry eyes", True, True), ("snoring", True, True), ("sleep apnea", False, True),
    ("high blood pressure", False, True), ("high cholesterol", False, True), ("type 2 diabetes", False, True),
    ("prediabetes", False, True), ("obesity", False, True), ("hypothyroidism", False, True),
    ("menopause symptoms", True, True), ("hot flashes", True, True), ("PCOS", False, True),
    ("endometriosis", False, True), ("period cramps", True, False), ("low testosterone", False, True),
    ("erectile dysfunction", False, True), ("enlarged prostate", False, True), ("gout", False, True),
    ("tinnitus", True, True), ("hearing loss", True, True), ("vertigo", True, False),
    ("long COVID", False, True), ("chronic fatigue", False, True), ("fibromyalgia", False, True),
    ("smoking addiction", True, True), ("alcohol addiction", False, True), ("motion sickness", True, False),
    ("jet lag", True, False), ("sunburn", True, False), ("bug bites", True, False),
    ("poison ivy", True, False), ("shingles", False, True), ("a sprained ankle", True, False),
    ("tendonitis", True, False), ("carpal tunnel", True, True), ("TMJ", True, True),
    ("teeth sensitivity", True, False), ("bad breath", True, False), ("gum disease", True, False),
]

PROCEDURES = ["LASIK provider", "hair transplant clinic", "weight loss surgery", "dental implant provider",
              "Invisalign alternative", "clear aligner brand", "teeth whitening treatment",
              "Botox alternative", "dermal filler brand", "laser hair removal chain", "CoolSculpting alternative",
              "IV therapy service", "urgent care chain", "walk-in clinic chain", "concierge medicine practice",
              "primary care membership", "telehealth app", "online psychiatrist service",
              "online therapy app", "online doctor for prescriptions", "mail-order pharmacy",
              "prescription discount card", "GLP-1 medication for weight loss", "compounded semaglutide provider",
              "at-home lab test", "DNA health test", "full-body scan service", "cancer screening test",
              "colon cancer screening test", "allergy test", "food sensitivity test", "sleep study at home",
              "physical therapy clinic chain", "chiropractor chain", "acupuncture clinic chain",
              "medical weight loss clinic", "fertility clinic", "egg freezing provider", "IVF clinic",
              "addiction treatment center", "eating disorder treatment program", "mental health app",
              "ADHD telehealth provider", "hearing aid brand", "contact lens brand", "eye drop brand",
              "CPAP alternative", "sleep apnea mouthguard", "pain relief cream", "probiotic for women",
              "medical alert device", "health insurance plan for families", "dental plan without insurance"]


KID_CONDITIONS = ["fever", "ear infections", "croup", "hand, foot and mouth disease", "pink eye",
                  "eczema", "constipation", "teething pain", "colic", "reflux", "allergies", "asthma",
                  "a cough", "head lice", "warts"]
PREGNANCY_CONDITIONS = ["morning sickness", "heartburn", "back pain", "insomnia", "constipation",
                        "a cold", "headaches", "stretch marks", "swollen feet", "leg cramps",
                        "hemorrhoids", "anxiety"]


def gen_medical() -> Iterator[dict]:
    common = dict(category="Medical", geo_scope="national")
    for cond in KID_CONDITIONS:
        yield q(f"What is the best treatment for {cond} in children?", subcategory="pediatric",
                family="med_kids_treatment", entity="treatment", priority=82,
                monetization="pharma_and_telehealth", cadence="quarterly", use_case=cond,
                age_group="0-12", **common)
    for cond in PREGNANCY_CONDITIONS:
        yield q(f"What is the best safe treatment for {cond} during pregnancy?", subcategory="pregnancy",
                family="med_pregnancy_treatment", entity="treatment", priority=82,
                monetization="pharma_and_telehealth", cadence="quarterly", use_case=cond, **common)
    for cond, otc, online in CONDITIONS:
        yield q(f"What is the best treatment for {cond}?", subcategory="treatments", family="med_treatment",
                entity="treatment", priority=88, monetization="pharma_and_telehealth", cadence="quarterly",
                use_case=cond, **common)
        if otc:
            yield q(f"What is the best over-the-counter medicine for {cond}?", subcategory="otc",
                    family="med_otc", entity="treatment", priority=86, monetization="affiliate_retail",
                    cadence="quarterly", use_case=cond, **common)
        if otc:
            yield q(f"What is the best home remedy for {cond}?", subcategory="home_remedies",
                    family="med_home_remedy", entity="treatment", priority=78, monetization="affiliate_retail",
                    cadence="quarterly", use_case=cond, **common)
        else:
            yield q(f"What is the best prescription medication for {cond}?", subcategory="prescriptions",
                    family="med_rx", entity="treatment", priority=84, monetization="pharma_and_telehealth",
                    cadence="quarterly", use_case=cond, **common)
        if online:
            yield q(f"Where is the best place to get treated for {cond} online?", subcategory="telehealth",
                    family="med_online_care", entity="service_provider", priority=84,
                    monetization="telehealth_cpa", cadence="quarterly", use_case=cond, **common)
    for p in PROCEDURES:
        ent = "treatment" if any(w in p for w in ("medication", "treatment", "surgery", "cream",
                                                   "mouthguard", "alternative")) else \
            "product" if "brand" in p or "drops" in p or "device" in p else "service_provider"
        yield q(_best(p), subcategory="procedures_and_providers", family="med_best", entity=ent,
                priority=84, monetization="telehealth_cpa", cadence="quarterly", product_category=p, **common)


# --------------------------------------------------------------------------- #
# WEDDINGS
# --------------------------------------------------------------------------- #

WEDDING_ITEMS = ["wedding dress designer", "affordable wedding dress brand", "online bridal shop",
                 "bridesmaid dress brand", "wedding suit brand", "tuxedo rental company",
                 "wedding band for men", "wedding band for women", "engagement ring style right now",
                 "wedding invitation website", "wedding website builder", "wedding photographer booking site",
                 "wedding planner app", "wedding budget app", "wedding favor idea", "wedding cake trend",
                 "wedding flower delivery service", "wedding DJ booking site", "wedding insurance",
                 "elopement package", "micro wedding venue type", "bachelorette party destination",
                 "bachelor party destination", "honeymoon destination in Europe", "honeymoon destination in Asia",
                 "all-inclusive honeymoon resort", "wedding guest gift", "bridal shower gift",
                 "groomsmen gift", "bridesmaid proposal gift", "wedding shoe brand",
                 "wedding hair and makeup service", "prenup service",
                 "fall wedding idea", "winter wedding idea", "spring wedding idea", "summer wedding idea",
                 "wedding on a $10,000 budget idea", "courthouse wedding outfit", "vow renewal idea",
                 "wedding thank-you card service", "wedding dress preservation service",
                 "wedding guest dress brand"]


def gen_weddings() -> Iterator[dict]:
    for item in WEDDING_ITEMS:
        ent = ("destination" if "destination" in item else "hotel" if "resort" in item else
               "gift" if "gift" in item else "experience" if "idea" in item or "trend" in item or "style" in item
               else "service_provider" if any(w in item for w in ("site", "website", "app", "service",
                                                                   "company", "insurance", "package", "shop"))
               else "product")
        yield q(_best(item), category="Weddings", subcategory="weddings", family="wedding_best", entity=ent,
                priority=80, monetization="affiliate_retail", cadence="quarterly", product_category=item,
                geo_scope="national")


# --------------------------------------------------------------------------- #
# AGING & SENIOR CARE
# --------------------------------------------------------------------------- #

AGING_ITEMS = ["medical alert system", "fall detection device", "stair lift", "walk-in tub", "lift chair",
               "senior living community chain", "assisted living company", "memory care provider",
               "in-home care agency", "adult day care program", "senior meal delivery service",
               "brain training app", "cell phone plan for seniors", "tablet for seniors",
               "TV for seniors with hearing loss", "pill organizer", "automatic pill dispenser",
               "hearing aids for seniors", "shoes for seniors", "cane", "rollator walker",
               "senior travel company", "cruise for seniors", "Medicare plan finder",
               "long-term care insurance company", "estate planning service for seniors",
               "retirement community in Florida", "retirement community in Arizona",
               "part-time job for retirees", "hobby for retirees", "exercise program for seniors",
               "dating site for seniors", "caregiver support app"]


def gen_aging() -> Iterator[dict]:
    for item in AGING_ITEMS:
        ent = ("place_to_live" if "community" in item else
               "experience" if "hobby" in item or "job" in item else
               "software" if item.endswith("app") or "finder" in item else
               "service_provider" if any(w in item for w in ("agency", "company", "provider", "program",
                                                             "service", "plan", "chain", "site"))
               else "product")
        yield q(_best(item), category="Aging & Senior Care", subcategory="aging", family="aging_best",
                entity=ent, priority=80, monetization="lead_gen_cpa", cadence="quarterly",
                product_category=item, age_group="65+", geo_scope="national")


# --------------------------------------------------------------------------- #
# HOME IMPROVEMENT
# --------------------------------------------------------------------------- #

HOME_ITEMS = ["roofing material", "roofing shingle brand", "siding material", "window brand",
              "exterior door brand", "garage door brand", "kitchen cabinet brand", "countertop brand",
              "quartz countertop brand", "flooring for pets", "waterproof flooring", "luxury vinyl plank brand",
              "hardwood flooring brand", "carpet brand", "deck material", "composite decking brand",
              "fence material", "paver brand", "insulation type", "heat pump brand", "furnace brand",
              "air conditioner brand", "mini split brand", "water heater brand", "plumbing fixture brand",
              "kitchen faucet brand", "toilet brand", "shower system brand", "appliance package",
              "smart home system", "solar panel brand", "home battery brand", "generator brand",
              "home inspection service", "home renovation app", "contractor finding site",
              "kitchen remodel idea", "bathroom remodel idea", "home addition idea", "backyard makeover idea",
              "pool type", "above-ground pool", "landscaping idea for small yards", "shed brand",
              "ADU builder", "prefab home builder", "tiny home builder"]


def gen_home() -> Iterator[dict]:
    for item in HOME_ITEMS:
        ent = ("experience" if "idea" in item else
               "service_provider" if any(w in item for w in ("service", "site", "app", "builder"))
               else "product")
        yield q(_best(item), category="Home Improvement", subcategory="home_improvement", family="home_best",
                entity=ent, priority=80, monetization="lead_gen_cpa", cadence="quarterly",
                product_category=item, geo_scope="national")


# --------------------------------------------------------------------------- #
# LEGAL
# --------------------------------------------------------------------------- #

LEGAL_ITEMS = ["LLC formation service", "registered agent service", "trademark filing service",
               "online will maker", "living trust service", "online divorce service", "divorce mediation service",
               "prenuptial agreement service", "immigration lawyer service", "green card application service",
               "online legal advice service", "legal plan subscription", "small business legal service",
               "contract template site", "eviction service for landlords", "traffic ticket lawyer service",
               "DUI lawyer referral service", "personal injury law firm", "workers' compensation law firm",
               "Social Security disability lawyer", "bankruptcy lawyer service", "tax relief company",
               "tax attorney service", "patent filing service", "name change service",
               "custody lawyer service", "landlord-tenant lawyer service", "employment lawyer service",
               "medical malpractice law firm", "car accident lawyer service", "power of attorney service",
               "probate service", "nonprofit formation service", "EIN filing service", "online notary service"]


def gen_legal() -> Iterator[dict]:
    for item in LEGAL_ITEMS:
        yield q(_best(item), category="Legal", subcategory="legal", family="legal_best",
                entity="service_provider", priority=80, monetization="lead_gen_cpa", cadence="quarterly",
                product_category=item, geo_scope="national")


# --------------------------------------------------------------------------- #
# SPORTS BETTING & GAMING (21+)
# --------------------------------------------------------------------------- #

BETTING_ITEMS = ["sportsbook", "sportsbook app", "sportsbook promo right now", "sportsbook for parlays",
                 "sportsbook for live betting", "sportsbook for odds", "daily fantasy sports app",
                 "fantasy football app", "fantasy football draft kit", "online casino", "online casino bonus",
                 "sweepstakes casino", "poker site", "poker app", "prediction market app",
                 "horse racing betting app", "lottery app", "sports betting tool", "betting picks service",
                 "Las Vegas casino", "Atlantic City casino", "casino resort in the US"]


def gen_betting() -> Iterator[dict]:
    for item in BETTING_ITEMS:
        ent = "hotel" if "casino" in item and ("Vegas" in item or "Atlantic" in item or "resort" in item) \
            else "service_provider"
        yield q(_best(item), category="Betting & Gaming", subcategory="betting", family="betting_best",
                entity=ent, priority=82, monetization="cpa_affiliate",
                cadence="weekly" if "promo" in item or "bonus" in item else "monthly",
                product_category=item, age_group="21+", geo_scope="national")
