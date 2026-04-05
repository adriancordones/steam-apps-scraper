import re
import scrapy
from scrapy import Request
from datetime import datetime

from steam_scraper.items import AppItem
from utils import get_text, join_fields, split_first, parse_value, set_price

class AppsSpider(scrapy.Spider):
    """
    Scrapes metadata for Steam apps from their store pages.

    Args:
        app_ids (list | str): List of Steam App IDs to scrape. When using the
            Scrapy CLI, pass as a comma-separated string (e.g. "413150,730").
        labels (str, optional): URL query string for filters. Defaults to URL_LABELS.
    """
    name = "apps"
    allowed_domains = ["store.steampowered.com"]
    
    REQUIRED = ["id", "url", "title", "date", "original_price", "dlcs_number", "has_ost", "is_dlc", "is_ost"]
    DEV_MAP = {
        "desarrollador": ("developer_name", "developer_url"),
        "editor": ("publisher_name", "publisher_url"),
        "developer": ("developer_name", "developer_url"),
        "publisher": ("publisher_name", "publisher_url")
    }
    # Default: website lang. spanish
    URL_LABELS = "?l=es"
    # Age Cookie
    AGE_COOKIE = {
        "birthtime": str(int(datetime(1999, 6, 11).timestamp())),
        "wants_mature_content": "1"
    }

    def __init__(self, app_ids=None, labels=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if isinstance(app_ids, str):
            # When using Scrapy CLI
            self.app_ids = app_ids.split(",")
        else:
            # When using main file
            self.app_ids = app_ids or []
        self.labels = labels or self.URL_LABELS
        self.errors = []

    async def start(self):
        if not self.app_ids:
            self.logger.error("Missing app ids!")
            return
        for app_id in self.app_ids:
            url = f"https://store.steampowered.com/app/{app_id}/{self.labels}"
            yield Request(url=url, callback=self.parse, cookies=self.AGE_COOKIE)

    def parse(self, response):
        app = AppItem()

        # Save URL
        app.url = split_first(response.url, "?")
        # Extract ID
        match = re.search(r"/app/(\d+)/", response.url)
        app_id = match.group(1)
        app.id = int(app_id) if app_id else None
        # Extract Title, Release Date and Description
        app.title = response.css("#appHubAppName::text").get()
        app.date = response.css("#glanceMidCtn div.date::text").get()
        app.short_desc = get_text(response.css("#gameHeaderCtn div.game_description_snippet::text"), trim=True)
        # Extract Developer and Publisher info (names and URLs)
        dev_rows = response.css("#glanceMidCtn div.dev_row")
        for row in dev_rows:
            dev_type = get_text(row.css("div.subtitle.column::text"), default="").rstrip(":").lower()
            dev_data = row.css("div.summary.column a")
            if dev_type not in self.DEV_MAP:
                self.logger.warning(f"Wrong dev_type for app_id={app_id}: '{dev_type}'.")
                continue
            name_field, url_field = self.DEV_MAP[dev_type]
            raw_url = split_first(get_text(dev_data.css("::attr(href)"), default=""), "?")
            setattr(app, name_field, dev_data.css("::text").get())
            setattr(app, url_field, None if raw_url == "https://store.steampowered.com/search/" else raw_url)
        # Extract Tags and Genres
        tags = [tag.strip() for tag in response.css("#glanceCtnResponsiveRight div.popular_tags a::text").getall()]
        app.tags = join_fields(tags)
        genres = [genre.strip() for genre in response.css("#genresAndManufacturer span a::text").getall()]
        app.genres = join_fields(genres)
        # Extract Price and Discount (if applied)
        price_wrapper = response.css("#game_area_purchase div.game_area_purchase_game_wrapper")
        if not price_wrapper:
            self.logger.warning(f"No price wrapper found for app_id={app_id}.")
        else:
            price_area = price_wrapper[0]
            regular_price = get_text(price_area.css("div.game_purchase_price.price::text"), trim=True)
            original_price = get_text(price_area.css("div.discount_original_price::text"), trim=True)
            discount_price = get_text(price_area.css("div.discount_final_price::text"), trim=True)
            discount = get_text(price_area.css("div.discount_pct::text"), trim=True)
            if regular_price:
                set_price(app, regular_price, None, None)
            elif original_price and discount_price and discount:
                set_price(app, original_price, discount_price, discount)
            else:
                self.logger.warning(f"Unexpected price structure for app_id={app_id}.")
        # Extract Achievements numbers
        achievement_text = response.css("#achievement_block div.block_title::text").get()
        app.achievements_number = parse_value(achievement_text, default=0, to_int=True)
        # Extract DLCs, number and relevant booleans
        dlcs = response.css("#gameAreaDLCSection div.game_area_dlc_name::text").getall()
        app_dlcs = [dlc.strip() for dlc in dlcs if dlc.strip() and not dlc.strip().lower().endswith("soundtrack")]
        app.dlcs = join_fields(app_dlcs)
        app.dlcs_number = len(app_dlcs) if app_dlcs else 0
        app.has_ost = any(dlc.strip().lower().endswith("soundtrack") for dlc in dlcs)
        app.is_dlc = bool(response.css("#game_area_purchase div.game_area_dlc_bubble"))
        app.is_ost = bool(response.css("#game_area_purchase div.game_area_soundtrack_bubble"))
        # Extract Languages and number
        languages = response.css("#languageTable tr:not(.unsupported) td.ellipsis::text").getall()
        app_languages = [lang.strip() for lang in languages]
        app.languages = join_fields(app_languages)
        app.langs_number = len(app_languages) if app_languages else None
        # Extract Reviews metadata
        review_area = response.css("#app_reviews_hash")
        review_rows = response.css("div.outlier_totals")
        rows_summaries = review_rows.css("span.game_review_summary::text").getall()
        if review_rows and rows_summaries:
            counts = review_rows.css("span.review_summary_count::text").getall()
            self.logger.debug(f"app_id={app_id} | counts={counts} | summaries={rows_summaries}")
            if len(counts) == 2 and len(rows_summaries) == 2:
                app.reviews_total, app.reviews_recent = [parse_value(count, to_int=True) for count in counts]
                app.reviews_total_summary, app.reviews_recent_summary = rows_summaries
            elif len(counts) == 1 and len(rows_summaries) == 1:
                app.reviews_total = parse_value(counts[0], to_int=True)
                app.reviews_total_summary = rows_summaries[0]
                app.reviews_recent = None
                app.reviews_recent_summary = None
            else:
                self.logger.warning(f"Unexpected review structure (with rows) for app_id={app_id}.")
        else:
            no_reviews = bool(review_area.css("div.noReviewsYetTitle, span.game_review_summary.no_reviews"))
            app.reviews_recent = app.reviews_recent_summary = None
            
            not_enough = review_area.css("span.game_review_summary.not_enough_reviews")
            summary = review_area.css("span.game_review_summary:not(.no_reviews):not(.not_enough_reviews)")
            if no_reviews:
                app.reviews_total = 0
                app.reviews_total_summary = "No hay reseñas"
            elif summary or not_enough:
                app.reviews_total = parse_value(get_text(review_area.css("span.app_reviews_count::text"), default=""), to_int=True)
                app.reviews_total_summary = None if not_enough else summary.css("::text").get()
            else:
                self.logger.warning(f"Unexpected review structure (without rows) for app_id={app_id}.")
        # Check which required fields are missing
        missing = [f for f in self.REQUIRED if getattr(app, f) is None]
        if missing:
            self.errors.append({"app_id": app_id, "missing_fields": missing})
            return
        
        yield app
    
    def closed(self, reason):
        if self.errors:
            self.logger.warning("Scraping Apps metadata finished with missing fields:")
            for error in self.errors:
                missing = ', '.join(error['missing_fields'])
                self.logger.warning(f"\tapp_id={error['app_id']} | missing: {missing}.")
        else:
            if reason == "finished":
                self.logger.info(f"Apps metadata scraped successfully! (total={len(self.app_ids)})")
            else:
                self.logger.warning(f"Spider closed unexpectedly ({reason}). No missing fields detected.")