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
        index =0
        for index, name in enumerate(names) :
            #self, zipcode, name, clinic, address, suite, city, state, phone
            addressCom = addresses[index].text.split(",")
            suite=""

            if (addressCom[1].strip().startswith("Suite")):
                suite = addressCom[1]
                city = addressCom[2]
                zipCom = addressCom[3].split(" ")
                state = zipCom[0]
                zipcode = zipCom[1]
            else:
                city = addressCom[1]
                zipCom = addressCom[2].split(" ")
                state = zipCom[0]
                zipcode = zipCom[1]
            phone = phones[index].text
            surgen = Surgeon(zipcode,name.text.strip(),"",addressCom[0].strip(), suite.strip(),city.strip(),state.strip(),phone.strip())
            surgeons.append(surgen)
        return surgeons
    def visa_bulletin_getpage(self, urlstr, titleStr, isLocal):
        if (isLocal == False) :
            page = requests.get(urlstr)
            document = lxml.html.fromstring(page.text)
        else:
            with open(urlstr,"r") as f:
                page = f.read()
            document = lxml.html.fromstring(page)
        try:
            tbodies = document.xpath("//tbody")
            boards = []
            if (tbodies.length > 1):
                boards = fill_VB_board(tbodies[0], titleStr,True) + fill_VB_board(tbodies[1], titleStr, False)
        except ValueError:
            self.logger.fatal("Error during processing: #{$!}")
            self.logger.fatal("Backtrace:\n\t#{e.backtrace.join('\n\t')}")
            self.logger.fatal("file name " + urlstr)

    def parse_current_date(self, dateStr):
        try:
            if (dateStr in ["Update on July Visa Availability", "July 2007 Visa Bulletin"]):
                return None
            else:
                return datetime.strptime(dateStr[18:], "%B %Y")

        except ValueError:
            self.logger.fatal ("wrong current month date " + dateStr)
        return None

    def fill_VB_board(self,document, titleStr, isFamilyBased): #isFamilyBased ==True
        titleStr = self.parse_current_date(titleStr)
        rows = document.elements.css("tr")
        boards = Array.new
        hasReachHeader = false
        if (!rows.nil?)
        # rows has stuff, then construct the family based prepopulated array
        defaultTable = construct_VB_initial_table(titleStr, isFamilyBased)  # familybased ->true
        headerArray = Array.new
        rows.each
        do | row |
        # grab the header
        # count the size is the header
        if (hasReachHeader == false)
            str = row.children.inner_text  # locate the header
            parts = str.split("\n").each
            do | x |
            headerArray = create_country_header_array(x.strip, headerArray)
        end
        if (headerArray.length > 0)
            hasReachHeader = true
        end

    else  # handle the data
    visaType = ""
    str = row.children.inner_text
    _parts = str.split("\n")
    # remove white space parts
    parts = Array.new
    part = nil
    _parts.each
    do | _part |
    # strip is not removing white space, try this instead
    part = _part.gsub( /\A[[:space:]]+ | [[:space:]]+\z /, '')
    if !(part.empty?)
    parts.push(part)


end
end
if (isFamilyBased == true)
    # only proceed if the first element is what we are tracking in visatype
    if (Enums: :
        FamilyVisaTypeEnum.to_hash.keys.any? { | key | parts[0].strip.downcase.include? key.to_s.downcase})
    rowName = transfer_td1_to_visaType_enum(parts[0].strip, isFamilyBased)
    # skip the first part because it is the row name
    for i in 1..parts.length - 1
        columnName = headerArray[i - 1]
        defaultTable = locate_and_modify_defaultTable(columnName, rowName, parts[i].strip, defaultTable, headerArray)
    end
end
else
# only proceed if the first element is what we are tracking in visatype
if (Enums: :
    EmploymentVisaTypeEnum.to_hash.keys.any? { | key | parts[0].strip.downcase.include? key.to_s.downcase})
rowName = transfer_td1_to_visaType_enum(parts[0].strip, isFamilyBased)
# skip the first part because it is the row name
for i in 1..parts.length - 1
    columnName = headerArray[i - 1]
    defaultTable = locate_and_modify_defaultTable(columnName, rowName, parts[i].strip, defaultTable, headerArray)
end
end
end
end
end
end
return defaultTable
end





