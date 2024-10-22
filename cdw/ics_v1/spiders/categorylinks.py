import re

import pymysql
import scrapy

from ics_v1.items import IcsV1SiteMapLinksItem3
from scrapy.cmdline import execute
import ics_v1.db_config as db
from scrapy.utils.response import open_in_browser

class CategorylinksSpider(scrapy.Spider):
    name = "categorylinks"
    allowed_domains = ["www.cdw.com"]
    start_urls = ["https://www.cdw.com/"]

    VENDOR_ID = "ACT-B3-010"
    VENDOR_NAME = "CDW"

    def __init__(self, start, end, name=None, **kwargs):
        super().__init__(name, **kwargs)
        # DATABASE CONNECTION
        self.con = pymysql.connect(host=db.db_host, user=db.db_user, password=db.db_password, db=db.db_name)
        self.cursor = self.con.cursor()
        self.start = start
        self.end = end
        self.counter = 1

    def start_requests(self):
        yield scrapy.Request(
            # url = 'https://www.cdw.com/header/1.14/dist/scripts/a/globalheader.js'
            url = 'https://www.cdw.com/header/1.14/dist/scripts/a/globalheader.js'
        )


    def parse(self, response, **kwargs):
        link = re.findall('u=\[\{name:"Hardware"(.*?)Storage & Hard Drives(.*?)}',response.text)
        catlinks = []
        for links in (" ".join(link[0]).split(",")):
            if 'url' in links and 'content' in links and 'en/products/' in links:
                if not re.findall('\/(.*?)\/(.*?)\/(.*?)\/(.*?)\/(.*?)\/(.*?)\.html',links):
                    link=re.findall('"(.*?)"',links)
                    catlinks.append(self.start_urls[0][:-1]+link[0].replace('cdwg','cdw'))

        unique_cat_links = set(catlinks)
        count=0
        for index,unique_link in enumerate(unique_cat_links):
            count+=1

            yield scrapy.Request(
                url = unique_link,
                callback=self.subcatlink,
                cb_kwargs={'number':count}
            )



    def subcatlink(self, response, **kwargs):
        open_in_browser(response)
        sublinks=response.xpath('//div[@class="grid-column-inner"]/div[@class="cdwrteatom parbase section"]/ul/li/span/a/@href | //div[@class="grid-column-inner"]/div[@class="cdwrteatom parbase section"]/ul/li//a/@href').getall()
        for link in sublinks:
            with open('link/links.txt', 'a') as data:
                data.write(f"{kwargs['number']} :- {self.start_urls[0][:-1]+link}\n")

if __name__ == '__main__':
    execute(f"scrapy crawl categorylinks -a start=0 -a end=1".split())