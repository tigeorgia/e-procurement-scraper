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
CONCURRENT_REQUESTS_PER_DOMAIN = 8
RETRY_TIMES = 20

ITEM_PIPELINES = [
    'procurementScrape.pipelines.ProcurementscrapePipeline',
]


