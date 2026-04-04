import re
import json
import logging
import scrapy
from scrapy import Request

from steam_scraper.items import AppItem


class AppsSpider(scrapy.Spider):
    name = "apps"

    def __init__(self, category=None, *args, **kwargs):
        super(AppsSpider, self).__init__(*args, **kwargs)
        self.urls = None

        self.file_path = "apps_urls.json"
        self.developer = "desarrollador"
        self.editor = "editor"

    async def start(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            self.urls = json.load(f)

        for entry in self.urls:
            if isinstance(entry, dict):
                url = entry.get("url")
            else:
                url = entry

            if url:
                yield Request(url=url, callback=self.parse_metadata)

    def parse_metadata(self, response):
        app = AppItem()

        app_url = response.url
        app.game_link = app_url

        match = re.search(r"/app/(\d+)/", app_url)
        app.id = match.group(1) if match else None

        title = response.css("#appHubAppName::text").get()
        app.title = title.strip() if title else None

        short_desc = response.css("#gameHeaderCtn .game_description_snippet::text").get()
        app.short_desc = short_desc.strip() if short_desc else None

        date = response.css("#glanceMidCtn .date::text").get()
        app.date = date.strip() if date else None

        dev_rows = response.css("#glanceMidCtn .dev_row")
        for row in dev_rows:
            dev_type_raw = row.css("div.subtitle.column::text").get()
            if not dev_type_raw:
                continue

            dev_type = dev_type_raw.strip().rstrip(":").lower()
            dev_data = row.css("div.summary.column a")

            dev_name = dev_data.css("::text").get()
            dev_link = dev_data.css("::attr(href)").get()
            if dev_link:
                dev_link = dev_link.split("?")[0]

            if dev_type == self.developer:
                app.developer_name = dev_name
                app.developer_link = dev_link
            elif dev_type == self.editor:
                app.editor_name = dev_name
                app.editor_link = dev_link
            else:
                logging.warning(f"Wrong dev_type: '{dev_type}'")

        tags = response.css("#glanceCtnResponsiveRight .popular_tags a::text").getall()
        app.tags = " | ".join(tag.strip() for tag in tags if tag.strip())

        total_reviews = response.css(
            "#app_reviews_hash div.outlier_totals.global.review_box_background_secondary span.review_summary_count::text"
        ).get()

        if total_reviews:
            cleaned_reviews = total_reviews.replace(".", "").replace(",", "").strip()
            app.total_reviews = int(cleaned_reviews) if cleaned_reviews.isdigit() else None
        else:
            app.total_reviews = None

        # Solo guardar filas que tengan contenido útil
        if app.title or app.short_desc:
            yield app