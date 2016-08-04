import lxml.html
import requests
from datetime import datetime
from lxml.cssselect import CSSSelector



class NetworkHelper:

    def __init__(self, logger) :
        self.logger = logger
        self.blacklist = ["Update on July Visa Availability", "July 2007 Visa Bulletin",
                          "USCIS Announces Revised Procedures for Determining Visa Availability for Applicants Waiting to File for Adjustment of Status."]
        self.visaboardMaps = {};

    def parse_current_date(self,dateStr):
        if (dateStr == "Update on Luly Visa Availability") :
            return None
        elif (dateStr == "July 2007 Visa Bulletin") :
            return None
        else :
            date =None
            try:
                date = datetime.strptime(dateStr[18:], "%B %Y")
            except ValueError:
                date = datetime.strptime(dateStr[14:], "%B %Y")
            return date

    def visa_bulletin_geturls(self,urlstr):
        if (urlstr == None) :
           urlstr = "http://travel.state.gov/content/visas/english/law-and-policy/bulletin.html"
        else :
           page = requests.get(urlstr)
           document = lxml.html.fromstring(page.text)
           self.logger.info("load the html into document")
           sel = CSSSelector("div.expandos a")
           ahrefs = sel(document)
           for ahref in ahrefs:
               if (ahref.text not in self.blacklist):
                   self.visaboardMaps.update({self.parse_current_date(ahref.text):"http://travel.state.gov"+ahref.get("href")})
