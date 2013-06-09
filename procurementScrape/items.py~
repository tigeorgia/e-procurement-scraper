# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class Tender(Item):
  # define the fields for your item here like:
  tenderID = Field()
  procuringEntityUrl = Field()
  procuringEntityName = Field()
  tenderType = Field()
  tenderRegistrationNumber = Field()
  tenderStatus = Field()
  tenderAnnouncementDate = Field()
  bidsStartDate = Field()
  bidsEndDate = Field()
  estimatedValue = Field()
  cpvCode = Field()
  info = Field()
  amountToSupply = Field()
  supplyPeriod = Field()
  offerStep = Field()
  guaranteeAmount = Field()
  guaranteePeriod = Field()

class CPVCode(Item):
  tenderID = Field()
  cpvCode = Field()
  description = Field()
    
    
class Organisation(Item):
  OrgID = Field()
  OrgUrl = Field()
  Name = Field()
  Country = Field()
  city = Field()
  address = Field()
  phoneNumber = Field()
  faxNumber = Field()
  email = Field()
  webpage = Field()
  Type = Field()

class TenderBidder(Item):
  tenderID = Field()
  OrgUrl = Field()
  firstBidAmount = Field() 
  firstBidDate = Field()
  lastBidAmount = Field()
  lastBidDate = Field()
  numberOfBids = Field()
    
class TenderAgreement(Item):
  tenderID = Field()
  AmendmentNumber = Field()
  OrgUrl = Field()
  Amount = Field()
  StartDate = Field()
  ExpiryDate = Field()
  documentUrl = Field()

class TenderDocument(Item):
  tenderID = Field()
  documentUrl = Field()
  title = Field()
  author = Field()
  date = Field()

class WhiteListObject(Item):
	orgID = Field()
	orgName = Field()
	issueDate = Field()
	agreementUrl = Field()
	companyInfoUrl = Field()

class BlackListObject(Item):
  orgID = Field()
  orgName = Field()
  issueDate = Field()
  procurer = Field()
  tenderID = Field()
  tenderNum = Field()
  reason = Field()

class Complaint(Item):
  status = Field()
  orgName = Field()
  orgID = Field()
  issueDate = Field()
  tenderID = Field()
  complaint = Field()
  legalBasis = Field()
  demand = Field()
