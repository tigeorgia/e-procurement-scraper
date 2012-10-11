# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
import json
from procurementScrape.items import Tender, Organisation, TenderBidder, TenderAgreement
 
class ProcurementscrapePipeline(object):
    def __init__(self):
        self.tendersfile = open('tenders.json', 'wb')
        self.tendersfile.write("[")
        
        self.procuringEntitiesfile = open('organisations.json', 'wb')
        self.procuringEntitiesfile.write("[")
        
        self.tenderBiddersFile = open('tenderBidders.json', 'wb')
        self.tenderBiddersFile.write("[")
        
        self.tenderAgreementsFile = open('tenderAgreements.json', 'wb')
        self.tenderAgreementsFile.write("[")
        
    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        
        if isinstance(item, Tender):
            self.tendersfile.write(line)
        elif isinstance(item, Organisation):
            self.procuringEntitiesfile.write(line)
        elif isinstance(item, TenderBidder):
            self.tenderBiddersFile.write(line)
        elif isinstance(item, TenderAgreement):
            self.tenderAgreementsFile.write(line)
        return item
    
    def close_spider(self,spider):
        self.tendersfile.write("]")
        self.tendersfile.close()
        
        self.procuringEntitiesfile.write("]")
        self.procuringEntitiesfile.close()
        
        self.tenderBiddersFile.write("]")
        self.tenderBiddersFile.close()
        
        self.tenderAgreementsFile.write("]")
        self.tenderAgreementsFile.close()
        
        
    

