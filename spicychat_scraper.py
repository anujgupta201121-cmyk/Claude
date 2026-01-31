#!/usr/bin/env python3
"""
SpicyChat.ai Web Scraper
Scrapes chatbot data from spicychat.ai using their Typesense API.
Extracts: name, url, categories, creator, and quantitative stats.
Outputs data to a CSV file.
"""

import csv
import json
import time
import requests
from datetime import datetime
from typing import Optional, List, Dict


class SpicyChatScraper:
    BASE_URL = "https://spicychat.ai"
    API_URL = "https://etmzpxgvnid370fyp.a1.typesense.net/multi_search"
    API_KEY = "STHKtT6jrC5z1IozTJHIeSN4qN9oL1s3"

    # Characters per page in Typesense
    PER_PAGE = 24

    def __init__(self):
        self.characters_data = []
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        })

    def get_total_characters(self) -> int:
        """Get total number of characters available."""
        result = self._search(page=1, per_page=1)
        if result and "results" in result and len(result["results"]) > 0:
            found = result["results"][0].get("found", 0)
            print(f"Total characters available: {found}")
            return found
        return 0

    def get_max_pages(self) -> int:
        """Calculate maximum number of pages."""
        total = self.get_total_characters()
        max_pages = (total + self.PER_PAGE - 1) // self.PER_PAGE
        print(f"Maximum pages: {max_pages}")
        return max_pages

    def _search(self, page: int = 1, per_page: int = None, sort_by: str = "num_messages_24h:desc") -> dict:
        """Execute a search query against the Typesense API."""
        if per_page is None:
            per_page = self.PER_PAGE

        params = {
            "use_cache": "true",
            "x-typesense-api-key": self.API_KEY
        }

        # Typesense search request format
        payload = {
            "searches": [
                {
                    "collection": "public_characters_alias",
                    "q": "*",
                    "query_by": "name,title,persona",
                    "sort_by": sort_by,
                    "page": page,
                    "per_page": per_page,
                    "facet_by": "tags",
                    "max_facet_values": 100
                }
            ]
        }

        try:
            response = self.session.post(
                self.API_URL,
                params=params,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request error: {e}")
            return None

    def scrape_page(self, page_num: int) -> List[Dict]:
        """Scrape a single page of characters."""
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
        """Extract character data from a Typesense document."""
        # Get character ID for URL
        char_id = doc.get("id", "")

        data = {
            "name": doc.get("name", ""),
            "url": f"{self.BASE_URL}/chat/{char_id}" if char_id else "",
            "categories": "; ".join(doc.get("tags", [])) if doc.get("tags") else "",
            "creator": doc.get("creator_username", "") or doc.get("creator_id", ""),
            "messages_24h": str(doc.get("num_messages_24h", "")),
            "total_messages": str(doc.get("num_messages", "")),
            "likes": str(doc.get("num_likes", "") or doc.get("likes", "")),
            "description": doc.get("title", "") or doc.get("persona", "")[:500] if doc.get("persona") else "",
            "num_chats": str(doc.get("num_chats", "")),
            "num_users": str(doc.get("num_users", "")),
            "created_at": doc.get("created_at", ""),
            "avatar_url": doc.get("avatar_url", ""),
        }

        return data

    def scrape_all_pages(self, max_pages: int = None, start_page: int = 1):
        """Scrape all available pages."""
        # Get max pages if not specified
        if max_pages is None:
            max_pages = self.get_max_pages()

        print(f"\nStarting scrape from page {start_page} to {max_pages}")
        print("=" * 50)

        for page_num in range(start_page, max_pages + 1):
            characters = self.scrape_page(page_num)
            self.characters_data.extend(characters)

            # Save intermediate results every 50 pages
            if page_num % 50 == 0:
                self.save_to_csv(f"spicychat_backup_page{page_num}.csv")
                print(f"  Backup saved. Total characters so far: {len(self.characters_data)}")

            # Small delay to be respectful
            time.sleep(0.5)

        return self.characters_data

    def save_to_csv(self, filename: str = None):
        """Save scraped data to CSV file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"spicychat_characters_{timestamp}.csv"

        if not self.characters_data:
            print("No data to save!")
            return None

        # Define CSV columns
        fieldnames = [
            "name",
            "url",
            "categories",
            "creator",
            "messages_24h",
            "total_messages",
            "likes",
            "num_chats",
            "num_users",
            "description",
            "created_at",
            "avatar_url",
        ]

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(self.characters_data)

        print(f"\nSaved {len(self.characters_data)} characters to {filename}")
        return filename


def run(pages=None, start=1, output=None):
    """
    Run the scraper directly (for Jupyter notebooks).

    Args:
        pages: Maximum number of pages to scrape (None = auto-detect)
        start: Starting page number (default: 1)
        output: Output CSV filename (None = auto-generated)

    Returns:
        List of scraped character data

    Example:
        from spicychat_scraper import run
        data = run(pages=5)
    """
    print("SpicyChat.ai Scraper (API Mode)")
    print("=" * 50)
    print(f"Starting page: {start}")
    print(f"Max pages: {pages or 'auto-detect'}")
    print()

    scraper = SpicyChatScraper()

    try:
        scraper.scrape_all_pages(max_pages=pages, start_page=start)
        output_file = scraper.save_to_csv(output)

        print("\n" + "=" * 50)
        print("Scraping complete!")
        print(f"Total characters scraped: {len(scraper.characters_data)}")
        print(f"Output file: {output_file}")

        return scraper.characters_data

    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user.")
        print("Saving collected data...")
        scraper.save_to_csv("spicychat_interrupted.csv")
        return scraper.characters_data

    except Exception as e:
        print(f"\nError during scraping: {e}")
        print("Saving collected data...")
        if scraper.characters_data:
            scraper.save_to_csv("spicychat_error_backup.csv")
        raise


def main():
    """Main entry point for command line."""
    import argparse

    parser = argparse.ArgumentParser(description="Scrape SpicyChat.ai character data")
    parser.add_argument("--pages", type=int, default=None,
                        help="Maximum number of pages to scrape (default: auto-detect)")
    parser.add_argument("--start", type=int, default=1,
                        help="Starting page number (default: 1)")
    parser.add_argument("--output", type=str, default=None,
                        help="Output CSV filename")

    args = parser.parse_args()

    run(pages=args.pages, start=args.start, output=args.output)


if __name__ == "__main__":
    main()
