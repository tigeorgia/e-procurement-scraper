#! /usr/bin/env python
#encoding:UTF-8


from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider
from scrapy.http import Request
from procurementScrape.items import Tender, Organisation, TenderBidder, TenderAgreement, TenderDocument
from time import sleep
import httplib2

class ProcurementSpider(BaseSpider):
    name = "procurement"
    allowed_domains = ["procurement.gov.ge", "tenders.procurement.gov.ge"]
    baseUrl = "https://tenders.procurement.gov.ge/public/"
    mainPageBaseUrl = baseUrl+"lib/controller.php?action=search_app&page="
    start_urls = [mainPageBaseUrl+"1"]
    tenderCount = 0
    
    def make_requests_from_url(self, url):
        return Request(url, cookies={"SPALITE":self.sessionCookie},headers={'User-Agent':'Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US))'})
        
    def setSessionCookie(self,sessionCookie):
        self.sessionCookie = sessionCookie

    def parseResultsPage(self,response):
        #print "parsing results"
        hxs = HtmlXPathSelector(response)
        resultsDividersXPath = hxs.select('//div[contains(@id, "agency_docs")]//div')
        resultsDividers = resultsDividersXPath.extract()
        
        #get results documents
        
        if resultsDividers.__len__() >= 3:
            winnerDiv = resultsDividers[2]
            
            #check for disqualifications
            if winnerDiv.find("დისკვალიფიკაცია") > -1 :
                return
            
            tenderID = response.meta['tenderID']
            amendmentNumber = 0
            item = TenderAgreement()
            item["tenderID"] = tenderID
            item["AmendmentNumber"] = str(amendmentNumber)
            
            index = winnerDiv.find("ShowProfile")
            index = winnerDiv.find("(",index)
            endIndex = winnerDiv.find(")",index)
            
            orgUrl = winnerDiv[index+1:endIndex]
            item["OrgUrl"] = orgUrl
                    
            index = winnerDiv.find("ნომერი/თანხა")
            endIndex = winnerDiv.find("ლარი",index)
            index = winnerDiv.rfind("/",index,endIndex)
            item["Amount"] = winnerDiv[index+1:endIndex].strip()
            
            index = winnerDiv.find("ძალაშია",index)
            index = winnerDiv.find(":",index)
            endIndex = winnerDiv.find("-",index)
            item["StartDate"] = winnerDiv[index+1:endIndex].strip()
            
            index = endIndex
            endIndex = winnerDiv.find("<",index)
            item["ExpiryDate"] = winnerDiv[index+1:endIndex].strip()
            
            #find the document download section
            index = winnerDiv.find('align="right',index)
            index = winnerDiv.find("href",index)
            index = winnerDiv.find('"',index)+1
            endIndex = winnerDiv.find('"',index)
            item["documentUrl"] = self.baseUrl+winnerDiv[index:endIndex]
            
            yield item
            
            #check for contract amendment
            if resultsDividers.__len__() > 3:
                amendments = resultsDividers[3]
                #just to be sure
                if amendments.find("ხელშეკრულების ცვლილება"):
                    #get all amendments
                    xAmendmentsTable = resultsDividersXPath[3]
                    xAmendments = xAmendmentsTable.select('.//tr')
                    for amendment in xAmendments:
                        amendmentHtml = amendment.extract()
                        item = TenderAgreement()
                        item["tenderID"] = tenderID
     
                        item["AmendmentNumber"] = str(amendmentNumber + 1)
                        item["OrgUrl"] = orgUrl
                        
                        if amendmentHtml.find("დისკვალიფიკაცია") > -1 :
                            #disqualified after an agreement was already signed
                            #need to revisit which values get set here
                            item["Amount"] = "NULL"                                 
                            item["StartDate"] = "NULL"                                 
                            item["ExpiryDate"] = "NULL"
                            item["documentUrl"] = "NULL"
                            yield item
                        else :
                            index = amendmentHtml.find("ნომერი/თანხა")
                            endIndex = amendmentHtml.find("ლარი",index)
                            index = amendmentHtml.rfind("/",index,endIndex)
                            item["Amount"] = amendmentHtml[index+1:endIndex].strip()
                            
                            index = amendmentHtml.find("ძალაშია",index)
                            index = amendmentHtml.find(":",index)
                            endIndex = amendmentHtml.find("-",index)
                            item["StartDate"] = amendmentHtml[index+1:endIndex].strip()
                            
                            index = endIndex
                            endIndex = amendmentHtml.find("<",index)
                            item["ExpiryDate"] = amendmentHtml[index+1:endIndex].strip()
                            
                            #find the document download section
                            index = amendmentHtml.find('align="right',index)
                            index = amendmentHtml.find("href",index)
                            index = amendmentHtml.find('"',index)+1
                            endIndex = amendmentHtml.find('"',index)
                            item["documentUrl"] = self.baseUrl+amendmentHtml[index:endIndex]
                            yield item

                
    
    def parseBidsPage(self,response):
        #print "parsing bids"
        hxs = HtmlXPathSelector(response)
        bidRows = hxs.select('//div[contains(@id, "app_bids")]//table[last()]/tbody//tr').extract()
        if bidRows.__len__() == 0:
            return
        for bidder in bidRows:        
            item = TenderBidder()
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
            
            item["numberOfBids"] = 0
            
            yield item
            
            #now lets use the company id to scrape the company data
            url = self.baseUrl+"lib/controller.php?action=profile&org_id="+item['OrgUrl']
            organisation_request = Request(url, callback=self.parseOrganisation, cookies={"SPALITE":self.sessionCookie})
            organisation_request.headers.setdefault('User-Agent', 'Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US))')     
            organisation_request.meta['OrgUrl'] = item['OrgUrl']
            organisation_request.meta['type'] = "biddingOrg"
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
            yield item
        
    
    def parseOrganisation(self,response):
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
    
    def parseTender(self, response):
        self.tenderCount = self.tenderCount + 1
        print "parsing Tender: "+str(self.tenderCount)
        hxs = HtmlXPathSelector(response)
        keyPairs = hxs.select('//tr/td').extract()  
        item = Tender()
   
        item['tenderID'] =  response.meta['tenderUrl']
        
        index = keyPairs[7].find("ShowProfile")
        index = keyPairs[7].find("(",index)
        endIndex = keyPairs[7].find(")",index)
        item['procuringEntityUrl'] = keyPairs[7][index+1:endIndex]
        
        index = keyPairs[7].find("<img")
        index = keyPairs[7].find(">", index)
        endIndex = keyPairs[7].find("</",index)
        item['procuringEntityName'] = keyPairs[7][index+1:endIndex].strip()
        
        index = keyPairs[1].find(">")
        endIndex = keyPairs[1].find("<",index)
        item['tenderType'] = keyPairs[1][index+1:endIndex].strip()
        
        index = keyPairs[3].find("strong")
        index = keyPairs[3].find(">",index)
        endIndex = keyPairs[3].find("<",index)
        item['tenderRegistrationNumber'] = keyPairs[3][index+1:endIndex]

        index = keyPairs[5].find("img")
        index = keyPairs[5].find(">",index)
        endIndex = keyPairs[5].find("<",index)
        item['tenderStatus'] = keyPairs[5][index+1:endIndex].strip()
        
        index = keyPairs[9].find(">")
        endIndex = keyPairs[9].find("<",index)
        item['tenderAnnouncementDate'] = keyPairs[9][index+1:endIndex]
        
        index = keyPairs[11].find(">")
        endIndex = keyPairs[11].find("<",index)
        item['bidsStartDate'] = keyPairs[11][index+1:endIndex]
        
        index = keyPairs[11].find(">")
        endIndex = keyPairs[11].find("<",index)
        item['bidsEndDate'] = keyPairs[13][index+1:endIndex]
        
        index = keyPairs[15].find("span")
        index = keyPairs[15].find(">",index)
        endIndex = keyPairs[15].find("<",index)
        item['estimatedValue'] = keyPairs[15][index+1:endIndex].replace("`","").replace("GEL","").strip()
        
        #item['includeVat']
        index = keyPairs[19].find("/strong")
        index = keyPairs[19].find(">",index)
        endIndex = keyPairs[19].find("<",index)
        item['cpvCode'] = keyPairs[19][index+1:endIndex].strip() 
        
        index = keyPairs[25].find("blabla")
        index = keyPairs[25].find(">",index)
        endIndex = keyPairs[25].find("</",index)
        item['info'] = keyPairs[25][index+1:endIndex]
        
        index = keyPairs[27].find(">")
        endIndex = keyPairs[27].find("</",index)
        item['amountToSupply'] = keyPairs[27][index+1:endIndex]
        
        index = keyPairs[29].find(">")
        endIndex = keyPairs[29].find("</",index)
        item['supplyPeriod'] = keyPairs[29][index+1:endIndex]
  
        index = keyPairs[31].find(">")
        endIndex = keyPairs[31].find("</",index)
        item['offerStep'] = keyPairs[31][index+1:endIndex]

        index = keyPairs[33].find(">")
        endIndex = keyPairs[33].find("</",index)
        item['guaranteeAmount'] = keyPairs[33][index+1:endIndex]

        index = keyPairs[35].find(">")
        endIndex = keyPairs[35].find("</",index)
        item['guaranteePeriod'] = keyPairs[35][index+1:endIndex]
    
        #now lets use the procuring entity id to find more info about the procurer
        url = self.baseUrl+"lib/controller.php?action=profile&org_id="+item['procuringEntityUrl']
        procurer_request = Request(url, callback=self.parseOrganisation, cookies={"SPALITE":self.sessionCookie})
        procurer_request.headers.setdefault('User-Agent', 'Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US))')     
        procurer_request.meta['OrgUrl'] = item['procuringEntityUrl']
        procurer_request.meta['type'] = "procuringOrg"
        #yield procurer_request
        
        #now lets look at the tender documentation
        url = self.baseUrl+"lib/controller.php?action=app_docs&app_id="+item['tenderID']
        documentation_request = Request(url, callback=self.parseDocumentationPage, cookies={"SPALITE":self.sessionCookie})
        documentation_request.headers.setdefault('User-Agent', 'Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US))')  
        documentation_request.meta['tenderID'] = item['tenderID']
        #yield documentation_request
        
        #now lets look at the bids made on this tender
        url = self.baseUrl+"lib/controller.php?action=app_bids&app_id="+item['tenderID']
        bids_request = Request(url, callback=self.parseBidsPage, cookies={"SPALITE":self.sessionCookie})
        bids_request.headers.setdefault('User-Agent', 'Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US))')  
        bids_request.meta['tenderID'] = item['tenderID']
        #yield bids_request
        
        #finally lets look at the results of this tender
        url = self.baseUrl+"lib/controller.php?action=agency_docs&app_id="+item['tenderID']
        results_request = Request(url, callback=self.parseResultsPage,cookies={"SPALITE":self.sessionCookie})
        results_request.headers.setdefault('User-Agent', 'Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US))')  
        results_request.meta['tenderID'] = item['tenderID']
        #yield results_request
        
        return procurer_request, results_request, bids_request, documentation_request, item
        
    def parseTenderUrls(self, response):
        hxs = HtmlXPathSelector(response)
        tenderOnClickItems = hxs.select('//table[@id="list_apps_by_subject"]//tr//@onclick').extract()

        for tenderOnClickItem in tenderOnClickItems:
            base_tender_url = self.baseUrl+"lib/controller.php?action=app_main&app_id="
            index = tenderOnClickItem.find("ShowApp")
            index = tenderOnClickItem.find("(",index)
            endIndex = tenderOnClickItem.find(",",index)
            index_url = tenderOnClickItem[index+1:endIndex]
            tender_url = base_tender_url+index_url
            print "parsing"+tender_url
            request = Request(tender_url, callback=self.parseTender, cookies={"SPALITE":self.sessionCookie})
            request.headers.setdefault('User-Agent', 'Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US))')
            request.meta['tenderUrl'] = index_url
            
            yield request
    
    def parse(self, response):
        #Find index of last page
        hxs = HtmlXPathSelector(response)

        totalPagesButton = hxs.select('//div[@class="pager pad4px"]//button').extract()[2]
        
        index = totalPagesButton.find('/')
        endIndex = totalPagesButton.find(')',index)
        final_page = totalPagesButton[index+1:endIndex]
        
        if( final_page == -1 ):
            #print "Parsing Error... stopping"
            return
        
        print "Starting scrape"  
        for i in range(int(final_page)/2,int(final_page)/2+5):
            url = self.mainPageBaseUrl+str(i)
            request = Request(url, callback=self.parseTenderUrls, cookies={"SPALITE":self.sessionCookie})
            request.headers.setdefault('User-Agent', 'Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US))')  
            print "requesting index page: "+ str(i)
            yield request


def main():
    from scrapy import signals
    from scrapy.xlib.pydispatch import dispatcher
 
    # shut off log
    from scrapy.conf import settings
    settings.overrides['LOG_ENABLED'] = False
 
    # set up crawler
    from scrapy.crawler import CrawlerProcess
 
    crawler = CrawlerProcess(settings)
    crawler.install()
    crawler.configure()
 
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

 
    # schedule spider
    procurementSpider = ProcurementSpider()
    procurementSpider.setSessionCookie(spaLite)
    crawler.crawl(procurementSpider)

    #start engine scrapy/twisted
    print "STARTING ENGINE"
    crawler.start()
    print "ENGINE STOPPED"
 
if __name__ == '__main__':
    main()
        
        
