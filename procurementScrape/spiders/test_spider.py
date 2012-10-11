#! /usr/bin/env python
#encoding:UTF-8


from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider
from scrapy.http import Request
from procurementScrape.items import Tender, Organisation, TenderBidder, TenderAgreement
from time import sleep
import httplib2

class ProcurementSpider(BaseSpider):
    name = "procurement"
    allowed_domains = ["procurement.gov.ge", "tenders.procurement.gov.ge"]
    start_urls = ["http://procurement.gov.ge/index.php?sec_id=1&lang_id=ENG"]
    
    def setSessionCookie(self,sessionCookie):
        self.sessionCookie = sessionCookie
    
    
    def parseResultsPage(self,response):
        print "parsing results"
        #<div id="agency_docs">
        #<div class="pad4px">
        #<div class="pad4px centrshi">
        #<div class="ui-state-highlight ui-corner-all" style="margin:2em;padding:0.5em">
        hxs = HtmlXPathSelector(response)
        resultsDividers = hxs.select('//div[contains(@id, "agency_docs")]//div').extract()
        test = hxs.select('//div[contains(@class, "ui-state-highlight ui-corner-all")]').extract()
        if resultsDividers.__len__() >= 3:
            winnerDiv = resultsDividers[2]
            
            #check for disqualifications
            if winnerDiv.find("დისკვალიფიკაცია ტექნიკური დოკუმენტაციის გამო") > -1 :
                return
            
            item = TenderAgreement()
            item["urlID"] = response.meta['urlID']
            
            index = winnerDiv.find("ShowProfile")
            index = winnerDiv.find("(",index)
            endIndex = winnerDiv.find(")",index)
            item["OrgID"] = winnerDiv[index+1:endIndex]
            
            index = winnerDiv.find("ნომერი/თანხა:")
            index = winnerDiv.find(":",index)
            endIndex = winnerDiv.find("<",index)  
            item["Amount"] = winnerDiv[index+2:endIndex]
            
            index = winnerDiv.find("ძალაშია",index)
            index = winnerDiv.find(":",index)
            endIndex = winnerDiv.find("-",index)
            item["StartDate"] = winnerDiv[index+1:endIndex]
            
            index = endIndex
            endIndex = winnerDiv.find("<",index)
            item["ExpiryDate"] = winnerDiv[index+1:endIndex]
            
            yield item
    
    def parseBidsPage(self,response):
        print "parsing bids"
        hxs = HtmlXPathSelector(response)
        bidRows = hxs.select('//div[contains(@id, "app_bids")]//table[last()]/tbody//tr').extract()
        if bidRows.__len__() == 0:
            return
        for bidder in bidRows:        
            item = TenderBidder()
            item["urlID"] = response.meta['urlID']
            
            index = bidder.find("ShowProfile")
            index = bidder.find("(",index)
            endIndex = bidder.find(")",index)
            item["OrgID"] = bidder[index+1:endIndex]
    
            index = bidder.find("strong")
            index = bidder.find(">",index)
            endIndex = bidder.find("<",index)
            item["firstBidAmount"] = bidder[index+1:endIndex]
            
            index = bidder.find("date",index)
            index = bidder.find(">",index)
            endIndex = bidder.find("<",index)
            item["firstBidDate"] = bidder[index+1:endIndex]
            
            index = bidder.find("activebid1",index)
            index = bidder.find(">",index)
            endIndex = bidder.find("<",index)
            item["lastBidAmount"] = bidder[index+1:endIndex]
            
            index = bidder.find("date",index)
            index = bidder.find(">",index)
            endIndex = bidder.find("<",index)
            item["lastBidDate"] = bidder[index+1:endIndex]
            yield item
            
            #now lets use the company id to scrape the company data
            url = "https://tenders.procurement.gov.ge/public/lib/controller.php?action=profile&org_id="+item['OrgID']
            organisation_request = Request(url, callback=self.parseOrganisation, cookies={"SPALITE":self.sessionCookie})
            organisation_request.headers.setdefault('User-Agent', 'Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US))')     
            organisation_request.meta['urlID'] = item['OrgID']
            organisation_request.meta['type'] = "biddingOrg"
            yield organisation_request
    
    def parseOrganisation(self,response):
        print "parsing procurer"
        hxs = HtmlXPathSelector(response)
        keyPairs = hxs.select('//div[contains(@id, "profile_dialog")]//tr').extract()
        item = Organisation()
        index = keyPairs[0].find("label")
        index = keyPairs[0].find(">",index)
        endIndex = keyPairs[0].find("<",index)
        item["Name"] = keyPairs[0][index+1:endIndex]
        
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
        item["urlID"] = response.meta['urlID']
        item["Type"] = response.meta['type']
        
        #[0] = entity#[1] = id #[2] = country #[3] = city  #[4] = address    #[5] = phone    #6 = fax #7 email #8 website #9contact
        return item
    
    def parseTender(self, response):
        print "parsing Tender"
        hxs = HtmlXPathSelector(response)
        keyPairs = hxs.select('//tr/td').extract()  
        item = Tender()
   
        item['urlID'] =  response.meta['urlID']
        
        index = keyPairs[7].find("ShowProfile")
        index = keyPairs[7].find("(",index)
        endIndex = keyPairs[7].find(")",index)
        item['procuringEntityID'] = keyPairs[7][index+1:endIndex]
        
        index = keyPairs[7].find("<img")
        index = keyPairs[7].find(">", index)
        endIndex = keyPairs[7].find("</",index)
        item['procuringEntityName'] = keyPairs[7][index+1:endIndex]
        
        index = keyPairs[1].find(">")
        endIndex = keyPairs[1].find("<",index)
        item['tenderType'] = keyPairs[1][index+1:endIndex]
        
        index = keyPairs[3].find("strong")
        index = keyPairs[3].find(">",index)
        endIndex = keyPairs[3].find("<",index)
        item['tenderRegistrationNumber'] = keyPairs[3][index+1:endIndex]

        index = keyPairs[5].find("img")
        index = keyPairs[5].find(">",index)
        endIndex = keyPairs[5].find("<",index)
        item['tenderStatus'] = keyPairs[5][index+1:endIndex]
        
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
        item['estimatedValue'] = keyPairs[15][index+1:endIndex]
        
        #item['includeVat']
        index = keyPairs[19].find("/strong")
        index = keyPairs[19].find(">",index)
        endIndex = keyPairs[19].find("<",index)
        item['cpvCode'] = keyPairs[19][index+1:endIndex]
    
        #now lets use the procuring entity id to find more info about the procurer
        url = "https://tenders.procurement.gov.ge/public/lib/controller.php?action=profile&org_id="+item['procuringEntityID']
        procurer_request = Request(url, callback=self.parseOrganisation, cookies={"SPALITE":self.sessionCookie})
        procurer_request.headers.setdefault('User-Agent', 'Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US))')     
        procurer_request.meta['urlID'] = item['procuringEntityID']
        procurer_request.meta['type'] = "procuringOrg"
        
        
        #now lets look at the bids made on this tender
        url = "https://tenders.procurement.gov.ge/public/lib/controller.php?action=app_bids&app_id="+item['urlID']
        bids_request = Request(url, callback=self.parseBidsPage, cookies={"SPALITE":self.sessionCookie})
        bids_request.headers.setdefault('User-Agent', 'Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US))')  
        bids_request.meta['urlID'] = item['urlID']
        
        #finally lets look at the results of this tender
        url = "https://tenders.procurement.gov.ge/public/lib/controller.php?action=agency_docs&app_id="+item['urlID']
        results_request = Request(url, callback=self.parseResultsPage,cookies={"SPALITE":self.sessionCookie})
        results_request.headers.setdefault('User-Agent', 'Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US))')  
        results_request.meta['urlID'] = item['urlID']
         
        return item, procurer_request, results_request
        
    def parseTenderUrls(self, response):
        print "Got response"
        hxs = HtmlXPathSelector(response)
        print "recieved hxs"
        tender_links = hxs.select('//a[@class="news_title"]/@href').extract()

        for tender_url in tender_links:
            print "found url: "+tender_url
            base_tender_url = "https://tenders.procurement.gov.ge/public/lib/controller.php?action=app_main&app_id="
            index = tender_url.find("=")
            index_url = tender_url[index+1:]
            tender_url = base_tender_url+index_url
            print "modified url: "+tender_url
            request = Request(tender_url, callback=self.parseTender, cookies={"SPALITE":self.sessionCookie})
            request.headers.setdefault('User-Agent', 'Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US))')
            request.meta['urlID'] = index_url
            
            yield request
    
    def parse(self, response):
        #Find index of last page
        hxs = HtmlXPathSelector(response)
        link_string = hxs.select('//div[@class="pager"]//a[last()]/@href').extract()[0]
        start = link_string.find('entrant=')
        end = link_string.find('&',start)
        index = -1
        final_page = -1
        if( end == -1 ):
            index = link_string.find('=',start)
            final_page = link_string[index+1:]
        else:
            index = link_string.find('=',start,end)
            final_page = link_string[index+1:end]
        
        if( final_page == -1 ):
            print "Parsing Error... stopping"
            return
        
        print "Starting scrape"
        base_link = "http://procurement.gov.ge/index.php?sec_id=0&info_id=0&mod_id=0&new_year=0&limit=0&date=&new_month=&lang_id=&entrant="
        
        requests = []
        for i in range(200,203): #,int(final_page)+1):
            url = base_link+str(i)
            request = Request(url, callback=self.parseTenderUrls, cookies={"SPALITE":self.sessionCookie})
            print "returning request"
            requests.append(request)
        return requests


def main():
    from scrapy import signals
    from scrapy.xlib.pydispatch import dispatcher
 
    def catch_item(sender, item, **kwargs):
        print "Got:", item
 
    dispatcher.connect(catch_item, signal=signals.item_passed)
 
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
        
        