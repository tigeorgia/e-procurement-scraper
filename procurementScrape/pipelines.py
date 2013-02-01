# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
import json
import datetime
import os
from procurementScrape.items import Tender, Organisation, TenderBidder, TenderAgreement, TenderDocument
 
 
class ProcurementscrapePipeline(object):

    def open_spider(self,spider):
        self.startTime = datetime.datetime.now()
        nowStr = self.startTime.strftime("%Y-%m-%d %H:%M")
        if spider.performFullScrape:
            if not os.path.exists("FullScrapes"):
                os.makedirs("FullScrapes")
            typeDir = "FullScrapes/"
        else:
            if not os.path.exists("IncrementalScrapes"):
                os.makedirs("IncrementalScrapes")
            typeDir = "IncrementalScrapes/"
        scrapeDir = typeDir+nowStr
        if not os.path.exists(scrapeDir):
            os.makedirs(scrapeDir)
        
        spider.setScrapePath(scrapeDir)
        self.tendersfile = open(scrapeDir+"/"+"tenders.json", 'wb')
        self.tendersfile.write("[")
        
        self.procuringEntitiesfile = open(scrapeDir+"/"+'organisations.json', 'wb')
        self.procuringEntitiesfile.write("[")
        
        self.tenderBiddersFile = open(scrapeDir+"/"+'tenderBidders.json', 'wb')
        self.tenderBiddersFile.write("[")
        
        self.tenderAgreementsFile = open(scrapeDir+"/"+'tenderAgreements.json', 'wb')
        self.tenderAgreementsFile.write("[")
         
        self.tenderDocumentationFile = open(scrapeDir+"/"+'tenderDocumentation.json', 'wb')
        self.tenderDocumentationFile.write("[")
        
        self.infoFile = open(scrapeDir+"/"+'scrapeInfo.txt', 'wb')
        self.infoFile.write("StartTime: " +nowStr+ "\n")
        
    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + ","
        
        if isinstance(item, Tender):
            self.tendersfile.write(line)
        elif isinstance(item, Organisation):
            self.procuringEntitiesfile.write(line)
        elif isinstance(item, TenderBidder):
            self.tenderBiddersFile.write(line)
        elif isinstance(item, TenderAgreement):
            self.tenderAgreementsFile.write(line)
        elif isinstance(item, TenderDocument):
            self.tenderDocumentationFile.write(line)
        return item
    
    def close_spider(self,spider):
        self.endTime = datetime.datetime.now()
        endTimeStr = self.endTime.strftime("%Y-%m-%d %H:%M")
        self.infoFile.write("End Time: " +endTimeStr+ "\n")
        timeTaken = self.endTime - self.startTime
        
        minutes = int(timeTaken.seconds/60)
        seconds = timeTaken.seconds%60
        self.infoFile.write("Time Taken:    Days: %d    Minutes:    %d    Seconds    %d \n" % (timeTaken.days,minutes,seconds))
        self.infoFile.write("Tenders scraped: %d \n" % (spider.tenderCount))
	self.infoFile.write("Orgs scraped: %d \n" % (spider.orgCount))
	self.infoFile.write("bidders scraped: %d \n" % (spider.bidderCount))
	self.infoFile.write("agreements scraped: %d \n" % (spider.agreementCount))
	self.infoFile.write("documents scraped: %d \n" % (spider.docCount))
        self.infoFile.write("firstTenderURL: " + spider.firstTender)
        self.infoFile.close()
        
        self.tendersfile.write("]")
        self.tendersfile.close()
        
        self.procuringEntitiesfile.write("]")
        self.procuringEntitiesfile.close()
        
        self.tenderBiddersFile.write("]")
        self.tenderBiddersFile.close()
        
        self.tenderAgreementsFile.write("]")
        self.tenderAgreementsFile.close()
        
        self.tenderDocumentationFile.write("]")
        self.tenderDocumentationFile.close()
        

