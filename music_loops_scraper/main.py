from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from spiders.loops_spider import LoopSpider

if __name__ == "__main__":
    process = CrawlerProcess(get_project_settings())
    process.crawl(LoopSpider)
    process.start()
