from scrapy.crawler import AsyncCrawlerRunner
from scrapy.utils.defer import deferred_f_from_coro_f
from scrapy.utils.log import configure_logging
from scrapy.utils.reactor import install_reactor
from twisted.internet.task import react

from steam_scraper.spiders.links_spider import LinksSpider
from steam_scraper.spiders.apps_spider import AppsSpider

process = CrawlerProcess(get_project_settings())

async def crawl(_):
    # TODO: Estructura posible, revisar cómo se manejarán URLs

    configure_logging({"LOG_FORMAT": "%(levelname)s: %(message)s"})
    
    runner = AsyncCrawlerRunner()
    await runner.crawl(LinksSpider, output=urls))
    await runner.crawl(AppsSpider, urls=urls)

install_reactor("twisted.internet.asyncioreactor.AsyncioSelectorReactor")
react(deferred_f_from_coro_f(crawl))