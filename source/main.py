from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from steam_scraper.spiders.links_spider import LinksSpider
from steam_scraper.spiders.apps_spider import AppsSpider

process = CrawlerProcess(get_project_settings())

process.crawl(LinksSpider)
process.crawl(AppsSpider)

process.start()