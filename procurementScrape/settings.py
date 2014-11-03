# Scrapy settings for procurementScrape project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'procurementScrape'

SPIDER_MODULES = ['procurementScrape.spiders']
NEWSPIDER_MODULE = 'procurementScrape.spiders'
COOKIES_DEBUG = True

CONCURRENT_REQUESTS = 16
DOWNLOAD_DELAY = 1
DOWNLOADER_DEBUG = True

RETRY_TIMES = 20
DEPTH_PRIORITY = 1
SCHEDULER_DISK_QUEUE = 'scrapy.squeue.PickleFifoDiskQueue'
SCHEDULER_MEMORY_QUEUE = 'scrapy.squeue.FifoMemoryQueue'

ITEM_PIPELINES = {
    'procurementScrape.pipelines.ProcurementscrapePipeline': 100
}


