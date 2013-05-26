#!/usr/bin/env python

import json
import logging
import logging.handlers
import sys

import scraperwiki


# Setup log.
logger = logging.getLogger('austin_tx_traffic_incidents')
logger.setLevel(logging.DEBUG)
if sys.platform == "darwin":
    handler = logging.handlers.SysLogHandler(address = '/var/run/syslog')
else:
    handler = logging.handlers.SysLogHandler(address = '/dev/log')
logger.addHandler(handler)
# Create a formatter so messages don't show up as Unknown.
formatter = logging.Formatter('%(name)s: [%(levelname)s] %(message)s')
handler.setFormatter(formatter)

def main():
    # Scrape the website.
    # This doesn't involve too much manipulation as this URL returns JSONP.
    jsonpstring = scraperwiki.scrape("http://www.austintexas.gov/GIS/TrafficViewer/Home/JsonpIncidents/query?f=json&where=1%3D1&returnGeometry=true&spatialRel=esriSpatialRelIntersects&outFields=*&outSR=4326&callback=f")
    lines = jsonpstring.split(";")
    jsons = [l[2:-1] for l in lines if l.strip() != ""]
    data = json.loads(jsons[0])
    logger.debug("Fetched {0} incidents.".format(len(data["features"])))

    # Save the data : convert into records
    records = []
    for row in data["features"]:
        record = {}
        records.append(record)
        record["x"] = row["geometry"]["x"]
        record["y"] = row["geometry"]["y"]
        for attribute in row["attributes"]:
            record[attribute] = row["attributes"][attribute]

    # Save in sqlite.
    scraperwiki.sqlite.save(unique_keys=["Address",
          "CrossStreet",
          "CurrentDate"],
        data=records)



if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception(e)
        raise

