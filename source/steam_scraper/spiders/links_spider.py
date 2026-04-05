import scrapy
from scrapy import Request

from utils import parse_value

class LinksSpider(scrapy.Spider):
    """
    Scrapes app IDs from the Steam store search results.

    Args:
        srt_page (int): First search results page to scrape.
        end_page (int): Last search results page to scrape (inclusive).
        app_ids (list, optional): Existing list to extend with new IDs.
        labels (str, optional): URL query string for filters. Defaults to URL_LABELS.
    """
    name = "urls"
    allowed_domains = ["store.steampowered.com"]

    # Default: hide Free2Play, not default lang. (in games) and website lang. spanish
    URL_LABELS = "?hidef2p=1&ndl=1&l=es"

    def __init__(self, srt_page=1, end_page=1, labels=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app_ids = []
        self.srt_page = int(srt_page)
        self.end_page = int(end_page)
        self.labels = labels or self.URL_LABELS

    async def start(self):
        if self.srt_page > self.end_page:
            self.logger.error("Wrong start and end page values.")
            return
        for num in range(self.srt_page, self.end_page + 1):
            url = f"https://store.steampowered.com/search/results/{self.labels}&page={num}"
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        app_ids = response.css("a.search_result_row.ds_collapse_flag::attr(data-ds-appid)").getall()
        app_ids = [parse_value(app_id, to_int=True) for app_id in app_ids]
        self.app_ids.extend(app_ids)
    
    def closed(self, reason):
        if reason == "finished":
            self.logger.info(f"Apps IDs scraped successfully! (total={len(self.app_ids)})")
            self.logger.debug(f"Apps IDs: {self.app_ids}.")
        else:
            self.logger.warning(f"Spider closed unexpectedly ({reason}). No missing fields detected.")