import datetime
import hashlib
import os.path
from curl_cffi import requests
import pymysql
import scrapy
# import requests
from scrapy.cmdline import execute
from Thorlabs import db_config as db


class DownloadAssestSpider(scrapy.Spider):
    name = 'req_download_assest'
    assets_save = r'D:/Data/gaurav/Assets/'
    handle_httpstatus_list = [404]

    date = datetime.datetime.now()
    month = date.strftime('%B')

    def __init__(self, start, end, name=None, vendor_id="ACT-B1-002", **kwargs):
        super().__init__(name, **kwargs)
        if not vendor_id:
            exit(-1)
        self.VENDOR_ID = vendor_id
        self.assets_save += "\\" + vendor_id + f"{self.month}\\"
        if not os.path.exists(self.assets_save):
            os.makedirs(self.assets_save)

        self.con = pymysql.connect(host=db.db_host, user=db.db_user, password=db.db_password, db=db.db_name)
        self.cursor = self.con.cursor()
        self.start = start
        self.end = end

    def start_requests(self):
        select_query = [
            f"select id, source, file_name, is_main_image, name, type from {db.asset_table} where",
            f"vendor_id = '{self.VENDOR_ID}'",
            f"and status = 'pending'",
            f"and id between {self.start} and {self.end}"
        ]
        # print(select_query)
        self.cursor.execute(" ".join(select_query))

        for data in self.cursor.fetchall():
            if not data[1].strip():
                continue
            url = data[1]
            yield scrapy.Request(
                url='https://books.toscrape.com/',
                cb_kwargs={
                    "id": data[0],
                    "file_name": data[2],
                    "main": data[3],
                    "name": "" if not data[4] else data[4],
                    "type": "" if not data[5] else data[5],
                    "source": url,
                },
                dont_filter=True
            )

    def parse(self, response, **kwargs):
        pro_urls = kwargs['source'].replace(' ','%20')
        try:
            response = requests.get(pro_urls,impersonate="chrome110",timeout=20000)

            id = kwargs['id']

            if 'play.google.com' in response.url:
                print("invalid document url")
                update = f'update {db.asset_table} set status="invalid" where Id={id}'
                self.cursor.execute(update)
                self.con.commit()
                self.logger.info(f'{db.asset_table} Inserted...')
                self.con.commit()
                return None
            elif response.status_code == 404:
                print("404 document url")
                update = f'update {db.asset_table} set status="404" where Id={id}'
                self.cursor.execute(update)
                self.con.commit()
                self.logger.info(f'{db.asset_table} 404 Not Found...')
                self.con.commit()
                return None

            if self.VENDOR_ID == "ACT-B1-008" and ('.php' in response.url or '.asp' in response.url):
                if 'Content-Type' in response.headers and b'text/xml' in response.headers['Content-Type']:
                    pass
                elif 'Content-Disposition' not in response.headers:
                    if 'already_processed' not in kwargs:
                        kwargs['already_processed'] = True
                        yield scrapy.FormRequest.from_response(response, cb_kwargs=kwargs)
                        return None

            file_name = kwargs['file_name']
            if response.url.endswith(".exe"):
                file_name = response.url.split("/")[-1]
            if not file_name or file_name.endswith(".php") or file_name.endswith(".asp"):
                try:
                    file_name = response.headers['content-disposition'].decode("utf-8").split("=")[-1].strip('"')
                except Exception as e:
                    print(e)
                    # return None

            file_type = kwargs['type']
            if not file_type:
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

                if 'software' in kwargs['name'].lower():
                    file_type = "other"

                if not file_type:
                    if 'manual' in kwargs['name'].lower():
                        file_type = "document/manual"
                    elif 'spec' in kwargs['name'].lower():
                        file_type = "document/spec"
                    elif 'catalog' in kwargs['name'].lower():
                        file_type = "document/catalog"

                if not file_type and '.pdf' in file_name.lower():
                    file_type = "document"

                if not file_type and file_name.split(".")[-1].lower() in ['png', 'jpg']:
                    file_type = "image/product"

                if not file_type:
                    file_type = "other"

            sha256 = hashlib.sha256(response.content).hexdigest()

            if 'Content-Length' in response.headers:
                # length = response.headers['Content-Length'].decode("utf-8")
                length = response.headers['Content-Length']
            else:
                length = response.content.__sizeof__()

            if 'Content-Type' in response.headers:
                # content_type = response.headers['Content-Type'].decode("utf-8")
                content_type = response.headers['Content-Type']
                if ";" in content_type:
                    content_type = content_type.split(";")[0].strip()
            elif "PDF" in response.content:
                content_type = "application/pdf"

            item = dict()
            item['download_path'] = self.assets_save + str(sha256)
            item['media_type'] = content_type
            item['length'] = length
            item['type'] = file_type
            item['sha256'] = sha256
            item['file_name'] = file_name.replace('"', "")
            item['status'] = "Done"
            # item['source'] = kwargs['source']

            if not os.path.exists(item['download_path']):
                open(self.assets_save + str(sha256), "wb").write(response.content)
            else:
                print(sha256, "already exsists")

            try:
                field_list = []
                for field in item.items():
                    field_list.append(f'{field[0]}="{field[1]}"')

                update = f'update {db.asset_table} set {", ".join(field_list)} where Id={id}'
                self.cursor.execute(update)

                self.con.commit()
                self.logger.info(f'{db.asset_table} {id} Inserted...')
                self.con.commit()

            except Exception as e:
                self.logger.error(e)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    execute("scrapy crawl req_download_assest -a start=855116 -a end=855116".split())
