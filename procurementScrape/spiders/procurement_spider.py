#! /usr/bin/env python
#encoding:UTF-8


from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider
from scrapy.http import Request
from procurementScrape.items import Tender, Organisation, TenderBidder, TenderAgreement, TenderDocument, CPVCode
import os
import sys
import httplib2
import shutil
from time import sleep

class ProcurementSpider(BaseSpider):
    name = "procurement"
    allowed_domains = ["procurement.gov.ge", "tenders.procurement.gov.ge"]
    baseUrl = "https://tenders.procurement.gov.ge/public/"
    mainPageBaseUrl = baseUrl+"lib/controller.php?action=search_app&page="
    userAgent = 'Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US'
    start_urls = [mainPageBaseUrl+"0"]
    tenderCount = 0
    orgCount = 0
    bidderCount = 0
    agreementCount = 0
    docCount = 0
    failedRequests = []
   
    def make_requests_from_url(self, url):
        return Request(url, cookies={"SPALITE":self.sessionCookie},headers={'User-Agent':'Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US))'})
        
    def setSessionCookie(self,sessionCookie):
        self.sessionCookie = sessionCookie
        
    def setScrapeMode(self,scrapeMode):
        self.scrapeMode = scrapeMode
        
    def setScrapePath(self, path):
        self.scrapePath = path
        
    def parseResultsPage(self,response):
        hxs = HtmlXPathSelector(response)
        resultsDividersXPath = hxs.select('//div[contains(@id, "agency_docs")]//div')
        resultsDividers = resultsDividersXPath.extract()
        
        #get results documents
        
        if resultsDividers.__len__() >= 3:
            winnerDiv = resultsDividers[2]
            tenderID = response.meta['tenderID']

            #parse results section if there is one
            if winnerDiv.find(u"ხელშეკრულება") > -1:    
              amendmentNumber = 0
              item = TenderAgreement()
              item["tenderID"] = tenderID
              item["AmendmentNumber"] = str(amendmentNumber)
              
              index = winnerDiv.find("ShowProfile")
              index = winnerDiv.find("(",index)
              endIndex = winnerDiv.find(")",index)
              
              orgUrl = winnerDiv[index+1:endIndex]
              item["OrgUrl"] = orgUrl
                      
              index = winnerDiv.find(u"ნომერი/თანხა")
              endIndex = winnerDiv.find("<br",index)
              index = winnerDiv.rfind("/",index,endIndex)
              item["Amount"] = winnerDiv[index+1:endIndex].strip()
              
              #there seem to be 2 different types of agreement date types
              #one has a single Contract validity date and the other has a start and end date
              dateRange = winnerDiv.find("-",index)
              if dateRange > -1:
                index = winnerDiv.find(u"ძალაშია",index)
                index = winnerDiv.find(":",index)
                endIndex = winnerDiv.find("-",index)
                item["StartDate"] = winnerDiv[index+1:endIndex].strip()
                
                index = endIndex
                endIndex = winnerDiv.find("<",index)
                item["ExpiryDate"] = winnerDiv[index+1:endIndex].strip()
              else:
                index = winnerDiv.find("date",validityIndex)
                index = winnerDiv.find(">",index)
                endIndex = winnerDiv.find("</",index)
                item["ExpiryDate"] = winnerDiv[index+1:endIndex].strip()

              
              #find the document download section
              index = winnerDiv.find('align="right',index)
              index = winnerDiv.find("href",index)
              index = winnerDiv.find('"',index)+1
              endIndex = winnerDiv.find('"',index)
              item["documentUrl"] = self.baseUrl+winnerDiv[index:endIndex]

              self.agreementCount = self.agreementCount + 1
              yield item
            
              #check for contract amendment
              if resultsDividers.__len__() > 3:
                  amendments = resultsDividers[3]
                  #just to be sure
                  if amendments.find(u"ხელშეკრულების ცვლილება") > -1:
                      #get all amendments
                      xAmendmentsTable = resultsDividersXPath[3]
                      xAmendments = xAmendmentsTable.select('.//tr')
                      for amendment in xAmendments:
                          amendmentHtml = amendment.extract()
                          item = TenderAgreement()
                          item["tenderID"] = tenderID
                          amendmentNumber = amendmentNumber + 1
                          item["AmendmentNumber"] = str(amendmentNumber)
                          item["OrgUrl"] = orgUrl
                          self.agreementCount = self.agreementCount + 1
                          #need to cover cases of "bidder refused the bid" and contract amendments with no updated documentation  
                      
                          if amendmentHtml.find(u"დისკვალიფიკაცია") > -1:
                              #disqualified after an agreement was already signed
                              #need to revisit which values get set here
                              item["Amount"] = "NULL"                                 
                              item["StartDate"] = "NULL"                                 
                              item["ExpiryDate"] = "NULL"
                              item["documentUrl"] = "disqualified"
                              yield item
                          else:
                              index = amendmentHtml.find(u"ნომერი/თანხა")
                              endIndex = amendmentHtml.find("<br",index)
                              index = amendmentHtml.rfind("/",index,endIndex)
                              item["Amount"] = amendmentHtml[index+1:endIndex].strip()
                              
                              index = amendmentHtml.find(u"ძალაშია",index)
                              index = amendmentHtml.find(":",index)
                              endIndex = amendmentHtml.find("-",index)
                              item["StartDate"] = amendmentHtml[index+1:endIndex].strip()
                              
                              index = endIndex
                              endIndex = amendmentHtml.find("<",index)
                              item["ExpiryDate"] = amendmentHtml[index+1:endIndex].strip()
                              
                              #find the document download section
                              if amendmentHtml.find(u"ხელშეკრულებაში შეცდომის გასწორება") > -1:
                                  item["documentUrl"] = "Treaty Correction: No Document"
                              else:  
                                  index = amendmentHtml.find('align="right',index)
                                  index = amendmentHtml.find("href",index)
                                  index = amendmentHtml.find('"',index)+1
                                  endIndex = amendmentHtml.find('"',index)
                                  item["documentUrl"] = self.baseUrl+amendmentHtml[index:endIndex]
                              yield item
            #the contract has been refused list all refusals            
            elif winnerDiv.find(u"პრეტენდენტმა უარი თქვა წინადადებაზე") > -1:
                  amendmentNumber = 0
                  xpath = HtmlXPathSelector(text=winnerDiv)
                  biddersRows = xpath.select('//tr').extract()
                  for row in biddersRows:
                    fields = HtmlXPathSelector(text=row).select('//td').extract()
                    item = TenderAgreement()
                    item["tenderID"] = tenderID
                    item["AmendmentNumber"] = str(amendmentNumber)
                    item["Amount"] = "-1"      

                    conditions = "width",">","</"                          
                    item["StartDate"] = self.findData( fields, conditions, -1 )[0]                               
                    item["documentUrl"] = "bidder refused agreement"
                    conditions = "strong",">","</"
                    item["OrgUrl"] = self.findData( fields, conditions, -1 )[0]
                    item["ExpiryDate"] = "NULL"
                    amendmentNumber = amendmentNumber + 1
                    yield item
            #check for disqualifications
            elif winnerDiv.find(u"დისკვალიფიკაცია") > -1:
              amendmentNumber = 0
              xpath = HtmlXPathSelector(text=winnerDiv)
              biddersRows = xpath.select('//tr').extract()
              for row in biddersRows:
                fields = HtmlXPathSelector(text=row).select('//td').extract()
                item = TenderAgreement()
                item["tenderID"] = tenderID
                item["AmendmentNumber"] = str(amendmentNumber)
                  
                conditions = "width",">","</"                          
                item["StartDate"] = self.findData( fields, conditions, -1 )[0]                                
                item["documentUrl"] = "disqualifed"
                conditions = "strong",">","</"
                item["OrgUrl"] = self.findData( fields, conditions, -1 )[0]
                conditions = "right",">","</td"
                item["Amount"] =  "-1"
                item["ExpiryDate"] = "NULL"
                amendmentNumber = amendmentNumber + 1
                yield item

            #unknown stuff
            else:
              item = TenderAgreement()
              item["tenderID"] = tenderID
              item["AmendmentNumber"] = str(0)
              item["Amount"] = "-1"                             
              item["StartDate"] = "NULL"                            
              item["documentUrl"] = "unknown"
              item["OrgUrl"] = "NULL"
              item["ExpiryDate"] = "NULL"
              yield item   
    
    def parseBidsPage(self,response):
        #print "parsing bids"
        hxs = HtmlXPathSelector(response)
        bidRows = hxs.select('//div[contains(@id, "app_bids")]//table[last()]/tbody//tr').extract()
        if bidRows.__len__() == 0:
            return
        for bidder in bidRows:
            item = TenderBidder()
            self.bidderCount = self.bidderCount + 1
            item["tenderID"] = response.meta['tenderID']
            index = bidder.find("ShowProfile")
            index = bidder.find("(",index)
            endIndex = bidder.find(")",index)
            item["OrgUrl"] = bidder[index+1:endIndex]
    
            index = bidder.find("strong")
            index = bidder.find(">",index)
            endIndex = bidder.find("<",index)
            item["lastBidAmount"] = bidder[index+1:endIndex].strip().replace("`","")
            
            index = bidder.find("date",index)
            index = bidder.find(">",index)
            endIndex = bidder.find("<",index)
            item["lastBidDate"] = bidder[index+1:endIndex]
            
            index = bidder.find("activebid1",index)
            index = bidder.find(">",index)
            endIndex = bidder.find("<",index)
            item["firstBidAmount"] = bidder[index+1:endIndex-1].strip().replace("`","")
            
            index = bidder.find("date",index)
            index = bidder.find(">",index)
            endIndex = bidder.find("<",index)
            item["firstBidDate"] = bidder[index+1:endIndex]
            
            index = bidder.find('align="center"',index)
            index = bidder.find("[",index)
            endIndex = bidder.find("]",index)
            item["numberOfBids"] = bidder[index+1:endIndex]
            
            yield item
            
            #now lets use the company id to scrape the company data
            url = self.baseUrl+"lib/controller.php?action=profile&org_id="+item['OrgUrl']
            metaData = { 'OrgUrl': item['OrgUrl'], 'type': "biddingOrg"}
            organisation_request = Request(url, meta=metaData,errback=self.orgFailed, callback=self.parseOrganisation, cookies={"SPALITE":self.sessionCookie}, dont_filter=True, headers={"User-Agent":self.userAgent})

            yield organisation_request
    
    def parseDocumentationPage(self,response):
        hxs = HtmlXPathSelector(response)
        documentRows = hxs.select('//table[contains(@id, "tender_docs")]//tr').extract()
        #drop element 0
        documentRows.pop(0)
        for documentRow in documentRows:
            item = TenderDocument()
            
            item["tenderID"] = response.meta['tenderID']
            
            index = documentRow.find("id")
            index = documentRow.find('"',index) + 1
            endIndex = documentRow.find('"',index)
            rawData = documentRow[index:endIndex]
            dataArray = rawData.split(".")
            url = self.baseUrl+"lib/files.php?mode=app&"
            item["documentUrl"] = url+"file="+dataArray[0]+"&code="+dataArray[1]

            index = documentRow.find("obsolete0",index)
            index = documentRow.find(">",index)
            endIndex = documentRow.find("</",index)
            item["title"] = documentRow[index+1:endIndex]
            
            index = documentRow.find("date",index)
            index = documentRow.find(">",index)
            endIndex = documentRow.find("<br",index)
            item["date"] = documentRow[index+1:endIndex]
            
            index = documentRow.find(">",endIndex)
            endIndex = documentRow.find("</td",index)
            item["author"] = documentRow[index+1:endIndex]
            self.docCount = self.docCount + 1

            yield item
        
    
    def parseOrganisation(self,response):
        self.orgCount = self.orgCount + 1
        #print "parsing procurer"
        hxs = HtmlXPathSelector(response)
        keyPairs = hxs.select('//div[contains(@id, "profile_dialog")]//tr').extract()
        item = Organisation()
        item["OrgUrl"] = response.meta['OrgUrl']

        index = keyPairs[0].find("label")
        index = keyPairs[0].find(">",index)
        endIndex = keyPairs[0].find("<",index)
        item["Type"] = keyPairs[0][index+1:endIndex].strip()
        
        index = keyPairs[0].find("strong",index)
        index = keyPairs[0].find(">",index)
        endIndex = keyPairs[0].find("<",index)
        item["Name"] = keyPairs[0][index+1:endIndex].strip()
        
        index = keyPairs[1].find("/td")
        index = keyPairs[1].find("<td",index)
        index = keyPairs[1].find(">",index)
        endIndex = keyPairs[1].find("<",index)
        item["OrgID"] = keyPairs[1][index+1:endIndex]
        #print "parsing Org: " + item['OrgUrl'] +" OrgID: "+ item['OrgID']
        
        index = keyPairs[2].find("/td")
        index = keyPairs[2].find("<td",index)
        index = keyPairs[2].find(">",index)
        endIndex = keyPairs[2].find("<",index)
        item["Country"] = keyPairs[2][index+1:endIndex]
        
        index = keyPairs[3].find("/td")
        index = keyPairs[3].find("<td",index)
        index = keyPairs[3].find(">",index)
        endIndex = keyPairs[3].find("<",index)
        item["city"] = keyPairs[3][index+1:endIndex]
        
        index = keyPairs[4].find("/td")
        index = keyPairs[4].find("<td",index)
        index = keyPairs[4].find(">",index)
        endIndex = keyPairs[4].find("<",index)
        item["address"] = keyPairs[4][index+1:endIndex]
        
        index = keyPairs[5].find("/td")
        index = keyPairs[5].find("<td",index)
        index = keyPairs[5].find(">",index)
        endIndex = keyPairs[5].find("<",index)
        item["phoneNumber"] = keyPairs[5][index+1:endIndex]
        
        index = keyPairs[6].find("/td")
        index = keyPairs[6].find("<td",index)
        index = keyPairs[6].find(">",index)
        endIndex = keyPairs[6].find("<",index)
        item["faxNumber"] = keyPairs[6][index+1:endIndex]
        
        #dig into 'a' tag
        index = keyPairs[7].find("href")
        index = keyPairs[7].find(">",index)
        endIndex = keyPairs[7].find("<",index)
        item["email"] = keyPairs[7][index+1:endIndex]
        
        #dig into 'a' tag
        index = keyPairs[8].find("href")
        index = keyPairs[8].find(">",index)
        endIndex = keyPairs[8].find("<",index)
        item["webpage"] = keyPairs[8] [index+1:endIndex]
        
        yield item
    


    def findKeyValue(self, keyString, pairs, conditions, direction = 1 ):
        keyCondition = (keyString, )
        result = self.findData( pairs, keyCondition, -1 )
        if result[0] is not None:
            result = self.findData( pairs, conditions, result[1]+direction )
        return result[0]

    def findData(self, keypairs, conditionList, startPair ):
        result = [None, -1]
        for i, keyPair in enumerate(keypairs):       
            if i >= startPair:        
                index = 0
                prevIndex = -1
                found = True
                #I make the assumption that the 2nd last index I calculate will be the start of substring
                #and the last index is the end of the substring so I need to always keep track of the 2nd last index
                for condition in conditionList:
                    searchIndex = keyPair.find(condition,index)
                    if searchIndex == -1:
                        found = False
                        break;
                    prevIndex = index
                    index = searchIndex
                if found:
                    result[0] = keyPair[prevIndex+1:index]
                    result[1] = i
                    return result
        return result
    
    def parseTender(self, response):
        self.tenderCount = self.tenderCount + 1
        hxs = HtmlXPathSelector(response)
        keyPairs = hxs.select('//tr/td').extract()
        toYield = []
        item = Tender()
     
        item['tenderID'] = response.meta['tenderUrl']
        conditions = "ShowProfile","(", ")"
        result = self.findData( keyPairs, conditions, -1 )
        item['procuringEntityUrl'] = result[0]
        
        conditions = "<img", ">", "</"
        result = self.findData( keyPairs, conditions, result[1] )
        item['procuringEntityName'] = result[0].strip()
        
        conditions = ">","<"
        item['tenderType'] = self.findKeyValue( u"ტენდერის ტიპი", keyPairs, conditions )
        
        conditions = "strong",">","<"
        item['tenderRegistrationNumber']  = self.findKeyValue( u"სატენდერო განცხადების ნომერი", keyPairs, conditions )

        conditions =  "img",">","<"
        item['tenderStatus']  = self.findKeyValue( u"ტენდერის მიმდინარეობის სტატუსი", keyPairs, conditions ).strip()
        
        conditions = ">","<"
        item['tenderAnnouncementDate'] =   self.findKeyValue( u"ტენდერის გამოცხადების თარიღი", keyPairs, conditions )       
        item['bidsStartDate'] =  self.findKeyValue( u"წინადადებების მიღება იწყება", keyPairs, conditions )       
        item['bidsEndDate'] =  self.findKeyValue( u"წინადადებების მიღება მთავრდება", keyPairs, conditions )
        
        conditions = "span", ">", "<"
        val =  self.findKeyValue( u"შესყიდვის სავარაუდო ღირებულება", keyPairs, conditions )
        if val == None:
          val =  self.findKeyValue( u"პრეისკურანტის სავარაუდო ღირებულება", keyPairs, conditions )
        item['estimatedValue'] = val.replace("`","").replace("GEL","").strip()

        conditions = "/strong",">","<"
        item['cpvCode'] =  self.findKeyValue( u"შესყიდვის კატეგორია", keyPairs, conditions ).strip()
      
        conditions = "blabla",">","</"
        item['info'] =  self.findKeyValue( u"დამატებითი ინფორმაცია", keyPairs, conditions )
        
        conditions = ">","</"
        item['amountToSupply'] =  self.findKeyValue( u"შესყიდვის რაოდენობა ან მოცულობა", keyPairs, conditions ) 
        item['supplyPeriod'] =  self.findKeyValue( u"მოწოდების ვადა", keyPairs, conditions )
        item['offerStep'] =  self.findKeyValue( u"შეთავაზების ფასის კლების ბიჯი", keyPairs, conditions )
        item['guaranteeAmount'] =  self.findKeyValue( u"შეთავაზების ფასის კლების ბიჯი", keyPairs, conditions )
        item['guaranteePeriod'] =  self.findKeyValue( u"გარანტიის ოდენობა", keyPairs, conditions )
        toYield.append(item)

        #the sub cpv codes are within a list so we will deal with these seperately

        #get all list items within a div tag
        cpvItems = hxs.select('//div/ul/li').extract()

        for cpvItem in cpvItems:
          if cpvItem.find("padding:4px") > -1:
            startIndex = cpvItem.find(">")
            endIndex = cpvItem.find("-",startIndex)
            cpvCode = cpvItem[startIndex+6:endIndex]
            descriptionEnd = cpvItem.find("<div",endIndex)
            description = cpvItem[endIndex+1:descriptionEnd]
            cpvObject = CPVCode()
            cpvObject['tenderID'] = item['tenderID']
            cpvObject['cpvCode'] = cpvCode.strip()
            cpvObject['description'] = description.strip()
            toYield.append(cpvObject)
            
    
        #now lets use the procuring entity id to find more info about the procurer
        print "parsing Tender: " + item['tenderID'] +" procurerURL: "+ item['procuringEntityUrl']
        url = self.baseUrl+"lib/controller.php?action=profile&org_id="+item['procuringEntityUrl']
        metaData = {'OrgUrl': item['procuringEntityUrl'],'type': "procuringOrg"}
        procurer_request = Request(url, errback=self.orgFailed, meta=metaData, callback=self.parseOrganisation, cookies={"SPALITE":self.sessionCookie}, headers={"User-Agent":self.userAgent})
        toYield.append(procurer_request)     

        #now lets look at the tender documentation
        url = self.baseUrl+"lib/controller.php?action=app_docs&app_id="+item['tenderID']
        documentation_request = Request(url, errback=self.documentationFailed,callback=self.parseDocumentationPage, cookies={"SPALITE":self.sessionCookie}, headers={"User-Agent":self.userAgent})
        documentation_request.meta['tenderID'] = item['tenderID']
        toYield.append(documentation_request)   
        
        #now lets look at the bids made on this tender
        url = self.baseUrl+"lib/controller.php?action=app_bids&app_id="+item['tenderID']
        bids_request = Request(url, errback=self.bidsFailed,callback=self.parseBidsPage, cookies={"SPALITE":self.sessionCookie}, headers={"User-Agent":self.userAgent})
        bids_request.meta['tenderID'] = item['tenderID']
        toYield.append(bids_request)   
        
        #finally lets look at the results of this tender
        url = self.baseUrl+"lib/controller.php?action=agency_docs&app_id="+item['tenderID']
        results_request = Request(url, errback=self.resultFailed,callback=self.parseResultsPage,cookies={"SPALITE":self.sessionCookie}, headers={"User-Agent":self.userAgent})
        results_request.meta['tenderID'] = item['tenderID']
        toYield.append(results_request)   
  
        return toYield
        
    def parseTenderUrls(self, response):
        hxs = HtmlXPathSelector(response)
        
        tenderOnClickItems = hxs.select('//table[@id="list_apps_by_subject"]//tr//@onclick').extract()
        #print "processing page: " + response.url
        first = True
        page = response.meta['page']
        incrementalFinished = False
        for tenderOnClickItem in tenderOnClickItems:
            base_tender_url = self.baseUrl+"lib/controller.php?action=app_main&app_id="
            index = tenderOnClickItem.find("ShowApp")
            index = tenderOnClickItem.find("(",index)
            endIndex = tenderOnClickItem.find(",",index)
            index_url = tenderOnClickItem[index+1:endIndex]
            if self.scrapeMode == "INCREMENTAL":
                if index_url == response.meta['prevScrapeStartTender']:
                    incrementalFinished = True
                    break
            tender_url = base_tender_url+index_url
            request = Request(tender_url, errback=self.tenderFailed,callback=self.parseTender, cookies={"SPALITE":self.sessionCookie}, meta={"tenderUrl": index_url, "prevScrapeStartTender": response.meta['prevScrapeStartTender']},headers={"User-Agent":self.userAgent})
            
            #if this is the first page store the first tender as a marker so the incremental scraper knows where to stop.
            if page == 1 and first:
              self.firstTender = index_url
            first = False
            yield request
            
        if not incrementalFinished and page < int(response.meta['final_page']):
            page = page+1
            url = self.mainPageBaseUrl+str(page)
            metadata ={"page": page, "final_page": response.meta['final_page'], "prevScrapeStartTender": response.meta['prevScrapeStartTender']}
            request = Request(url, errback=self.urlPageFailed,callback=self.parseTenderUrls, meta=metadata, cookies={"SPALITE":self.sessionCookie}, headers={"User-Agent":self.userAgent})
            yield request
    
    def parse(self, response):
      #if we are doing a single tender test scrape
      if self.scrapeMode != "FULL" and self.scrapeMode != "INCREMENTAL":
        url_id = self.scrapeMode
        tender_url = self.baseUrl+"lib/controller.php?action=app_main&app_id="+url_id
        self.firstTender = self.scrapeMode
        request = Request(tender_url, errback=self.tenderFailed,callback=self.parseTender, cookies={"SPALITE":self.sessionCookie}, meta={"tenderUrl": url_id, "prevScrapeStartTender": self.firstTender},headers={"User-Agent":self.userAgent})
        yield request
                  
      else:  
        #Find index of last page
        hxs = HtmlXPathSelector(response)
        totalPagesButton = hxs.select('//div[@class="pager pad4px"]//button').extract()[2]
        
        index = totalPagesButton.find('/')
        endIndex = totalPagesButton.find(')',index)
        final_page = totalPagesButton[index+1:endIndex]
        
        if( final_page == -1 ):
            #print "Parsing Error... stopping"
            return
        
        lastTenderURL = -1
        if self.scrapeMode != "FULL":
            #find where the last scrape left off
            scrapeList = []
            currentDir = os.getcwd()
            if os.path.exists("FullScrapes"):
                fullScrapes = os.listdir("FullScrapes")
                
            if os.path.exists("IncrementalScrapes"):
                incrementalScrapes = os.listdir("IncrementalScrapes")
            scrapeList = fullScrapes + incrementalScrapes
            #now we have a list of old scrape directories lets find the most recent one and find the first tender it scraped
            scrapeList.sort()
            while lastTenderURL == -1 and scrapeList.count > 0:
                last = scrapeList.pop()
                typeDir = "IncrementalScrapes"
                if fullScrapes.__contains__(last):
                    typeDir = "FullScrapes"
                    
                lastScrapeInfo = open(currentDir+"/"+typeDir+"/"+last+"/"+"scrapeInfo.txt")
                
                while 1:
                    line = lastScrapeInfo.readline()
                    if not line:
                        break
                    index = line.find("firstTenderURL")
                    if index > -1:
                        index = line.find(":")
                        lastTenderURL = line[index+2:]
                        break
        print "Starting scrape"
        url = self.mainPageBaseUrl+str(1)
        metadata = {"page": 1, "final_page": int(final_page), "prevScrapeStartTender": lastTenderURL}
        request = Request(url, errback=self.urlPageFailed,callback=self.parseTenderUrls, meta = metadata, cookies={"SPALITE":self.sessionCookie}, headers={"User-Agent":self.userAgent})
        yield request


