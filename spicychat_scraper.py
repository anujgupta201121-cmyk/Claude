#!/usr/bin/env python3
"""
SpicyChat.ai Web Scraper
Scrapes chatbot data from spicychat.ai public characters listing.
Extracts: name, url, categories, creator, and quantitative stats.
Outputs data to a CSV file.
"""

import asyncio
import csv
import re
import time
from datetime import datetime
from typing import Optional

try:
    from playwright.async_api import async_playwright, Page, Browser
except ImportError:
    print("Playwright is not installed. Install it with:")
    print("  pip install playwright")
    print("  playwright install chromium")
    exit(1)


class SpicyChatScraper:
    BASE_URL = "https://spicychat.ai"
    CHARACTERS_URL = "https://spicychat.ai/?public_characters_alias%2Fsort%2Fnum_messages_24h%3Adesc%5Bpage%5D={page}"

    def __init__(self, headless: bool = True, slow_mo: int = 100):
        self.headless = headless
        self.slow_mo = slow_mo
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.characters_data = []

    async def init_browser(self):
        """Initialize the Playwright browser."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo
        )
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        self.page = await self.context.new_page()

    async def close_browser(self):
        """Close the browser and cleanup."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def get_max_pages(self) -> int:
        """Detect the maximum number of pages available."""
        await self.page.goto(self.CHARACTERS_URL.format(page=1), wait_until="networkidle")
        await asyncio.sleep(2)  # Wait for dynamic content

        # Try to find pagination elements
        # Common patterns: page numbers, "last" button, or total count
        max_page = 1

        # Look for pagination buttons/links
        pagination_selectors = [
            '[class*="pagination"] a',
            '[class*="pagination"] button',
            '[class*="page"] a',
            'nav[aria-label*="pagination"] a',
            'a[href*="page"]',
            'button[aria-label*="page"]',
            '[data-page]',
        ]

        for selector in pagination_selectors:
            try:
                elements = await self.page.query_selector_all(selector)
                for el in elements:
                    text = await el.text_content()
                    if text and text.strip().isdigit():
                        page_num = int(text.strip())
                        max_page = max(max_page, page_num)
                    # Check href for page numbers
                    href = await el.get_attribute("href")
                    if href:
                        match = re.search(r'page[=\]]+(\d+)', href)
                        if match:
                            page_num = int(match.group(1))
                            max_page = max(max_page, page_num)
            except Exception:
                continue

        # Also try to find "showing X of Y" or similar text
        try:
            page_text = await self.page.content()
            # Look for patterns like "Page 1 of 100" or "1/100"
            matches = re.findall(r'(?:of|/)\s*(\d+)\s*(?:pages?)?', page_text, re.IGNORECASE)
            for match in matches:
                try:
                    num = int(match)
                    if num > max_page and num < 10000:  # Sanity check
                        max_page = num
                except ValueError:
                    continue
        except Exception:
            pass

        print(f"Detected maximum pages: {max_page}")
        return max_page

    async def scrape_page(self, page_num: int) -> list:
        """Scrape all characters from a single page."""
        characters = []
        url = self.CHARACTERS_URL.format(page=page_num)

        print(f"Scraping page {page_num}...")

        try:
            await self.page.goto(url, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(3)  # Wait for dynamic content to load

            # Try multiple selectors for character cards
            card_selectors = [
                '[class*="character-card"]',
                '[class*="CharacterCard"]',
                '[class*="bot-card"]',
                '[class*="card"]',
                'article',
                '[data-testid*="character"]',
                'a[href*="/chat/"]',
                '[class*="grid"] > div > a',
                '[class*="character"]',
            ]

            cards = []
            for selector in card_selectors:
                try:
                    cards = await self.page.query_selector_all(selector)
                    if len(cards) > 5:  # Found meaningful results
                        print(f"  Found {len(cards)} cards using selector: {selector}")
                        break
                except Exception:
                    continue

            if not cards:
                # Fallback: look for links containing /chat/
                cards = await self.page.query_selector_all('a[href*="/chat/"]')
                print(f"  Fallback: Found {len(cards)} chat links")

            for card in cards:
                try:
                    char_data = await self.extract_character_data(card)
                    if char_data and char_data.get("name"):
                        characters.append(char_data)
                except Exception as e:
                    print(f"  Error extracting card data: {e}")
                    continue

        except Exception as e:
            print(f"Error scraping page {page_num}: {e}")

        print(f"  Extracted {len(characters)} characters from page {page_num}")
        return characters

    async def extract_character_data(self, card) -> dict:
        """Extract data from a single character card."""
        data = {
            "name": "",
            "url": "",
            "categories": "",
            "creator": "",
            "messages_24h": "",
            "total_messages": "",
            "likes": "",
            "description": "",
        }

        try:
            # Get the card's outer HTML for debugging
            outer_html = await card.evaluate("el => el.outerHTML")

            # Extract name - try multiple approaches
            name_selectors = [
                '[class*="name"]',
                '[class*="title"]',
                'h2', 'h3', 'h4',
                '[class*="heading"]',
                'strong',
                '[class*="character-name"]',
            ]

            for sel in name_selectors:
                try:
                    name_el = await card.query_selector(sel)
                    if name_el:
                        name = await name_el.text_content()
                        if name and name.strip():
                            data["name"] = name.strip()
                            break
                except Exception:
                    continue

            # If no name found, try getting text from the card itself
            if not data["name"]:
                text = await card.text_content()
                if text:
                    # Take first line or first few words as name
                    lines = [l.strip() for l in text.split('\n') if l.strip()]
                    if lines:
                        data["name"] = lines[0][:100]  # Limit length

            # Extract URL
            try:
                href = await card.get_attribute("href")
                if href:
                    if href.startswith("/"):
                        data["url"] = self.BASE_URL + href
                    else:
                        data["url"] = href
                else:
                    # Look for nested link
                    link = await card.query_selector("a")
                    if link:
                        href = await link.get_attribute("href")
                        if href:
                            data["url"] = self.BASE_URL + href if href.startswith("/") else href
            except Exception:
                pass

            # Extract creator/author
            creator_selectors = [
                '[class*="creator"]',
                '[class*="author"]',
                '[class*="by"]',
                '[class*="user"]',
                'a[href*="/profile/"]',
                'a[href*="/user/"]',
                '[class*="username"]',
            ]

            for sel in creator_selectors:
                try:
                    creator_el = await card.query_selector(sel)
                    if creator_el:
                        creator = await creator_el.text_content()
                        if creator and creator.strip():
                            # Clean up "by" prefix if present
                            creator = re.sub(r'^by\s+', '', creator.strip(), flags=re.IGNORECASE)
                            data["creator"] = creator
                            break
                except Exception:
                    continue

            # Extract categories/tags
            tag_selectors = [
                '[class*="tag"]',
                '[class*="category"]',
                '[class*="badge"]',
                '[class*="chip"]',
                '[class*="label"]',
            ]

            tags = []
            for sel in tag_selectors:
                try:
                    tag_els = await card.query_selector_all(sel)
                    for tag_el in tag_els:
                        tag_text = await tag_el.text_content()
                        if tag_text and tag_text.strip():
                            tags.append(tag_text.strip())
                except Exception:
                    continue

            if tags:
                data["categories"] = "; ".join(set(tags))

            # Extract stats (messages, likes, etc.)
            stats_selectors = [
                '[class*="stat"]',
                '[class*="count"]',
                '[class*="number"]',
                '[class*="metric"]',
            ]

            stats_text = []
            for sel in stats_selectors:
                try:
                    stat_els = await card.query_selector_all(sel)
                    for stat_el in stat_els:
                        stat = await stat_el.text_content()
                        if stat and stat.strip():
                            stats_text.append(stat.strip())
                except Exception:
                    continue

            # Parse stats from text - look for numbers with K/M suffixes
            full_text = await card.text_content() or ""

            # Look for message counts
            msg_patterns = [
                r'(\d+(?:\.\d+)?[KkMm]?)\s*(?:messages?|msgs?|chats?)',
                r'(?:messages?|msgs?|chats?)[\s:]*(\d+(?:\.\d+)?[KkMm]?)',
            ]
            for pattern in msg_patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    data["total_messages"] = match.group(1)
                    break

            # Look for 24h stats
            h24_patterns = [
                r'(\d+(?:\.\d+)?[KkMm]?)\s*(?:24h|daily|today)',
                r'(?:24h|daily|today)[\s:]*(\d+(?:\.\d+)?[KkMm]?)',
            ]
            for pattern in h24_patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    data["messages_24h"] = match.group(1)
                    break

            # Look for likes/favorites
            like_patterns = [
                r'(\d+(?:\.\d+)?[KkMm]?)\s*(?:likes?|❤|♥|favorites?)',
                r'(?:likes?|❤|♥|favorites?)[\s:]*(\d+(?:\.\d+)?[KkMm]?)',
            ]
            for pattern in like_patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    data["likes"] = match.group(1)
                    break

            # Extract description if available
            desc_selectors = [
                '[class*="description"]',
                '[class*="desc"]',
                '[class*="bio"]',
                '[class*="summary"]',
                'p',
            ]

            for sel in desc_selectors:
                try:
                    desc_el = await card.query_selector(sel)
                    if desc_el:
                        desc = await desc_el.text_content()
                        if desc and desc.strip() and len(desc.strip()) > 20:
                            data["description"] = desc.strip()[:500]  # Limit length
                            break
                except Exception:
                    continue

        except Exception as e:
            print(f"    Error in extract_character_data: {e}")

        return data

    async def scrape_all_pages(self, max_pages: int = None, start_page: int = 1):
        """Scrape all available pages."""
        await self.init_browser()

        try:
            # Detect max pages if not specified
            if max_pages is None:
                max_pages = await self.get_max_pages()

            print(f"\nStarting scrape from page {start_page} to {max_pages}")
            print("=" * 50)

            for page_num in range(start_page, max_pages + 1):
                characters = await self.scrape_page(page_num)
                self.characters_data.extend(characters)

                # Save intermediate results every 10 pages
                if page_num % 10 == 0:
                    self.save_to_csv(f"spicychat_backup_page{page_num}.csv")
                    print(f"  Backup saved. Total characters so far: {len(self.characters_data)}")

                # Rate limiting - be respectful
                await asyncio.sleep(2)

        finally:
            await self.close_browser()

        return self.characters_data

    def save_to_csv(self, filename: str = None):
        """Save scraped data to CSV file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"spicychat_characters_{timestamp}.csv"

        if not self.characters_data:
            print("No data to save!")
            return

        # Define CSV columns
        fieldnames = [
            "name",
            "url",
            "categories",
            "creator",
            "messages_24h",
            "total_messages",
            "likes",
            "description"
        ]

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(self.characters_data)

        print(f"\nSaved {len(self.characters_data)} characters to {filename}")
        return filename


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Scrape SpicyChat.ai character data")
    parser.add_argument("--pages", type=int, default=None,
                        help="Maximum number of pages to scrape (default: auto-detect)")
    parser.add_argument("--start", type=int, default=1,
                        help="Starting page number (default: 1)")
    parser.add_argument("--output", type=str, default=None,
                        help="Output CSV filename")
    parser.add_argument("--visible", action="store_true",
                        help="Run browser in visible mode (not headless)")

    args = parser.parse_args()

    print("SpicyChat.ai Scraper")
    print("=" * 50)
    print(f"Headless mode: {not args.visible}")
    print(f"Starting page: {args.start}")
    print(f"Max pages: {args.pages or 'auto-detect'}")
    print()

    scraper = SpicyChatScraper(headless=not args.visible)

    try:
        await scraper.scrape_all_pages(max_pages=args.pages, start_page=args.start)
        output_file = scraper.save_to_csv(args.output)

        print("\n" + "=" * 50)
        print("Scraping complete!")
        print(f"Total characters scraped: {len(scraper.characters_data)}")
        print(f"Output file: {output_file}")

    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user.")
        print("Saving collected data...")
        scraper.save_to_csv("spicychat_interrupted.csv")

    except Exception as e:
        print(f"\nError during scraping: {e}")
        print("Saving collected data...")
        scraper.save_to_csv("spicychat_error_backup.csv")
        raise


if __name__ == "__main__":
    asyncio.run(main())
