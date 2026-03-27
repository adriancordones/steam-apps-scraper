import os
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
        
        self.file_path = "apps_urls.json"
        self.developer = "desarrollador"
        self.editor = "editor"

    async def start(self):
        with open(self.file_path, 'r') as f:
            urls = json.load(f)
        
        for url in urls:
            yield Request(url=url, callback=self.parse_metadata)

    def parse_metadata(self, response):
        # TODO: Cookie o login para juegos +18

        app = AppItem()

        app_url = response.url
        app.game_link = app_url

        match = re.search(r"/app/(\d+)/", app_url)
        app_id = match.group(1) if match else None
        app.id = app_id

        app.title = response.css("#appHubAppName::text").get()
        app.short_desc = response.css("#gameHeaderCtn .game_description_snippet::text").get().strip()
        app.date = response.css("#glanceMidCtn .date::text").get()
         
        dev_rows = response.css("#glanceMidCtn .dev_row")
        for row in dev_rows:
            dev_type = row.css("div.subtitle.column::text").get().strip().rstrip(":").lower()
            dev_data = row.css("div.summary.column a")
            
            if dev_type == self.developer:
                app.developer_name = dev_data.css("::text").get()
                app.developer_link = dev_data.css("::attr(href)").get().split("?")[0]
            elif dev_type == self.editor:
                app.editor_name = dev_data.css("::text").get()
                app.editor_link = dev_data.css("::attr(href)").get().split("?")[0]
            else:
                logging.warning(f"Wrong dev_type: '{dev_type}'")
        
        tags = response.css("#glanceCtnResponsiveRight .popular_tags a::text").getall()
        app_tags = []
        for tag in tags:
            app_tags.append(tag.strip())
        app.tags = app_tags

        # TODO: Revisar variables como esta que pueden variar si no se separa por regional
        total_reviews = response.css("#app_reviews_hash div.outlier_totals.global.review_box_background_secondary span.review_summary_count::text").get()
        app.total_reviews = int(total_reviews.replace(".", ""))
        
        yield app