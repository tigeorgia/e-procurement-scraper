# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
import json
import datetime
import os
import re
from scrapy.contrib.exporter import JsonLinesItemExporter
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
        self.procuringEntitiesfile = open(scrapeDir+"/"+'organisations.json', 'wb')      
        self.tenderBiddersFile = open(scrapeDir+"/"+'tenderBidders.json', 'wb')        
        self.tenderAgreementsFile = open(scrapeDir+"/"+'tenderAgreements.json', 'wb')      
        self.tenderDocumentationFile = open(scrapeDir+"/"+'tenderDocumentation.json', 'wb')

        self.tenderExporter = JsonLinesItemExporter(self.tendersfile)
        self.tenderExporter.start_exporting()
        self.procurerExporter = JsonLinesItemExporter(self.procuringEntitiesfile)
        self.procurerExporter.start_exporting()
        self.biddersExporter = JsonLinesItemExporter(self.tenderBiddersFile)
        self.biddersExporter.start_exporting()
        self.agreementExporter = JsonLinesItemExporter(self.tenderAgreementsFile)
        self.agreementExporter.start_exporting()
        self.documentationExporter = JsonLinesItemExporter(self.tenderDocumentationFile)
        self.documentationExporter.start_exporting()
        
        self.infoFile = open(scrapeDir+"/"+'scrapeInfo.txt', 'wb')
        self.infoFile.write("StartTime: " +nowStr+ "\n")
        
    def process_item(self, item, spider):
        if isinstance(item, Tender):
          self.tenderExporter.export_item(item)
        elif isinstance(item, Organisation):
          self.procurerExporter.export_item(item)
        elif isinstance(item, TenderBidder):
          self.biddersExporter.export_item(item)
        elif isinstance(item, TenderAgreement):
          self.agreementExporter.export_item(item)
        elif isinstance(item, TenderDocument):
          self.documentationExporter.export_item(item)
        return item

   #for key, value in item.iteritems():
          #newVal = re.sub('"','/"',value)
          #item[key] = newVal

        #line = json.dumps(dict(item)) + ","
        
        #if isinstance(item, Tender):
       #     self.tendersfile.write(line)
       # elif isinstance(item, Organisation):
        #    self.procuringEntitiesfile.write(line)
       # elif isinstance(item, TenderBidder):
       #     self.tenderBiddersFile.write(line)
       # elif isinstance(item, TenderAgreement):
       #     self.tenderAgreementsFile.write(line)
       # elif isinstance(item, TenderDocument):
       #     self.tenderDocumentationFile.write(line)
       # return item
    
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
        print spider.firstTender
        self.infoFile.write("firstTenderURL: %d" % int(spider.firstTender))
        self.infoFile.close()
        

        self.tenderExporter.finish_exporting()
        self.procurerExporter.finish_exporting()
        self.biddersExporter.finish_exporting()
        self.agreementExporter.finish_exporting()
        self.documentationExporter.finish_exporting()
        self.tendersfile.close()
        self.procuringEntitiesfile.close()
        self.tenderBiddersFile.close()
        self.tenderAgreementsFile.close()       
        self.tenderDocumentationFile.close()
        

