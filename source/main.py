from scrapy.crawler import AsyncCrawlerRunner
from scrapy.utils.defer import deferred_f_from_coro_f
from scrapy.utils.log import configure_logging
from scrapy.utils.reactor import install_reactor
from twisted.internet.task import react

from steam_scraper.spiders.links_spider import LinksSpider
from steam_scraper.spiders.apps_spider import AppsSpider

async def crawl(_):
    configure_logging({"LOG_FORMAT": "%(levelname)s: %(message)s"})
    
    runner = AsyncCrawlerRunner()
    await runner.crawl(LinksSpider, output=app_ids)
    await runner.crawl(AppsSpider, app_ids=app_ids)

install_reactor("twisted.internet.asyncioreactor.AsyncioSelectorReactor")
react(deferred_f_from_coro_f(crawl))