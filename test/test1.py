
import logging

from src.utils.network_helper import NetworkHelper


def main():
    with open("app.log", "w") as file:
        file.truncate()
    logging.basicConfig(filename="app.log",
                        format='%(asctime)s %(levelname)s %(message)s',
                        level= logging.DEBUG,
                        mode ="w")


    logging.info("start this")
    networkhelper = NetworkHelper(logging)
    urlStr = "http://travel.state.gov/content/visas/english/law-and-policy/bulletin.html"
    networkhelper.visa_bulletin_geturls(urlStr)
    for key, value in networkhelper.visaboardMaps.iteritems():
        logging.debug(key.strftime("%A %d. %B %Y")+"=====>"+ value)
    logging.info("end")

if __name__=="__main__" :
    main()