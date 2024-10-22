import pymysql
import scrapy
import time
from ics_v1.items import IcsV1SiteMapLinksItem3
from scrapy.cmdline import execute
import ics_v1.db_config as db


class LinksSpider(scrapy.Spider):
    name = 'links_brand'
    start_urls = [f'https://www.cdw.com/']

    VENDOR_ID = "ACT-B3-010"
    VENDOR_NAME = "CDW"

    def __init__(self, name=None, start=1, end=1, **kwargs):
        super().__init__(name, **kwargs)
        # DATABASE CONNECTION
        self.con = pymysql.connect(host=db.db_host, user=db.db_user, password=db.db_password, db=db.db_name)
        self.cursor = self.con.cursor()
        self.start = start
        self.end = end
        self.counter = 1

    def start_requests(self):

        select_query = [
                    f"select id, product_urls from {db.category_sitemap_final} where",
                    f"status = 'pending' and",
                    f"id between {self.start} and {self.end}"
                ]
        self.cursor.execute(" ".join(select_query))

        for data in self.cursor.fetchall():
            yield scrapy.Request(
                url=data[1],
                callback=self.parse,
                dont_filter=True,
                meta={'url':data[1],'counter':self.counter}
            )

    def parse(self, response,**kwargs):
        item = IcsV1SiteMapLinksItem3()
        url = response.meta['url']
        urls1 = response.xpath('//div[@aria-labelledby="filter-Brand"]//@data-filter-url').getall()
        urls2 = response.xpath('//div[@class="filter-item filter-item-hidden"]//@data-filter-url').getall()
        urls3 = set(urls1) | set(urls2)
        urls3 = list(urls3)

        if urls3:
            for i in urls3:
                item['vendor_id'] = self.VENDOR_ID
                item['vendor_name'] = self.VENDOR_NAME
                item['product_urls'] = 'https://www.cdw.com' + i
                yield item

            try:
                update = f'update {db.category_sitemap_final} set status="Done" where product_urls="{url}"'
                self.cursor.execute(update)
                self.con.commit()
            except Exception as e:
                print(e)


if __name__ == '__main__':
    execute(f"scrapy crawl links_brand -a start=1 -a end=227".split())
