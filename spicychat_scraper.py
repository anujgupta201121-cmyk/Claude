#!/usr/bin/env python3
"""
SpicyChat.ai Web Scraper
Scrapes chatbot data from spicychat.ai using their Typesense API.
Extracts: name, url, categories, creator, and quantitative stats.
Outputs data to a CSV file.
"""

import csv
import time
import requests
from datetime import datetime
from typing import List, Dict


class SpicyChatScraper:
    BASE_URL = "https://spicychat.ai"
    API_URL = "https://etmzpxgvnid370fyp.a1.typesense.net/multi_search"
    API_KEY = "STHKtT6jrC5z1IozTJHIeSN4qN9oL1s3"
    PER_PAGE = 24

    def __init__(self):
        self.characters_data = []
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        })

    def get_total_characters(self) -> int:
        result = self._search(page=1, per_page=1)
        if result and "results" in result and len(result["results"]) > 0:
            found = result["results"][0].get("found", 0)
            print(f"Total characters available: {found}")
            return found
        return 0

    def get_max_pages(self) -> int:
        total = self.get_total_characters()
        max_pages = (total + self.PER_PAGE - 1) // self.PER_PAGE
        print(f"Maximum pages: {max_pages}")
        return max_pages

    def _search(self, page: int = 1, per_page: int = None, sort_by: str = "num_messages_24h:desc") -> dict:
        if per_page is None:
            per_page = self.PER_PAGE

        params = {
            "use_cache": "true",
            "x-typesense-api-key": self.API_KEY
        }

        payload = {
            "searches": [
                {
                    "collection": "public_characters_alias",
                    "q": "*",
                    "sort_by": sort_by,
                    "page": page,
                    "per_page": per_page,
                }
            ]
        }

        try:
            response = self.session.post(self.API_URL, params=params, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request error: {e}")
            return None

    def scrape_page(self, page_num: int) -> List[Dict]:
        characters = []
        print(f"Scraping page {page_num}...")

        result = self._search(page=page_num)
        if not result or "results" not in result:
            print(f"  No results for page {page_num}")
            return characters

        hits = result["results"][0].get("hits", [])
        for hit in hits:
            doc = hit.get("document", {})
            char_data = self.extract_character_data(doc)
            if char_data.get("name"):
                characters.append(char_data)

        print(f"  Extracted {len(characters)} characters from page {page_num}")
        return characters

    def extract_character_data(self, doc: dict) -> dict:
        char_id = doc.get("character_id", "") or doc.get("id", "")
        tags = doc.get("tags", [])

        # Convert timestamp to readable date
        created_ts = doc.get("createdAt", 0)
        if created_ts:
            try:
                created_date = datetime.fromtimestamp(created_ts / 1000).strftime("%Y-%m-%d %H:%M:%S")
            except:
                created_date = str(created_ts)
        else:
            created_date = ""

        return {
            "name": doc.get("name", ""),
            "url": f"{self.BASE_URL}/chat/{char_id}" if char_id else "",
            "title": doc.get("title", ""),
            "categories": "; ".join(tags) if tags else "",
            "creator": doc.get("creator_username", ""),
            "num_messages_24h": doc.get("num_messages_24h", 0),
            "num_messages": doc.get("num_messages", 0),
            "rating_score": doc.get("rating_score", 0),
            "is_nsfw": doc.get("is_nsfw", False),
            "language": doc.get("language", ""),
            "token_count": doc.get("token_count", 0),
            "lora_status": doc.get("lora_status", ""),
            "type": doc.get("type", ""),
            "visibility": doc.get("visibility", ""),
            "group_size_category": doc.get("group_size_category", ""),
            "created_at": created_date,
            "avatar_url": f"https://spicychat.ai/{doc.get('avatar_url', '')}" if doc.get('avatar_url') else "",
            "greeting": doc.get("greeting", "")[:500] if doc.get("greeting") else "",
        }

    def scrape_all_pages(self, max_pages: int = None, start_page: int = 1):
        if max_pages is None:
            max_pages = self.get_max_pages()

        print(f"\nStarting scrape from page {start_page} to {max_pages}")
        print("=" * 50)

        for page_num in range(start_page, max_pages + 1):
            characters = self.scrape_page(page_num)
            self.characters_data.extend(characters)

            if page_num % 50 == 0:
                self.save_to_csv(f"spicychat_backup_page{page_num}.csv")
                print(f"  Backup saved. Total characters so far: {len(self.characters_data)}")

            time.sleep(0.3)

        return self.characters_data

    def save_to_csv(self, filename: str = None):
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"spicychat_characters_{timestamp}.csv"

        if not self.characters_data:
            print("No data to save!")
            return None

        fieldnames = [
            "name", "url", "title", "categories", "creator",
            "num_messages_24h", "num_messages", "rating_score",
            "is_nsfw", "language", "token_count", "lora_status",
            "type", "visibility", "group_size_category",
            "created_at", "avatar_url", "greeting"
        ]

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(self.characters_data)

        print(f"\nSaved {len(self.characters_data)} characters to {filename}")
        return filename


# === RUN THE SCRAPER ===
if __name__ == "__main__":
    scraper = SpicyChatScraper()
    scraper.scrape_all_pages(max_pages=5)  # Change to None for ALL pages
    scraper.save_to_csv("spicychat_data.csv")