#ERROR HANDLING SECTION#
    def urlPageFailed(self,error):
        print "urlpager failed"
        yield error.request
        #requestFailure = [self.parseTenderUrls, error.request.url]
        #self.failedRequests.append(requestFailure)
    def tenderFailed(self,error):
        print "tender failed "
        requestFailure = [self.parseTender, error.request.url]
        self.failedRequests.append(requestFailure)
    def resultFailed(self,error):
        print "result failed"
        requestFailure = [self.parseResultsPage, error.request.url]
        self.failedRequests.append(requestFailure)
    def bidsFailed(self,error):
        print "bidder failed"
        requestFailure = [self.parseBidsPage, error.request.url]
        self.failedRequests.append(requestFailure)
    def documentationFailed(self,error):
        print "documentation failed"
        requestFailure = [self.parseDocumentationPage, error.request.url]
        self.failedRequests.append(requestFailure)
    def orgFailed(self,error):
        print "org failed failed"
        requestFailure = [self.parseOrganisation, error.request.url]
        self.failedRequests.append(requestFailure)
def main():
    # shut off log
    from scrapy.conf import settings
    settings.overrides['LOG_ENABLED'] = False
 
    # set up crawler
    from scrapy.crawler import CrawlerProcess
 
    crawler = CrawlerProcess(settings)
    crawler.install()
    crawler.configure()
 
    def getSPACookie():
        #first get cookie from dummy request
        http = httplib2.Http()
        url = "https://tenders.procurement.gov.ge/public/?go=1000"
        headers={"User-Agent":'Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US'}
        response, content = http.request(url, 'POST', headers=headers)
        if( response['set-cookie'] ):
            cookieString = response['set-cookie']
            index = cookieString.find('SPALITE')
            index = cookieString.find("=",index)
            endIndex = cookieString.find(';',index)
            spaLite = cookieString[index+1:endIndex]
            return spaLite

    spaLite = getSPACookie()
    # schedule spider
    procurementSpider = ProcurementSpider()
    scrapeMode = "INCREMENTAL"
    if len(sys.argv) > 1:
      scrapeMode = sys.argv[1]

    procurementSpider.setScrapeMode(scrapeMode)
    outputPath = sys.argv[2]
    procurementSpider.setSessionCookie(spaLite)
    crawler.crawl(procurementSpider)

    #start engine scrapy/twisted
    print "STARTING ENGINE"
    crawler.start()
    print "MAIN SCRAPE COMPLETE"

    #lets go through our failed list greatly increase the amount of retries we allowed and try and scrape them again with a fresh cookie
    spaLite = getSPACookie()       
    failFile = open(procurementSpider.scrapePath+"/failures.txt", 'wb')
    for failedRequest in procurementSpider.failedRequests:
        failFile.write(failedRequest[1])
        failFile.write("\n")
    failFile.close()

    #now make a copy of our scraped files and place them in the website folder and tell the web server to proc$
    currentPath = os.getcwd()
    os.chdir(outputPath)
    publicPath = "/shared/system"

    fullPath = os.getcwd()+publicPath
    for f in os.listdir(os.getcwd()+publicPath):
     os.remove(fullPath+"/"+f)
    print os.getcwd()
    os.rmdir(os.getcwd()+publicPath)
    os.chdir(currentPath)
    shutil.copytree(procurementSpider.scrapePath, outputPath+publicPath)
    
if __name__ == '__main__':
    main()
        
        