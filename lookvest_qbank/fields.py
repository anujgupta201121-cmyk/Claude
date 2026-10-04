"""
Answer schemas: what Lookvest extracts from every LLM answer, per entity type.

Each question points at one entity type. When an LLM answers, the tracker
parses out these fields so answers can be compared across models and over time
(the "consensus" is the most-cited value of the primary field).
"""

# entity_type -> (primary field, ordered extraction fields)
ANSWER_SCHEMAS: dict[str, tuple[str, list[str]]] = {
    "hotel": ("hotel_name", ["hotel_name", "brand", "neighborhood", "price_band",
                             "booking_source", "booking_url"]),
    "restaurant": ("restaurant_name", ["restaurant_name", "cuisine", "neighborhood",
                                       "price_band", "reservation_source", "reservation_url"]),
    "bar_venue": ("venue_name", ["venue_name", "venue_type", "neighborhood",
                                 "reservation_source", "url"]),
    "attraction": ("attraction_name", ["attraction_name", "attraction_type", "neighborhood",
                                       "ticket_source", "ticket_url", "price"]),
    "neighborhood": ("neighborhood", ["neighborhood", "recommended_hotel", "booking_source",
                                      "booking_url"]),
    "local_business": ("business_name", ["business_name", "business_type", "neighborhood",
                                         "booking_or_contact_source", "url", "rating_source"]),
    "product": ("product_name", ["product_name", "brand", "model", "price",
                                 "retailer", "product_url"]),
    "gift": ("product_name", ["product_name", "brand", "gift_category", "price",
                              "retailer", "product_url"]),
    "apparel": ("item", ["item", "brand_manufacturer", "style_trend", "price",
                         "retailer", "product_url"]),
    "food_list": ("foods", ["foods", "food_group", "key_nutrient", "reasoning_source"]),
    "diet_program": ("program_name", ["program_name", "provider", "signup_source", "url"]),
    "supplement": ("product_name", ["product_name", "brand", "form", "price",
                                    "retailer", "product_url"]),
    "media_title": ("title", ["title", "format", "genre", "streaming_service",
                              "where_to_watch_url", "release_year"]),
    "book": ("title", ["title", "author", "genre", "retailer", "product_url"]),
    "podcast": ("title", ["title", "host", "platform", "url"]),
    "video_game": ("title", ["title", "publisher", "platform", "retailer", "product_url"]),
    "financial_product": ("product_name", ["product_name", "provider", "key_rate_or_fee",
                                           "signup_source", "apply_url"]),
    "travel_brand": ("brand_name", ["brand_name", "specific_offering", "booking_source",
                                    "booking_url"]),
    "destination": ("destination", ["destination", "country", "recommended_hotel",
                                    "booking_source", "booking_url"]),
    "vehicle": ("model", ["make", "model", "trim", "model_year", "msrp",
                          "where_to_buy", "url"]),
    "software": ("product_name", ["product_name", "vendor", "pricing_tier",
                                  "signup_source", "url"]),
    "service_provider": ("provider", ["provider", "plan", "price", "signup_source", "url"]),
    "institution": ("institution", ["institution", "program", "location", "apply_url"]),
    "place_to_live": ("place", ["place", "state_or_country", "reason", "listing_source"]),
    "pet_breed": ("breed", ["breed", "size", "temperament", "adoption_or_breeder_source"]),
}


def fields_for(entity_type: str) -> tuple[str, str]:
    primary, fields = ANSWER_SCHEMAS[entity_type]
    return primary, "|".join(fields)
