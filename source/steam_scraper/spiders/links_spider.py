import scrapy
from urllib.parse import urlsplit, urlunsplit


class LinksSpider(scrapy.Spider):
    name = "urls"
    allowed_domains = ["store.steampowered.com"]
    start_urls = [
        "https://store.steampowered.com/search/?supportedlang=spanish&ndl=1"
    ]

    def parse(self, response):
        game_links = response.css("a[href*='/app/']::attr(href)").getall()

        seen = set()

        for link in game_links:
            clean_link = self.clean_app_url(link)

            if clean_link and clean_link not in seen:
                seen.add(clean_link)
                yield {"url": clean_link}

        next_page = response.css("a.search_pagination_btn::attr(href)").get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def clean_app_url(self, url):
        if not url or "/app/" not in url:
            return None

        parts = urlsplit(url)

        clean_path = parts.path
        if not clean_path.endswith("/"):
            clean_path += "/"

        return urlunsplit((parts.scheme, parts.netloc, clean_path, "", ""))