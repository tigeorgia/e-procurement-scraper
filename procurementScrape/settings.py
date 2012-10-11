# Scrapy settings for procurementScrape project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'procurementScrape'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['procurementScrape.spiders']
NEWSPIDER_MODULE = 'procurementScrape.spiders'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)
COOKIES_DEBUG = True

ITEM_PIPELINES = [
    'procurementScrape.pipelines.ProcurementscrapePipeline',
]


