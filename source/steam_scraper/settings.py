# Scrapy settings for steam_scraper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "steam-apps-scraper"

SPIDER_MODULES = ["steam_app_scraper.spiders"]
NEWSPIDER_MODULE = "steam_apps_scraper.spiders"

ADDONS = {}


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:148.0) Gecko/20100101 Firefox/148.0"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Concurrency and throttling settings
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 1

# Enable cookies
COOKIES_ENABLED = True

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    "Accept": "*/*",
    "Accept-Language": "es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7",
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 1
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 10
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"

FEEDS = {
    "../dataset/steam_apps.csv": {
        "format": "csv",
        "overwrite": True,
        "fields": ["id", "title", "date", "developer_name", "publisher_name", "reviews_total", "reviews_recent",
                   "reviews_total_summary", "reviews_recent_summary", "original_price", "discount_price", "discount_percent",
                   "achievements_number", "langs_number", "dlcs_number", "has_ost", "is_dlc", "is_ost", "short_desc", "dlcs",
                   "tags", "genres", "languages", "url", "developer_url", "publisher_url"],
    }
}