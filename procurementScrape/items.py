# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class Tender(Item):
    # define the fields for your item here like:
    urlID = Field()
    procuringEntityID = Field()
    procuringEntityName = Field()
    tenderType = Field()
    tenderRegistrationNumber = Field()
    tenderStatus = Field()
    tenderAnnouncementDate = Field()
    bidsStartDate = Field()
    bidsEndDate = Field()
    estimatedValue = Field()
    cpvCode = Field()
    
    
class Organisation(Item):
    urlID = Field()
    OrgID = Field()
    Name = Field()
    Country = Field()
    Type = Field()

class TenderBidder(Item):
    urlID = Field()
    OrgID = Field()
    firstBidAmount = Field() 
    firstBidDate = Field()
    lastBidAmount = Field()
    lastBidDate = Field()
    
class TenderAgreement(Item):
    urlID = Field()
    OrgID = Field()
    Amount = Field()
    StartDate = Field()
    ExpiryDate = Field()
    