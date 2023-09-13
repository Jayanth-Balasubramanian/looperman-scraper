from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from spiders.loops_spider import LoopSpider
from time import perf_counter

if __name__ == "__main__":
    process = CrawlerProcess(get_project_settings())
    process.crawl(LoopSpider)
    start_time = perf_counter()
    process.start()
    end_time = perf_counter()
    print(f"Elapsed time: {end_time - start_time}")
