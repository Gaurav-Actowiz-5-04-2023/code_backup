import datetime
import os.path

import pymysql
import scrapy
from scrapy.cmdline import execute
from scrapy.utils.response import open_in_browser
import hashlib

from Thorlabs import db_config as db


class DownloadAssestSpider(scrapy.Spider):
    name = 'download_assest'
    assets_save = 'D:/Data/gaurav/Assets/october/'
    handle_httpstatus_list = [404, 400, 502, 301]

    date = datetime.datetime.now()
    month = date.strftime('%B')

    def __init__(self, start,end, name=None, vendor_id=None, **kwargs):
        super().__init__(name, **kwargs)
        if not vendor_id:
            exit(-1)
        self.VENDOR_ID = vendor_id
        self.assets_save += vendor_id + f"{self.month}/"
        if not os.path.exists(self.assets_save):
            os.makedirs(self.assets_save)

        self.con = pymysql.connect(host=db.db_host, user=db.db_user, password=db.db_password, db=db.db_name)
        self.cursor = self.con.cursor()
        self.start = start
        self.end = end

    def start_requests(self):
        select_query = [
            f"select id, source, file_name, is_main_image, name from {db.asset_table} where",
            f"vendor_id = '{self.VENDOR_ID}'",
            f"and status = 'pending'",
            f"and id between {self.start} and {self.end}"
        ]

        self.cursor.execute(" ".join(select_query))

        cookies = {
            'LANGUAGE': 'ENGLISH',
            'LANGABBR': 'EN',
            'visid_incap_893434': 'j6qdoUC+SRmUfFRl/Y3xAXtdt2UAAAAAQUIPAAAAAADt8Agv9mJQSt0LEIk/1RmQ',
            '__utmz': '71944534.1706515838.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
            '_ga': 'GA1.1.968803150.1706515842',
            'ai_user': 'Lf2ov|2024-01-29T08:10:42.211Z',
            'LPVID': 'M1MzQ0ZTkwMjgyODgwNmU5',
            '_ga_PQ7M4FRQ4E': 'deleted',
            'CFID': '22986211',
            'CFTOKEN': '2f3fe7d2fbc96660-50D103CC-C11B-2B5F-ABC171FF09FC185D',
            '__utma': '71944534.193177393.1706515838.1707369748.1707385065.27',
            'reese84': '3:iyj15yqCi7ujMB8WONEvzA==:K0cs2/9yA33lgjo/qFWa9L22FQPptw/262ZExxbmqi2FGC/YuhpOvYTFzYZkIILIoSrJpOaOWe7BJ3zQxmSpoV0x8GFlpXzDMBXVhc7yevFKHi8VG2paFCEsWPdKmYgl5cJTps+hNwhA8Vj01jyHah6Zna2MmkM3TEeJOLdKXE2SxzKENJtzPbHSoPo3V1Z6WkeZMMAyoNBI0Rcj+yw/4dpLPqZsbUuuqEeYU6CwbBxJxe3cPD7mVG66s0lHwKcL1oX+Y5R5xFy7SxGO9lBPuUvMW94iVWbpEudzD6uzrlThk2fNKgLA/Uyy5sbJ+P3IDQ/wS+viDZA9AzWjC8KAGIKr8FPViRYSTEk94A2D+Au8/VjUQCzlq3Ws6tkJBsMAzoNaPKy96WBG/j0e1EXm4E6NVJ5b33LhT88VGJNxRz/OcWdx+DvA4g0KS0VcVBtNkS4Kb/EX02L5FJRTdvs12g==:X+tDY0k7w+Rq5TB6PldBe2OD/Yq8EbMlpGXEyre7nnU=',
            '__utmb': '71944534.2.10.1707385065',
            'ai_session': 'fuW8w|1707385065366|1707385073901',
            '_ga_PQ7M4FRQ4E': 'GS1.1.1707385064.29.1.1707385080.0.0.0',
            'LOADCURRENCY': 'Dollar',
            'LOADCURRENCYSYMBOL': '%24',
            'ROITRACK': '1',
            'LOADCOUNTRY': 'IN',
            'nlbi_893434': 'MrUXcxrV3GBfdm39UtRJRQAAAAAUbX0ThPVlSPJ4uNoZcjFm',
            'incap_ses_50_893434': 'Hmy/CNnQYUfD7/YIEKOxALGlxGUAAAAAc88QbYOEpWYeft41QiBK9Q==',
        }

        headers = {
            'authority': 'www.thorlabs.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            # 'cookie': 'LANGUAGE=ENGLISH; LANGABBR=EN; visid_incap_893434=j6qdoUC+SRmUfFRl/Y3xAXtdt2UAAAAAQUIPAAAAAADt8Agv9mJQSt0LEIk/1RmQ; __utmz=71944534.1706515838.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _ga=GA1.1.968803150.1706515842; ai_user=Lf2ov|2024-01-29T08:10:42.211Z; LPVID=M1MzQ0ZTkwMjgyODgwNmU5; _ga_PQ7M4FRQ4E=deleted; CFID=22986211; CFTOKEN=2f3fe7d2fbc96660-50D103CC-C11B-2B5F-ABC171FF09FC185D; __utma=71944534.193177393.1706515838.1707369748.1707385065.27; reese84=3:iyj15yqCi7ujMB8WONEvzA==:K0cs2/9yA33lgjo/qFWa9L22FQPptw/262ZExxbmqi2FGC/YuhpOvYTFzYZkIILIoSrJpOaOWe7BJ3zQxmSpoV0x8GFlpXzDMBXVhc7yevFKHi8VG2paFCEsWPdKmYgl5cJTps+hNwhA8Vj01jyHah6Zna2MmkM3TEeJOLdKXE2SxzKENJtzPbHSoPo3V1Z6WkeZMMAyoNBI0Rcj+yw/4dpLPqZsbUuuqEeYU6CwbBxJxe3cPD7mVG66s0lHwKcL1oX+Y5R5xFy7SxGO9lBPuUvMW94iVWbpEudzD6uzrlThk2fNKgLA/Uyy5sbJ+P3IDQ/wS+viDZA9AzWjC8KAGIKr8FPViRYSTEk94A2D+Au8/VjUQCzlq3Ws6tkJBsMAzoNaPKy96WBG/j0e1EXm4E6NVJ5b33LhT88VGJNxRz/OcWdx+DvA4g0KS0VcVBtNkS4Kb/EX02L5FJRTdvs12g==:X+tDY0k7w+Rq5TB6PldBe2OD/Yq8EbMlpGXEyre7nnU=; __utmb=71944534.2.10.1707385065; ai_session=fuW8w|1707385065366|1707385073901; _ga_PQ7M4FRQ4E=GS1.1.1707385064.29.1.1707385080.0.0.0; LOADCURRENCY=Dollar; LOADCURRENCYSYMBOL=%24; ROITRACK=1; LOADCOUNTRY=IN; nlbi_893434=MrUXcxrV3GBfdm39UtRJRQAAAAAUbX0ThPVlSPJ4uNoZcjFm; incap_ses_50_893434=Hmy/CNnQYUfD7/YIEKOxALGlxGUAAAAAc88QbYOEpWYeft41QiBK9Q==',
            'if-modified-since': 'Tue, 10 Apr 2018 21:01:57 GMT',
            'if-none-match': '"0493729fd1d31:0"',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        }

        for data in self.cursor.fetchall():
            print(data)
            yield scrapy.Request(
                url=data[1],
                cookies=cookies,
                headers=headers,
                cb_kwargs={
                    "id": data[0],
                    "file_name": data[2],
                    "main": data[3],
                    "name": data[4],
                },
                dont_filter=True
            )

    def parse(self, response, **kwargs):
        id = kwargs['id']
        if response.status == 301:
            update = f'update {db.asset_table} set status="502" where Id={id}'
            self.cursor.execute(update)
            self.con.commit()
            self.logger.info(f'{db.asset_table} 502 Not Found...')
            self.con.commit()
            return None

        file_name = kwargs['file_name']
        if response.url.endswith(".exe"):
            file_name = response.url.split("/")[-1]
        if not file_name:
            file_name = response.headers['content-disposition'].decode("utf-8").split("=")[-1].strip('"')

        file_type = None
        if kwargs['main']:
            file_type = "image/product"
        elif ".zip" in file_name:
            file_type = "other"
        elif file_name.split(".")[-1].lower() in ['dxf', 'dwg', 'slddrw']:
            file_type = "cad/2D"
        elif file_name.split(".")[-1].lower() in ['step', 'iges', 'igs', 'sldprt', 'ipt', 'x_t', 'eprt', '.step']:
            file_type = "cad/3D"
        elif file_name.split(".")[-1].lower() in ['cert', 'crt']:
            file_type = "document/cert"

        try:
            if 'software' in kwargs['name'].lower():
                file_type = "other"
        except:
            pass

        try:
            if not file_type:
                if 'manual' in kwargs['name'].lower():
                    file_type = "document/manual"
                elif 'spec' in kwargs['name'].lower():
                    file_type = "document/spec"
                elif 'catalog' in kwargs['name'].lower():
                    file_type = "document/catalog"
        except:
            pass

        if not file_type and '.pdf' in file_name.lower():
            file_type = "document"

        if not file_type and file_name.split(".")[-1].lower() in ['png', 'jpg']:
            file_type = "image/product"

        if not file_type:
            file_type = "other"

        sha256 = hashlib.sha256(response.body).hexdigest()

        item = dict()
        item['download_path'] = self.assets_save + str(sha256)
        item['media_type'] = response.headers['Content-Type'].decode("utf-8")
        try:
            item['length'] = response.headers['Content-Length'].decode("utf-8")
        except:
            item['length'] = response.body.__sizeof__()
        item['type'] = file_type
        item['sha256'] = sha256
        item['file_name'] = file_name.replace('%20','')
        item['status'] = "Done"

        open(item['download_path'], "wb").write(response.body)

        try:
            id = kwargs['id']

            field_list = []
            for field in item.items():
                field_list.append(f'{field[0]}="{field[1]}"')

            update = f'update {db.asset_table} set {", ".join(field_list)} where Id=%s'
            self.cursor.execute(update, id)

            self.con.commit()
            self.logger.info(f'{db.asset_table} Inserted...')
            self.con.commit()

        except Exception as e:
            self.logger.error(e)


if __name__ == '__main__':
    execute("scrapy crawl download_assest -a vendor_id=ACT-B1-002 -a start=7889169 -a end=7889664".split())
