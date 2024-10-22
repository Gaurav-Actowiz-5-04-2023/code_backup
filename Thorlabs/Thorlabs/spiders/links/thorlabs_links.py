import json
import pymysql
import scrapy
from scrapy.cmdline import execute
from Thorlabs import db_config as db
from Thorlabs.items import IcsV1SiteMapLinksItem

head={
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',

}

class ThorlabsSpider(scrapy.Spider):
    name = "thorlabs"
    allowed_domains = ["www.thorlabs.com"]
    start_urls = ["https://www.thorlabs.com/navigation.cfm"]
    start = "https://www.thorlabs.com/"
    # Site information :-
    VENDOR_ID = "ACT-B1-002"
    VENDOR_NAME = "Thorlabs"

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        # DATABASE CONNECTION
        self.con = pymysql.connect(host=db.db_host, user=db.db_user, password=db.db_password, db=db.db_name)
        self.cursor = self.con.cursor()

    def parse(self, response, **kwargs):
        for index,catlink in enumerate(response.xpath('//div[@class="vis-nav-group"]/a')):
            if not index:
                meta_data = list()
                catdict = dict()
                catdict['url'] = self.start + catlink.xpath("./@href").get()
                catdict['name'] = catlink.xpath("./text()").get()
                meta_data.append(catdict)
                for subcatlink in catlink.xpath('./following-sibling::div/a'):
                    subcatdict = dict()
                    subcatdict['url'] = self.start + subcatlink.xpath("./@href").get()
                    subcatdict['name'] = subcatlink.xpath(".//text()").get()
                    meta_data.append(subcatdict)
                    yield scrapy.Request(
                        url=subcatdict['url'],
                        cb_kwargs={'meta_data':meta_data.copy()},
                        callback=self.category_make
                    )
                    meta_data.pop()

    def category_make(self, response, **kwargs):
        # making meta_data using above dictionary :-
        meta_data = list()
        for category_dictionary in kwargs['meta_data']:
            meta_data.append(category_dictionary)

        if response.xpath('//div[@id="navBoxContainer"]/a'):
            for links in response.xpath('//div[@id="navBoxContainer"]/a'):
                linkdict = dict()
                linkdict['url'] = self.start + "/" + links.xpath("./@href").get()
                linkdict['name'] = " ".join(links.xpath(".//text()").getall())
                meta_data.append(linkdict)
                # print(meta_data)
                yield scrapy.Request(
                    url=linkdict['url'],
                    cb_kwargs={'meta_data': meta_data.copy()},
                    callback=self.category_make,
                    # dont_filter=True
                )
                meta_data.pop()

        elif response.xpath('//td[contains(@class,"prodNumber")]/a'):
            for pdplinks in response.xpath('//td[contains(@class,"prodNumber")]/a'):
                product_urls = self.start+pdplinks.xpath('./@href').get()
                item = IcsV1SiteMapLinksItem()
                item['vendor_id'] = self.VENDOR_ID
                item['vendor_name'] = self.VENDOR_NAME
                item['product_urls'] = product_urls
                item['meta_data'] = json.dumps(meta_data, ensure_ascii=False)
                yield item


if __name__ == '__main__':
    execute("scrapy crawl thorlabs".split())