import lxml.html
import requests
import requests.packages.urllib3

from datetime import datetime
from lxml.cssselect import CSSSelector
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from src.poco.case_info import CaseInfo
from src.poco.processing_center_enum import ProcessingCenterEnum
from src.poco.surgeon import Surgeon


class NetworkHelper:
    def __init__(self, logger):
        self.logger = logger
        self.blacklist = ["Update on July Visa Availability",
                          "July 2007 Visa Bulletin",
                          "USCIS Announces Revised Procedures for Determining Visa Availability for Applicants Waiting to File for Adjustment of Status."]
        self.visaboardMaps = {};

    def parse_current_date(self, dateStr):
        if (dateStr == "Update on Luly Visa Availability"):
            return None
        elif (dateStr == "July 2007 Visa Bulletin"):
            return None
        else:
            try:
                date = datetime.strptime(dateStr[18:], "%B %Y")
            except ValueError:
                date = datetime.strptime(dateStr[14:], "%B %Y")
            return date

    def visa_bulletin_geturls(self, urlstr):
        if (urlstr == None):
            urlstr = "http://travel.state.gov/content/visas/english/law-and-policy/bulletin.html"
        else:
            page = requests.get(urlstr)
            document = lxml.html.fromstring(page.text)
            self.logger.info("load the html into document")
            sel = CSSSelector("div.expandos a")
            ahrefs = sel(document)
            for ahref in ahrefs:
                if (ahref.text not in self.blacklist):
                    self.visaboardMaps.update(
                        {self.parse_current_date(ahref.text): "http://travel.state.gov" + ahref.get("href")})

    def usciscaselookup(self,casenumber):
        post_params ={"appReceiptNum": casenumber}
        urlStr = "https://egov.uscis.gov/casestatus/mycasestatus.do"
        requests.packages.urllib3.disable_warnings()
        response = requests.post(urlStr, data=post_params, verify = False)
        document = lxml.html.fromstring(response.text)
        statusSel = CSSSelector("div.rows.text-center h1")
        detailSel = CSSSelector("div.rows.text-center p")
        status = (statusSel(document))[0].text
        detail = (detailSel(document))[0].text
        processingcenter = (ProcessingCenterEnum[casenumber[0:3]]).value
        receiptyear = "20"+ casenumber[3:3+2]
        computerWorkDay = casenumber[5:5+3]
        caseinfo = CaseInfo(casenumber, status,detail,processingcenter,receiptyear,computerWorkDay)
        return caseinfo
    def uscis_civil_surgeons_lookup(self,zipcode):
        post_params = {"OfficeLocator.office_type" : "CIV", "OfficeLocator.zipcode" : zipcode}
        urlStr = "https://egov.uscis.gov/crisgwi/go?action=offices.summary"
        requests.packages.urllib3.disable_warnings()
        response = requests.post(urlStr, data=post_params, verify=False)
        document = lxml.html.fromstring(response.text)
        nameSel = CSSSelector("div#positioningDiv table#body td#content li ul li b")
        addressSel = CSSSelector("div#positioningDiv table#body td#content li ul li span.civAddress")
        phoneSel = CSSSelector("div#positioningDiv table#body td#content li ul li span.civPhone")
        names = nameSel(document)
        addresses = addressSel(document)
        phones = phoneSel(document)
        surgeons = []

        for index, name in names :
            #self, zipcode, name, clinic, address, suite, city, state, phone
            addressCom = addresses[index].text.split(",")
            if (addressCom[1].text.startswith("Suite")):
                suite = addressCom[1].text
            surgen = Surgeon(zipcode,name.text,"",addressCom[0], suite,)



