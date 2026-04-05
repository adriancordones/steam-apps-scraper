import re
import scrapy
from scrapy import Request
from datetime import datetime

from steam_scraper.items import AppItem
from utils import get_text, join_fields, split_first, parse_value, set_price

class AppsSpider(scrapy.Spider):
    name = "apps"
    
    URL_LABELS = "?l=es"
    REQUIRED = ["id", "url", "title", "date", "original_price", "short_desc",
                "dlcs_number", "has_ost", "is_dlc", "is_ost"]
    DEV_MAP = {
        "desarrollador": ("developer_name", "developer_url"),
        "editor": ("publisher_name", "publisher_url"),
    }
    
    # Age cookie
    birth_date = str(int(datetime(1999, 6, 11).timestamp()))
    AGE_COOKIE = {
        "birthtime": birth_date,
        "wants_mature_content": "1"
    }

    def __init__(self, app_ids=None, error_ids=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if isinstance(app_ids, str):
            self.app_ids = app_ids.split(",")
        else:
            self.app_ids = app_ids or []
        self.errors = []

    async def start(self):
        if not self.app_ids:
            self.logger.error("Missing app ids")
            return
        for app_id in self.app_ids:
            url = f"https://store.steampowered.com/app/{app_id}/{self.URL_LABELS}"
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
                self.logger.warning(f"Wrong dev_type for app_id={app_id}: '{dev_type}'")
                continue
            name_field, url_field = self.DEV_MAP[dev_type]
            setattr(app, name_field, dev_data.css("::text").get())
            setattr(app, url_field, split_first(get_text(dev_data.css("::attr(href)"), default=""), "?"))
        # Extract Tags and Genres
        tags = [tag.strip() for tag in response.css("#glanceCtnResponsiveRight div.popular_tags a::text").getall()]
        app.tags = join_fields(tags)
        genres = [genre.strip() for genre in response.css("#genresAndManufacturer span a::text").getall()]
        app.genres = join_fields(genres)
        # Extract Price and Discount (if applied)
        price_wrapper = response.css("#game_area_purchase div.game_area_purchase_game_wrapper")
        if not price_wrapper:
            self.logger.warning(f"No price wrapper found for app_id={app_id}")
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
                self.logger.warning(f"Unexpected price structure for app_id={app_id}")
        # Extract Achievements numbers
        achievement_text = response.css("#achievement_block div.block_title::text").get()
        if achievement_text:
            app.achievements_number = int(re.search(r"\d+", achievement_text).group())
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
        if review_rows:
            counts = review_rows.css("span.review_summary_count::text").getall()
            summaries = review_rows.css("span.game_review_summary::text").getall()
            if len(counts) == 2 and len(summaries) == 2:
                app.reviews_total, app.reviews_recent = [parse_value(count, to_int=True) for count in counts]
                app.reviews_total_summary, app.reviews_recent_summary = summaries
            else:
                self.logger.warning(f"Unexpected review structure (with rows) for app_id={app_id}")
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
                self.logger.warning(f"Unexpected review structure (without rows) for app_id={app_id}")
        # Check which required fields are missing
        missing = [f for f in self.REQUIRED if getattr(app, f) is None]
        if missing:
            self.errors.append({"app_id": app_id, "missing_fields": missing})
        
        yield app
    
    def closed(self, reason):
        if self.errors:
            self.logger.warning("Scraping finished with missing fields:")
            for error in self.errors:
                self.logger.warning(f"app_id={error['app_id']} | missing: {', '.join(error['missing_fields'])}")
        else:
            self.logger.info("All items scraped successfully!")