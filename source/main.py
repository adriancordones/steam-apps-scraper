from scrapy.crawler import AsyncCrawlerRunner
from scrapy.utils.defer import deferred_f_from_coro_f
from scrapy.utils.log import configure_logging
from scrapy.utils.reactor import install_reactor
from scrapy.utils.project import get_project_settings
from twisted.internet.task import react

from steam_apps_scraper.spiders.links_spider import LinksSpider
from steam_apps_scraper.spiders.apps_spider import AppsSpider

async def crawl(_):
    settings = get_project_settings()
    runner = AsyncCrawlerRunner(settings)

    crawler = runner.create_crawler(LinksSpider)
    await runner.crawl(crawler, srt_page=1, end_page=1000)
    await runner.crawl(AppsSpider, app_ids=crawler.spider.app_ids)

configure_logging({"LOG_FORMAT": "%(levelname)s: %(message)s"})
install_reactor("twisted.internet.asyncioreactor.AsyncioSelectorReactor")
react(deferred_f_from_coro_f(crawl))