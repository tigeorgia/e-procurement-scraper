# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
#import json
import datetime
import os
#import re
from scrapy.contrib.exporter import JsonLinesItemExporter
# from procurementScrape.items import Tender, Organisation, TenderBidder, TenderAgreement, TenderDocument, CPVCode, BlackListObject, WhiteListObject, Complaint, BidderResult
 
 
class ProcurementscrapePipeline(object):
    
    def __init__(self):
        self.startTime = None
        self.endTime = None
        self.tendersfile = None
        self.procuringEntitiesfile = None
        self.tenderBiddersFile = None
        self.tenderAgreementsFile = None
        self.tenderDocumentationFile = None
        self.tenderCPVCodeFile = None
        self.whiteListFile = None
        self.blackListFile = None
        self.complaintFile = None
        self.bidderResultFile = None

        self.tenderExporter = None
        self.procurerExporter = None
        self.biddersExporter = None
        self.agreementExporter = None
        self.documentationExporter = None
        self.cpvCodeExporter = None
        self.whiteListExporter = None
        self.blackListExporter = None
        self.complaintExporter = None
        self.bidderResultExporter = None
        self.infoFile = None


    def open_spider(self,spider):

        self.startTime = datetime.datetime.now()
        nowStr = self.startTime.strftime("%Y-%m-%d %H:%M")
        scrapeDir = ""
        if spider.scrapeMode == "FIXERRORS":
            scrapeDir = spider.fixpath+"_FIX"
        else:
            if spider.scrapeMode == "FULL":
                if not os.path.exists("FullScrapes"):
                    os.makedirs("FullScrapes")
                typeDir = "FullScrapes/"
            elif spider.scrapeMode == "INCREMENTAL":
                if not os.path.exists("IncrementalScrapes"):
                    os.makedirs("IncrementalScrapes")
                typeDir = "IncrementalScrapes/"
            else:
                if not os.path.exists("TestScrapes"):
                    os.makedirs("TestScrapes")
                typeDir = "TestScrapes/"
            scrapeDir = typeDir+nowStr
        
        if not os.path.exists(scrapeDir):
            os.makedirs(scrapeDir)
        
        spider.setScrapePath(scrapeDir)
        self.tendersfile = open(scrapeDir+"/"+"tenders.json", 'wb') 
        self.procuringEntitiesfile = open(scrapeDir+"/"+'organisations.json', 'wb')        
        self.tenderBiddersFile = open(scrapeDir+"/"+'tenderBidders.json', 'wb')        
        self.tenderAgreementsFile = open(scrapeDir+"/"+'tenderAgreements.json', 'wb')        
        self.tenderDocumentationFile = open(scrapeDir+"/"+'tenderDocumentation.json', 'wb')
        self.tenderCPVCodeFile = open(scrapeDir+"/"+'tenderCPVCode.json', 'wb')
        self.whiteListFile = open(scrapeDir+"/"+'whiteList.json', 'wb')
        self.blackListFile = open(scrapeDir+"/"+'blackList.json', 'wb')
        self.complaintFile = open(scrapeDir+"/"+'complaints.json', 'wb')
        self.bidderResultFile = open(scrapeDir+"/"+'bidderResult.json', 'wb')

        self.tenderExporter = JsonLinesItemExporter(self.tendersfile)
        self.procurerExporter = JsonLinesItemExporter(self.procuringEntitiesfile)
        self.biddersExporter = JsonLinesItemExporter(self.tenderBiddersFile)
        self.agreementExporter = JsonLinesItemExporter(self.tenderAgreementsFile)
        self.documentationExporter = JsonLinesItemExporter(self.tenderDocumentationFile)
        self.cpvCodeExporter = JsonLinesItemExporter(self.tenderCPVCodeFile)
        self.whiteListExporter = JsonLinesItemExporter(self.whiteListFile)
        self.blackListExporter = JsonLinesItemExporter(self.blackListFile)
        self.complaintExporter = JsonLinesItemExporter(self.complaintFile)
        self.bidderResultExporter = JsonLinesItemExporter(self.bidderResultFile)

        self.tenderExporter.start_exporting()         
        self.procurerExporter.start_exporting()        
        self.biddersExporter.start_exporting()     
        self.agreementExporter.start_exporting()
        self.documentationExporter.start_exporting()        
        self.cpvCodeExporter.start_exporting()
        self.whiteListExporter.start_exporting()
        self.blackListExporter.start_exporting()
        self.complaintExporter.start_exporting()
        self.bidderResultExporter.start_exporting()
        
        self.infoFile = open(scrapeDir+"/"+'scrapeInfo.txt', 'wb')
        self.infoFile.write("StartTime: " +nowStr+ "\n")
        
    def process_item(self, item):
        itemClassName = item.__class__.__name__
        if (itemClassName == "Tender"):
            self.tenderExporter.export_item(item)
        elif (itemClassName == "Organisation"):
            self.procurerExporter.export_item(item)
        elif (itemClassName == "TenderBidder"):
            self.biddersExporter.export_item(item)
        elif (itemClassName == "TenderAgreement"):
            self.agreementExporter.export_item(item)
        elif (itemClassName == "TenderDocument"):
            self.documentationExporter.export_item(item)
        elif (itemClassName == "CPVCode"):
            self.cpvCodeExporter.export_item(item)
        elif (itemClassName == "WhiteListObject"):
            self.whiteListExporter.export_item(item)
        elif (itemClassName == "BlackListObject"):
            self.blackListExporter.export_item(item)
        elif (itemClassName == "Complaint"):
            self.complaintExporter.export_item(item)
        elif (itemClassName == "BidderResult"):
            self.bidderResultExporter.export_item(item)
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
        print spider.firstTender
        self.infoFile.write("firstTenderURL: %d" % int(spider.firstTender))
        self.infoFile.close()
        
        self.tenderExporter.finish_exporting()
        self.procurerExporter.finish_exporting()
        self.biddersExporter.finish_exporting()
        self.agreementExporter.finish_exporting()
        self.documentationExporter.finish_exporting()
        self.whiteListExporter.finish_exporting()
        self.blackListExporter.finish_exporting()
        self.complaintExporter.finish_exporting()
        self.bidderResultExporter.finish_exporting()

        self.tendersfile.close()
        self.procuringEntitiesfile.close()
        self.tenderBiddersFile.close()
        self.tenderAgreementsFile.close()         
        self.tenderDocumentationFile.close()
        self.tenderCPVCodeFile.close()
        self.whiteListFile.close() 
        self.blackListFile.close()
        self.complaintFile.close()
        self.bidderResultFile.close()
