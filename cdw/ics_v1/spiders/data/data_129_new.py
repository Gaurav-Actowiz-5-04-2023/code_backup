import re
import time

import pymysql
from scrapy.cmdline import execute
from ics_v1.items import IcsV1PricingItem , IcsV1PDPItem , IcsV1AssetItem
import hashlib
import os.path
import scrapy
import json
import ics_v1.db_config as db
from datetime import datetime
import requests
from random_user_agent.params import SoftwareName, OperatingSystem
from random_user_agent.user_agent import UserAgent
from random import choice

def get_useragent():
    l1 = [SoftwareName.CHROME.value, SoftwareName.FIREFOX.value, SoftwareName.OPERA.value]
    software_names = [choice(l1)]
    operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value,
                         OperatingSystem.SUNOS.value]
    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems,
                                   limit=1000)
    return user_agent_rotator.get_random_user_agent()


class Data2Spider(scrapy.Spider):
    name = 'data_cdw'
    VENDOR_ID = 'ACT-B3-010'
    VENDOR_NAME = 'CDW'
    # Month :-
    date = datetime.now()
    month = date.strftime('%B')
    # Page save Directory :-
    page_save = "D:/Pagesave/" + VENDOR_ID + "-" + VENDOR_NAME + f"{month}/"

    if not os.path.exists(page_save):
        os.makedirs(page_save)

    def __init__(self, name=None, start=2, end=2,**kwargs):
        super().__init__(name, **kwargs)
        # DATABASE CONNECTION
        self.con = pymysql.connect(host=db.db_host, user=db.db_user, password=db.db_password, db=db.db_name)
        self.cursor = self.con.cursor()
        self.start=start
        self.end=end

    def start_requests(self):

        select_query = [
            f"select id, product_urls, hash_key from {db.sitemap_table} where",
            f"vendor_id = '{self.VENDOR_ID}'",
            f"and status = 'pending'",
            f"and id between {self.start} and {self.end}"
        ]

        self.cursor.execute(" ".join(select_query))

        for data in self.cursor.fetchall():
            main_file_path = self.page_save + str(data[2]) + ".html"
            if os.path.exists(main_file_path):
                yield scrapy.Request(
                    url="file:///" + main_file_path,
                    cb_kwargs={
                        "id": data[0],
                        "url": data[1]
                    },
                    callback=self.pdp,
                    dont_filter=True
                )
            else:
                # pass
                yield scrapy.Request(
                    url=data[1],
                    cb_kwargs={
                        "id": data[0],
                        "url": data[1]
                    },
                    callback=self.pdp,
                    dont_filter=True
                )

    def pdp(self,response, **kwargs):

        key_value = dict()
        for i in re.findall('"Shipping.*?,', response.text):
            key_value[i.replace('"', '').split(':')[0]] = i.replace('"', '').split(':')[1][:-1]

        item = IcsV1PDPItem()

        id = kwargs['id']
        try:
            item['id'] = id
        except:
            item['id'] = ''

        pdp_url = kwargs['url']
        try:
            item['pdp_url'] = pdp_url
        except:
            item['pdp_url'] = ''

        try:
            item['vendor_id'] = 'ACT-B3-010'
        except:
            item['vendor_id'] = ''

        try:
            item['vendor_name'] = 'CDW'
        except:
            item['vendor_name'] = ''

        name = response.xpath('//div[@class="mfeo-list-item js-add-to-cart-item"]//p//span[@class="mfeo-list-name"]//text()').get()
        if name:
            item['name']  = name
        else:
            if name:
                item['name']  = response.xpath('//div[@class="sticky-header"]//div//h1//text()').get()
            else:
                item['name'] = response.xpath('//h1[@class="-bold"]//text()').get()



        category_ls = response.xpath('//ul[@class="breadcrumbs"]//li//a//span//text()').getall()
        category_ls.remove('Home')

        try:
            item['category'] = json.dumps(category_ls, ensure_ascii=False)
        except:
            item['category'] = ''

        item['mpn'] = response.xpath('//div[@class="primary-product-part-numbers"]//span[@itemprop="mpn"]//text()').get().strip()

        item['sku'] = response.xpath('//div[@class="primary-product-part-numbers"]//span[@itemprop="sku"]//text()').get().strip()

        # hash_key_n = int(hashlib.md5(bytes(str(f'{response.url}{item["sku"]}'), "utf8")).hexdigest(), 16) % (20 ** 20)
        hs_id = kwargs['url'] + item['sku'] +   item['mpn'] + item['category']
        hash_key = hashlib.sha256(hs_id.encode()).hexdigest()
        item['hash_key'] = hash_key

        # manu_json = " ".join(response.xpath('//script[contains(text(), "Manufacture")]//text()').getall()).strip()
        # json_dict = re.findall("{.*}",manu_json)
        # try:
        #     manufacture_name = json.loads(json_dict[0])['ManufactureName']
        #     if manufacture_name:
        #         item['manufacturer'] = manufacture_name
        #     # manufacture_name = response.xpath('//div[@class="panel-row"]//span[contains(text(),"Manufacturer")]/following-sibling::span//text()').get()
        # except:
        #     item['manufacturer'] = self.VENDOR_NAME
        attribute_file_path = self.page_save + item['sku'] + "_attribut_url" + ".html"
        if not os.path.exists(attribute_file_path):
            cookies = {
                'optimizelyEndUserId': 'oeu1700892717236r0.980095103676454',
                's_ecid': 'MCMID%7C90467126778480956810624019658723044245',
                'bluecoreNV': 'false',
                '_fbp': 'fb.1.1700892840814.1513221058',
                '_rdt_uuid': '1700892841425.5875105b-a4ba-4e90-961b-513871c5843f',
                '_lc2_fpi': '464f01cb1133--01hg2ht5hf2phe3x5e4xcd4gks',
                '_lc2_fpi_meta': '{%22w%22:1700892841519}',
                '__pdst': '5b0924bf7e054503a02611adabe421da',
                '_gcl_au': '1.1.985197267.1700892842',
                'sa-user-id': 's%253A0-b7b6a3bf-0e35-549f-489a-9d798cea60b6.Eo37ZVDGdrD%252B%252Fg1D0X7SOqX%252Fs1Zc8%252BmhO1gr61zxO0E',
                'sa-user-id-v2': 's%253At7ajvw41VJ9Imp15jOpgtsBlRzs.25X7eG2Sqkg0pM4fHXCjs46Vlj0xk0FOp%252F8TP37fFh8',
                'sa-user-id-v3': 's%253AAQAKINvjWwBnbw68NfUy4_DCbCLFXMyIABKAhIlxLki7hsidEHwYBCDms6OqBjABOgSJefOjQgT6aMT2.Lc2jgcr2TUzlSjY5qDAw0uTmytSTlbtlmAtYejPlsWk',
                'OptanonAlertBoxClosed': '2023-11-25T06:14:04.389Z',
                '__qca': 'P0-55999582-1700892842512',
                'dtm_token_sc': 'AAAGTrwAzvjI0ABSdu8dAAAAAAE',
                '_hjSessionUser_68143': 'eyJpZCI6ImY5NmI2OGNlLTJmYTItNTlmNS05YzZiLTMzYmQ4ZmE5ZTdlNiIsImNyZWF0ZWQiOjE3MDA4OTI4NDcwNzMsImV4aXN0aW5nIjp0cnVlfQ==',
                'dtm_token': 'AAAGTrwAzvjI0ABSdu8dAAAAAAE',
                'optimizelyEndUserId': 'oeu1700892717236r0.980095103676454',
                '_uetvid': 'd42fe2d08b5911eebee27fe031d46f58',
                'optimizelyEndUserId': 'oeu1700892717236r0.980095103676454',
                '_hjSessionUser_68143': 'eyJpZCI6ImY5NmI2OGNlLTJmYTItNTlmNS05YzZiLTMzYmQ4ZmE5ZTdlNiIsImNyZWF0ZWQiOjE3MDA4OTI4NDcwNzMsImV4aXN0aW5nIjp0cnVlfQ==',
                '70549A6B29AD46CF90DA19BC17972419': 'l0pw4tx4VEeGV_Ew1HfpHQqjoZO_RjQXeG1Lsg-blM-fBmzACx5O2YVXyfjWH8ljyvCyR1_94CLEJ2pVYRfnhH3pZB01',
                'A8A8F83D13EA4F8B917AA5F211762060': '07EE9408E96145A182FD3D78949AE8C9',
                'BA9AA5C91598458BA251A10B273627B6': 'A9C24774921D49AB94B150A450111737',
                'AKA_A2': 'A',
                '_abck': 'D55A26E32B51F8B590D07CF989867037~0~YAAQNe/dF72BQGSMAQAABgyWugsHFEnSDy3Y307q1vdDHcFn8nPiAtPsYT3zY7eBxrZBE/T+5OyOtCMOc9zUAMFCky6ccR1Or3OcqOI+1OZAlgGrI4E0G098mYcYwrPRZjk89+baHiTddQngjUPE5xuZKwUwaPh9s2FqjqoJtwIKK+8HWcFmgAK7KEaPdeHhAhtCgoDQ4C9r+ZVTFpn8ZPDBsdDMhY2y0LcxdVKC+oVd67jmaXXFhqvrz+ZhIHmATokeK+mB45Bk16cldZkt6aZl9+lqrB7Agg1C/HXNfJc61H90Xdvj4Ma6nVyEkHK+6+HD0vI8n6yGSl0z4dDNrFr+2QCHNkpOcYFRfmJ5vPw9Uzd0wXwmmxi8r34liIeYbGzmUmt2yPdAioucstqeLKg5VMQ5~-1~-1~-1',
                'bm_sz': 'B3EA3DB80021CAA4DE54CFC641FA7A43~YAAQNe/dF8CBQGSMAQAABgyWuhYCsj5u42mOIqrvbe0B2emJkqzwodvQ61WwrCX8EP9KUZ5jKeS1QPfPYv73qaOR4EDB8820opwgw25Acz2/weMGHcQ5DsIIUTWUUIyH02v7u8ZSZ7eN2fopRTWuGo1INuIvqPs6DlePFaVWwzSO+s7Kc3J/FMXMSkPPAtMwu0O51Uthz8Ja6VqA3DGA+157jjlF+DI/3X2GNEIU6ac5iRWISK0eEzlgDNAUczTQGkGG7UKSlh90rq1YkL/TW5kCPXQlMoROigaUhjn7VIA=~4272177~3621190',
                's_dfa': 'cdwglobalstaging',
                'AMCVS_6B61EE6A54FA17010A4C98A7%40AdobeOrg': '1',
                'AMCV_6B61EE6A54FA17010A4C98A7%40AdobeOrg': '-1124106680%7CMCIDTS%7C19722%7CMCMID%7C90467126778480956810624019658723044245%7CMCAAMLH-1704542248%7C7%7CMCAAMB-1704542248%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1703944648s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C5.2.0',
                's_visit': '1',
                's_dl': '1',
                's_dl1': '1',
                's_dl2': '1',
                's_dl3': '1',
                's_cc': 'true',
                '265B10B0AD854F37A02410D8F39E9723': '8A6760DA-A25D-4CBF-B4FF-051E906D6B4C',
                'CartKey': '795c7ed0c84d474981f0657454a9f782',
                '_li_dcdm_c': '.cdw.com',
                'bm_mi': '538C94FE3F773AF757E88E53C8FD4118~YAAQNe/dF8GYQGSMAQAAcaiWuhZd344t5rD0ZlqWnX3W6WYuaIj9FkPFuXMv37vgrYbR6tNx1MgWUnnvE5x4J1GcIoRhOh9KQjEXlknu+RnmttwfQyvGn0fimiHM2wKoQitej6A2PzdTVfLtxbEnMrY8Z/GNPs8Rkrgj30cMVxYMS58/fKuUKGqG8OgZH3Tyi13nPyDpZuCqW82uARrargydV/em6RaEAJzzs+BIo4q+PflTTJ/vTIUhqBWAHEmu2WRLRSH9ihpS1qru26/hCx8iLqSmnmhibCOQuOlmM9c2/aKQI+OU++MqKiQ9C3W+YPZw+RPxFoUY6GK0uZC4wzN5Qguf81uQs5ZUC/E7XjQlqXSoqF1YMInWiSuOKaum3g==~1',
                'ak_bmsc': '29B504F28A680CDF29FDC873EA747186~000000000000000000000000000000~YAAQNe/dF/KZQGSMAQAAx6+Wuhal9+UuxrF84BIcKS6KE4WI/ScC8NVtTLYBMOKMuKIrdWrK4xTkkhn/11khHH1/q1/mNmVAlZt+9VVBfDl1ElsXhn3J2OiqLC38vAbPOqNyQzsoY0Q13YLVdkbu8Oamy8H07txFi1PbiJB+XCoKb40isPIEeGYICjb1h7+uBtJBsAyB0NrbF7MzAzgL2q8rTAIJbvmSc60YQEmIj6xzaYdQqtBGoby3vz7xoeT7TmQVAa9gyNMaD13Q21vH4++FMx6PHhZyRwQGjzKde2dujFMYIARhuMU6rLuSoua/yDQ/ydplfibNzrwe34AVmXy8m4rF/g5MrJCAZDCp/QX5LTmUVVljmcQoUyz+wCqul9lOyJ36eHh9sEy3//4kfWuHlbDDziEYzPERY3F1wdrXRz8CKEfwUEg3UY8vbMiLbs61OzKoGgU1EV43pNjkwNAAm/eM7SSk35HafqB39JJJIbANl1Ckwy+VB5SRrldjKloU12svScX/ePCBVj9SnC6WYzjrPdabMgWER7gAfgTFnWHo/8/+pZH+p7H2LXWhXlKtNyziioLzSTk7deIIP1InsN0=',
                '_hjIncludedInSessionSample_68143': '1',
                '_hjAbsoluteSessionInProgress': '1',
                '_hjSession_68143': 'eyJpZCI6ImJmMWEzYjY2LTFjYTMtNDIxNi04MTkzLTBkMTQ3ZTQ1MjM1ZiIsImMiOjE3MDM5Mzc0OTg5MjEsInMiOjEsInIiOjEsInNiIjowfQ==',
                'QSI_HistorySession': '',
                '4112525968F44D5C99DF0BDE0C235561': '_5117410,5476920,7612224,7449048,6390664,7448810,1033626,6333990,091361,023717,022935,5136151',
                'gpv_pn': 'Poly%20-%20USB-C%20adapter%20-%20USB%20to%2024%20pin%20USB-C',
                'cto_bundle': 'r7HcMl9MOG1DUndESlQ5NE05eUFqenNFWm4wR053bFNYNnZuVGtjakUyMGpxY3dEUTFZZmEwbGNiZDRQVjZwVjk1RkpFZk9JejBkNnU3VFF1Qnh4WDVWS3NlZEIlMkJ5cnglMkJoNXBpV21ZbFV6dFA5TEJzcmlwZlI1ZTVXRWp4dWdxSGhFTFRYayUyRkhNWkV6RlVJOTlNRXc3c0Z6Q2clM0QlM0Q',
                'cto_bundle': 'r7HcMl9MOG1DUndESlQ5NE05eUFqenNFWm4wR053bFNYNnZuVGtjakUyMGpxY3dEUTFZZmEwbGNiZDRQVjZwVjk1RkpFZk9JejBkNnU3VFF1Qnh4WDVWS3NlZEIlMkJ5cnglMkJoNXBpV21ZbFV6dFA5TEJzcmlwZlI1ZTVXRWp4dWdxSGhFTFRYayUyRkhNWkV6RlVJOTlNRXc3c0Z6Q2clM0QlM0Q',
                'SC_LINKS': '%5B%5BB%5D%5D',
                's_sq': '%5B%5BB%5D%5D',
                '_uetsid': 'a4e39510a70a11ee913e31845f92c3c5',
                'needlepin': 'N190d1700892724894429b3002112cd81916503781944c5d281944c82200315100081944c68022f0000000141381944c5e70000000000000cinvTargeted214138191ed3003afb',
                's_ppvl': '5117410%2C70%2C100%2C3574%2C1600%2C347%2C1280%2C720%2C1.2%2CL',
                's_ptc': '%5B%5BB%5D%5D',
                'OptanonConsent': 'isGpcEnabled=0&datestamp=Sat+Dec+30+2023+17%3A38%3A10+GMT%2B0530+(India+Standard+Time)&version=202310.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=99489b3e-7dc3-40ee-b7d4-4cee096d456e&interactionCount=2&landingPath=NotLandingPage&groups=C0003%3A1%2CC0004%3A1%2CC0001%3A1%2CC0002%3A1&AwaitingReconsent=false&geolocation=US%3BIL',
                'utag_main': 'v_id:018c051b3c6f00142b9f57d259ee0506f0031067007e8$_sn:21$_se:18$_ss:0$_st:1703939889740$random_number:27$vapi_domain:cdw.com$dc_visit:21$ses_id:1703937447209%3Bexp-session$_pn:6%3Bexp-session$dcsyncran:1%3Bexp-session$dc_event:18%3Bexp-session$dc_region:us-east-1%3Bexp-session',
                'mp_cdw_mixpanel': '%7B%22distinct_id%22%3A%20%2218b653590d7930-026ad7da281732-26031151-e1000-18b653590d87df%22%2C%22bc_persist_updated%22%3A%201701276390443%7D',
                'bc_invalidateUrlCache_targeting': '1703938090718',
                'RT': '"z=1&dm=cdw.com&si=1c5aa96f-da7a-4462-935b-8f8aa28065b7&ss=lqs0cxve&sl=8&tt=21gg&bcn=%2F%2F173bf106.akstat.io%2F&ld=dvqm"',
                's_ppv': '5117410%2C100%2C99%2C2632%2C1600%2C347%2C1280%2C720%2C1.2%2CL',
                'bm_sv': '383DEA515AE69624A1FC82D894050013~YAAQNe/dF88aQmSMAQAAEumfuhbqRZXJ89Yw8hKrx6HV94r9vHkJWzCl8aTDF4RGIgEyuJIj/GiMVjVQwrP5WIhC10kW9sggIyrGc14g8PtmuRJR+xg0cVzVlwf7fgMAnY7kjsGc5tG+/L2b5k5pL6cGhwSPBFVRq7rI/XyxvislwRSd/fsaHbfFgHWdsSyWmVrGzHDtcHGeKlpLGLpghmuD+d1rNMh4/nq/3g4eK2c5VFMlZPJFAx5EHEFvUw==~1',
            }

            headers = {
                'authority': 'www.cdw.com',
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                # 'cookie': 'optimizelyEndUserId=oeu1700892717236r0.980095103676454; s_ecid=MCMID%7C90467126778480956810624019658723044245; bluecoreNV=false; _fbp=fb.1.1700892840814.1513221058; _rdt_uuid=1700892841425.5875105b-a4ba-4e90-961b-513871c5843f; _lc2_fpi=464f01cb1133--01hg2ht5hf2phe3x5e4xcd4gks; _lc2_fpi_meta={%22w%22:1700892841519}; __pdst=5b0924bf7e054503a02611adabe421da; _gcl_au=1.1.985197267.1700892842; sa-user-id=s%253A0-b7b6a3bf-0e35-549f-489a-9d798cea60b6.Eo37ZVDGdrD%252B%252Fg1D0X7SOqX%252Fs1Zc8%252BmhO1gr61zxO0E; sa-user-id-v2=s%253At7ajvw41VJ9Imp15jOpgtsBlRzs.25X7eG2Sqkg0pM4fHXCjs46Vlj0xk0FOp%252F8TP37fFh8; sa-user-id-v3=s%253AAQAKINvjWwBnbw68NfUy4_DCbCLFXMyIABKAhIlxLki7hsidEHwYBCDms6OqBjABOgSJefOjQgT6aMT2.Lc2jgcr2TUzlSjY5qDAw0uTmytSTlbtlmAtYejPlsWk; OptanonAlertBoxClosed=2023-11-25T06:14:04.389Z; __qca=P0-55999582-1700892842512; dtm_token_sc=AAAGTrwAzvjI0ABSdu8dAAAAAAE; _hjSessionUser_68143=eyJpZCI6ImY5NmI2OGNlLTJmYTItNTlmNS05YzZiLTMzYmQ4ZmE5ZTdlNiIsImNyZWF0ZWQiOjE3MDA4OTI4NDcwNzMsImV4aXN0aW5nIjp0cnVlfQ==; dtm_token=AAAGTrwAzvjI0ABSdu8dAAAAAAE; optimizelyEndUserId=oeu1700892717236r0.980095103676454; _uetvid=d42fe2d08b5911eebee27fe031d46f58; optimizelyEndUserId=oeu1700892717236r0.980095103676454; _hjSessionUser_68143=eyJpZCI6ImY5NmI2OGNlLTJmYTItNTlmNS05YzZiLTMzYmQ4ZmE5ZTdlNiIsImNyZWF0ZWQiOjE3MDA4OTI4NDcwNzMsImV4aXN0aW5nIjp0cnVlfQ==; 70549A6B29AD46CF90DA19BC17972419=l0pw4tx4VEeGV_Ew1HfpHQqjoZO_RjQXeG1Lsg-blM-fBmzACx5O2YVXyfjWH8ljyvCyR1_94CLEJ2pVYRfnhH3pZB01; A8A8F83D13EA4F8B917AA5F211762060=07EE9408E96145A182FD3D78949AE8C9; BA9AA5C91598458BA251A10B273627B6=A9C24774921D49AB94B150A450111737; AKA_A2=A; _abck=D55A26E32B51F8B590D07CF989867037~0~YAAQNe/dF72BQGSMAQAABgyWugsHFEnSDy3Y307q1vdDHcFn8nPiAtPsYT3zY7eBxrZBE/T+5OyOtCMOc9zUAMFCky6ccR1Or3OcqOI+1OZAlgGrI4E0G098mYcYwrPRZjk89+baHiTddQngjUPE5xuZKwUwaPh9s2FqjqoJtwIKK+8HWcFmgAK7KEaPdeHhAhtCgoDQ4C9r+ZVTFpn8ZPDBsdDMhY2y0LcxdVKC+oVd67jmaXXFhqvrz+ZhIHmATokeK+mB45Bk16cldZkt6aZl9+lqrB7Agg1C/HXNfJc61H90Xdvj4Ma6nVyEkHK+6+HD0vI8n6yGSl0z4dDNrFr+2QCHNkpOcYFRfmJ5vPw9Uzd0wXwmmxi8r34liIeYbGzmUmt2yPdAioucstqeLKg5VMQ5~-1~-1~-1; bm_sz=B3EA3DB80021CAA4DE54CFC641FA7A43~YAAQNe/dF8CBQGSMAQAABgyWuhYCsj5u42mOIqrvbe0B2emJkqzwodvQ61WwrCX8EP9KUZ5jKeS1QPfPYv73qaOR4EDB8820opwgw25Acz2/weMGHcQ5DsIIUTWUUIyH02v7u8ZSZ7eN2fopRTWuGo1INuIvqPs6DlePFaVWwzSO+s7Kc3J/FMXMSkPPAtMwu0O51Uthz8Ja6VqA3DGA+157jjlF+DI/3X2GNEIU6ac5iRWISK0eEzlgDNAUczTQGkGG7UKSlh90rq1YkL/TW5kCPXQlMoROigaUhjn7VIA=~4272177~3621190; s_dfa=cdwglobalstaging; AMCVS_6B61EE6A54FA17010A4C98A7%40AdobeOrg=1; AMCV_6B61EE6A54FA17010A4C98A7%40AdobeOrg=-1124106680%7CMCIDTS%7C19722%7CMCMID%7C90467126778480956810624019658723044245%7CMCAAMLH-1704542248%7C7%7CMCAAMB-1704542248%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1703944648s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C5.2.0; s_visit=1; s_dl=1; s_dl1=1; s_dl2=1; s_dl3=1; s_cc=true; 265B10B0AD854F37A02410D8F39E9723=8A6760DA-A25D-4CBF-B4FF-051E906D6B4C; CartKey=795c7ed0c84d474981f0657454a9f782; _li_dcdm_c=.cdw.com; bm_mi=538C94FE3F773AF757E88E53C8FD4118~YAAQNe/dF8GYQGSMAQAAcaiWuhZd344t5rD0ZlqWnX3W6WYuaIj9FkPFuXMv37vgrYbR6tNx1MgWUnnvE5x4J1GcIoRhOh9KQjEXlknu+RnmttwfQyvGn0fimiHM2wKoQitej6A2PzdTVfLtxbEnMrY8Z/GNPs8Rkrgj30cMVxYMS58/fKuUKGqG8OgZH3Tyi13nPyDpZuCqW82uARrargydV/em6RaEAJzzs+BIo4q+PflTTJ/vTIUhqBWAHEmu2WRLRSH9ihpS1qru26/hCx8iLqSmnmhibCOQuOlmM9c2/aKQI+OU++MqKiQ9C3W+YPZw+RPxFoUY6GK0uZC4wzN5Qguf81uQs5ZUC/E7XjQlqXSoqF1YMInWiSuOKaum3g==~1; ak_bmsc=29B504F28A680CDF29FDC873EA747186~000000000000000000000000000000~YAAQNe/dF/KZQGSMAQAAx6+Wuhal9+UuxrF84BIcKS6KE4WI/ScC8NVtTLYBMOKMuKIrdWrK4xTkkhn/11khHH1/q1/mNmVAlZt+9VVBfDl1ElsXhn3J2OiqLC38vAbPOqNyQzsoY0Q13YLVdkbu8Oamy8H07txFi1PbiJB+XCoKb40isPIEeGYICjb1h7+uBtJBsAyB0NrbF7MzAzgL2q8rTAIJbvmSc60YQEmIj6xzaYdQqtBGoby3vz7xoeT7TmQVAa9gyNMaD13Q21vH4++FMx6PHhZyRwQGjzKde2dujFMYIARhuMU6rLuSoua/yDQ/ydplfibNzrwe34AVmXy8m4rF/g5MrJCAZDCp/QX5LTmUVVljmcQoUyz+wCqul9lOyJ36eHh9sEy3//4kfWuHlbDDziEYzPERY3F1wdrXRz8CKEfwUEg3UY8vbMiLbs61OzKoGgU1EV43pNjkwNAAm/eM7SSk35HafqB39JJJIbANl1Ckwy+VB5SRrldjKloU12svScX/ePCBVj9SnC6WYzjrPdabMgWER7gAfgTFnWHo/8/+pZH+p7H2LXWhXlKtNyziioLzSTk7deIIP1InsN0=; _hjIncludedInSessionSample_68143=1; _hjAbsoluteSessionInProgress=1; _hjSession_68143=eyJpZCI6ImJmMWEzYjY2LTFjYTMtNDIxNi04MTkzLTBkMTQ3ZTQ1MjM1ZiIsImMiOjE3MDM5Mzc0OTg5MjEsInMiOjEsInIiOjEsInNiIjowfQ==; QSI_HistorySession=; 4112525968F44D5C99DF0BDE0C235561=_5117410,5476920,7612224,7449048,6390664,7448810,1033626,6333990,091361,023717,022935,5136151; gpv_pn=Poly%20-%20USB-C%20adapter%20-%20USB%20to%2024%20pin%20USB-C; cto_bundle=r7HcMl9MOG1DUndESlQ5NE05eUFqenNFWm4wR053bFNYNnZuVGtjakUyMGpxY3dEUTFZZmEwbGNiZDRQVjZwVjk1RkpFZk9JejBkNnU3VFF1Qnh4WDVWS3NlZEIlMkJ5cnglMkJoNXBpV21ZbFV6dFA5TEJzcmlwZlI1ZTVXRWp4dWdxSGhFTFRYayUyRkhNWkV6RlVJOTlNRXc3c0Z6Q2clM0QlM0Q; cto_bundle=r7HcMl9MOG1DUndESlQ5NE05eUFqenNFWm4wR053bFNYNnZuVGtjakUyMGpxY3dEUTFZZmEwbGNiZDRQVjZwVjk1RkpFZk9JejBkNnU3VFF1Qnh4WDVWS3NlZEIlMkJ5cnglMkJoNXBpV21ZbFV6dFA5TEJzcmlwZlI1ZTVXRWp4dWdxSGhFTFRYayUyRkhNWkV6RlVJOTlNRXc3c0Z6Q2clM0QlM0Q; SC_LINKS=%5B%5BB%5D%5D; s_sq=%5B%5BB%5D%5D; _uetsid=a4e39510a70a11ee913e31845f92c3c5; needlepin=N190d1700892724894429b3002112cd81916503781944c5d281944c82200315100081944c68022f0000000141381944c5e70000000000000cinvTargeted214138191ed3003afb; s_ppvl=5117410%2C70%2C100%2C3574%2C1600%2C347%2C1280%2C720%2C1.2%2CL; s_ptc=%5B%5BB%5D%5D; OptanonConsent=isGpcEnabled=0&datestamp=Sat+Dec+30+2023+17%3A38%3A10+GMT%2B0530+(India+Standard+Time)&version=202310.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=99489b3e-7dc3-40ee-b7d4-4cee096d456e&interactionCount=2&landingPath=NotLandingPage&groups=C0003%3A1%2CC0004%3A1%2CC0001%3A1%2CC0002%3A1&AwaitingReconsent=false&geolocation=US%3BIL; utag_main=v_id:018c051b3c6f00142b9f57d259ee0506f0031067007e8$_sn:21$_se:18$_ss:0$_st:1703939889740$random_number:27$vapi_domain:cdw.com$dc_visit:21$ses_id:1703937447209%3Bexp-session$_pn:6%3Bexp-session$dcsyncran:1%3Bexp-session$dc_event:18%3Bexp-session$dc_region:us-east-1%3Bexp-session; mp_cdw_mixpanel=%7B%22distinct_id%22%3A%20%2218b653590d7930-026ad7da281732-26031151-e1000-18b653590d87df%22%2C%22bc_persist_updated%22%3A%201701276390443%7D; bc_invalidateUrlCache_targeting=1703938090718; RT="z=1&dm=cdw.com&si=1c5aa96f-da7a-4462-935b-8f8aa28065b7&ss=lqs0cxve&sl=8&tt=21gg&bcn=%2F%2F173bf106.akstat.io%2F&ld=dvqm"; s_ppv=5117410%2C100%2C99%2C2632%2C1600%2C347%2C1280%2C720%2C1.2%2CL; bm_sv=383DEA515AE69624A1FC82D894050013~YAAQNe/dF88aQmSMAQAAEumfuhbqRZXJ89Yw8hKrx6HV94r9vHkJWzCl8aTDF4RGIgEyuJIj/GiMVjVQwrP5WIhC10kW9sggIyrGc14g8PtmuRJR+xg0cVzVlwf7fgMAnY7kjsGc5tG+/L2b5k5pL6cGhwSPBFVRq7rI/XyxvislwRSd/fsaHbfFgHWdsSyWmVrGzHDtcHGeKlpLGLpghmuD+d1rNMh4/nq/3g4eK2c5VFMlZPJFAx5EHEFvUw==~1',
                'referer': f'{kwargs["url"]}',
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': get_useragent(),
                'x-requested-with': 'XMLHttpRequest',
            }

            params = {
                '_': '1703938089206',
            }

            Response = requests.get(
                f'https://www.cdw.com/api/product/1/data/technicalspecifications/{item["sku"]}',
                params=params,
                cookies=cookies,
                headers=headers,
            )

            manufacture_json = json.loads(Response.text)

        else:
            manufacture_json = json.loads(open(attribute_file_path, 'r').read())

        try:
            for i in manufacture_json['AttributeGroups'][0]['Attributes']:
                if i['key'] == 'Manufacturer':
                    item['manufacturer'] = i['value']
        except:
            try:
                for i in manufacture_json['AttributeGroups'][0]['Attributes']:
                    if i['Key'] == 'Manufacturer':
                        item['manufacturer'] = i['Value']
            except:
                item['manufacturer'] = self.VENDOR_NAME

        if 'manufacturer' not in item:
            item['manufacturer'] = self.VENDOR_NAME

        if "message availability in-stock" in response.text:
            item['in_stock'] = True
        else:
            item['in_stock'] = False

        available_to_checkout = response.xpath('//div[@class="addtocart-container"]//button[@type="submit"]//text()').get()
        if available_to_checkout == None:
                item['available_to_checkout'] = False
        else:
                item['available_to_checkout'] = True

        open(self.page_save + item['sku'] + ".html", "wb").write(response.body)

        update = f'update {db.sitemap_table} set hash_key={item["sku"]} where Id=%s'
        self.cursor.execute(update, id)

        if not os.path.exists(self.page_save + item['sku'] + "_estimated_lead_time_url" + ".html"):

            estimated_lead_time_url = 'https://www.cdw.com/api/product/1/data/getshippingmessage'

            payload = f"ProductsInfo%5B0%5D%5BProductCode%5D={item['sku']}&ProductsInfo%5B0%5D%5BDropShip%5D=2&ProductsInfo%5B0%5D%5BProductClass%5D=RO&ProductsInfo%5B0%5D%5BSource%5D=&ProductsInfo%5B0%5D%5BQuantity%5D=&ToZipCode="
            headers = {
                'authority': 'www.cdw.com',
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'cookie': 'optimizelyEndUserId=oeu1685001507617r0.352993028636466; _gcl_au=1.1.581762258.1685001721; bluecoreNV=false; _rdt_uuid=1685001721892.07cc02a6-06ca-4a7d-b81b-71bc40fe2330; _lc2_fpi=464f01cb1133--01h18yvp2f7hbcvs74y3y6s2sh; _fbp=fb.1.1685001722393.1590691643; __qca=P0-1840470368-1685001722354; OptanonAlertBoxClosed=2023-05-25T09:42:07.412Z; rr_rcs=eF5j4cotK8lM4TMyMNU11DVkKU32MDA0sLQwN0vSTUoFEibGqRa6lpZGSbrmxmZGhiYWialJaSkAe84OBw; A8A8F83D13EA4F8B917AA5F211762060=88723E4C891C469C9BC9719F786DA34A; BA9AA5C91598458BA251A10B273627B6=85FBC097543F4D5D8BDF6F7602421BFC; dtCookie=v_4_srv_12_sn_006F887D659D413DC2F9EF6F9135D170_perc_100000_ol_0_mul_1_app-3A9daca7aae537f807_1_rcs-3Acss_0; AKA_A2=A; _abck=9520A65921B493C2FBE705085A79EF7B~0~YAAQzuvfrVA9Fm2IAQAAArfkdQkZ9/90+ZkORY0jY09FMtqaHvEJzaanK9oC6YkMhiFl+HXAfh3a4FXVm4ktN2JCDFvpBcOIVW/y7Rzs7yid3244/4OlIPuHCXGEaS4xy0Ti7VpKBAavxAmzbQZw9dXm9KRE6NjlnSfdlLq3Cg9gjY8Lwbd+vd53Ll2YZ+WWZiYI2ef8fiPajKVV1V8rEWPayI7rVo7DwjaEs0B+T3bEs41/Tz6znZ27dbpyZL+5kuCjgQxFCZK1El/UHCAAiUKf44DF6E85JcWnyKaweYDw10OnO6ZAcxgHNxvj07YP26bk0kJ1TEWxO8ZcvcEQzklAEfmIy2KxrbD/1gUYEgqWF4jFFqvNKXlFUhZDO6+WXZJttLdZ1hbcc81r1+ZoDFWUntpG~-1~-1~-1; bm_sz=7C432CDBA116F09AB68B4EE0054AF2F8~YAAQzuvfrVM9Fm2IAQAAArfkdRNPCfeRDrhJJi1Ar4MJ0oKPdI7qW68cxMbuq1hJVCjcN3DSemYWpU++F6bvahKaXrmunY0JyM4aW/1mMSjYALwExR/vIndl6FBI1T1E6e6yfR9YvKLkOD7rnVOGhcEilSpiwq9V5HAptpI6wYAKhmnN7cSZg3hUhxSDgxpolWd+XXfMWei9Qt93uvNEcKNEvE90QEehOwAl4ZCB5Mqhzg5AqnIaRtOBLsjRagM+tNGiWlJilyFFLYFzWq/hKE6m7PEdqhJ2QcSrk8xhqns=~4407873~4272434; rxVisitor=16856051091577GAJNQVG46GS9DBQHEC9BU4CMC3BNOPO; dtSa=-; newVisitor=true; ak_bmsc=2325B393918CA06DE97A8BAC2D3BC5EB~000000000000000000000000000000~YAAQzuvfrZA+Fm2IAQAAHtrkdRPpc1g5M8t+2GVvISjmSazyxCn59Q7L+qC/ZlkytSIJf6RKqIEtX2237oZwnq9aZUmOEPDfv4cOkb/YOT4SlEvWumWEcCzjzmkv2vL35o2M7Z6gTRfo+p+59A9D97Z7L6hyDQIQKR0SJ5WbKk9Z5ovzjwVO805Nz5gH7KQijY4u+lSbkvaM+dIoOSeQSe0HB9yWtdZcLVRR1xXptYSST1s2qg3mPw7DLUDoUUvL7adp18AZ5vn81xndQp3UEm565/vNdkA1+4ooPnlVkrUUyOIg6jCOyr215Ua/d56v1uhd+hCGh5D/HJ92tjIes2YLrbQN4BzHncXEvksDVJKx6hO8CQvxNZjrEM4GPTVmEHnFW4mKU5pasnilzVAZQMqtKkIgyj8KQbiZS4HrdAjJOgfAzQEZS9zB/lS/fmVvjLz4fQN+t2XAR0XaD6ZSxs9Jdm8BNM8j6SaYrC25rczZj89qqOr7uQ==; 265B10B0AD854F37A02410D8F39E9723=A4D6C57D-2D33-4E02-924D-7149DD11E015; CartKey=88b9cab9fd58445fb07faab66baf9428; AMCVS_6B61EE6A54FA17010A4C98A7%40AdobeOrg=1; s_visit=1; s_dl=1; s_dl1=1; s_dl2=1; s_dl3=1; s_cc=true; _li_dcdm_c=.cdw.com; __pdst=fad83dfd6e0149eab10fcb8b541100c0; ln_or=eyIzMTI3IjoiZCJ9; 70549A6B29AD46CF90DA19BC17972419=n9zwH4unV6g1osuTXxiTpF-j6qzLrAPaIRBi3d6Fs5mA4vO-yPXDUATAkuhS7W3QW40SD-Zq_V2bG4va0mdMABGKzLE1; QSI_HistorySession=; cto_bundle=gS5MFF9sMCUyQjdjZlF2Y1Z4NFo4empsUGhWZVdFWSUyRk9MTiUyRjR1eDdqSGpHRndVcVVlWiUyQmtmaFE1YkdnNkp3TUpCTW1ZNFl2Ykt6OHh6SkFHdVFSNzNvVk9lS1RzaCUyRmJsQkk5NUJZWkJvT0V4Y05FdGxWTyUyQkxmZFM4QzhPQ0xKaEFpc0Rtd0JmS0Znak5wSmRHeFVweGticlRtcUElM0QlM0Q; SC_LINKS=%5B%5BB%5D%5D; s_sq=%5B%5BB%5D%5D; _uetsid=55801c70004f11eea86fb7f830d3c4bf; _uetvid=6df960f0fad211eda0653d8cf158d25e; gpv_pn=HamiltonBuhl%20Edison%20Educational%20Robot%20Kit%20-%20Set%20of%2020%20-%20STEAM%20Education; 4112525968F44D5C99DF0BDE0C235561=_5136151,6745331,7360426,717516,6738755,559124,2565617; needlepin=N190d168500152592144279001c2ed81823d53e8182d0b048182d15eb0021e0008182d150227100000000118182d0b4900000000000005invT20138182987303342; dtPC=12$207918906_474h1vKQATFLKLCFPVQAPIGETVKAMDHTSACOCC-0e0; dtLatC=3; rxvt=1685609718936|1685607455274; s_dfa=cdwglobalstaging; RT="z=1&dm=cdw.com&si=440164a2-b63c-46f4-8d7c-efcbaa7839d4&ss=lictr9gq&sl=8&tt=1h6t&bcn=%2F%2F684d0d4c.akstat.io%2F"; s_ppvl=5136151%2C47%2C60%2C1818%2C1920%2C510%2C1920%2C1080%2C1%2CL; s_ptc=%5B%5BB%5D%5D; AMCV_6B61EE6A54FA17010A4C98A7%40AdobeOrg=1585540135%7CMCMID%7C40407086489455280136413274095147520423%7CMCOPTOUT-1685615121s%7CNONE%7CvVersion%7C4.4.0; bm_sv=86529417F8189715580FBA4774E4ECA1~YAAQ5+/IFzr8ZG6IAQAAfbQPdhMfzcqSWwMz9yvpBYD8YDqKHg2lcn7/zKyRsPXteKTNGrdA2cAzAmRaLG4TomuuvSrN/3Cetg0UY1GYKxetyHvw+CbNu0mYdBOqO7KtHtYgJGwVHChYbw21Ww/Wy4HPwl7uAKwm3GUG2fvHiBEkdTPLoBWL//5yUmJmdLNpotVmkUVOqRSt/qTQRcsRDU2051ukMVcgMPEycYO/YNBGqZLgDs2CR9a952yBUw==~1; s_ppv=5136151%2C23%2C23%2C564%2C1920%2C510%2C1920%2C1080%2C1%2CL; mp_cdw_mixpanel=%7B%22distinct_id%22%3A%20%2218851ead4b95d9-01f9259ca068d8-26031a51-1fa400-18851ead4bac22%22%2C%22bc_persist_updated%22%3A%201685001524412%7D; utag_main=v_id:018851ea957a0000de717a3bd91a0506f001406700bd0$_sn:13$_se:20$_ss:0$_st:1685609720076$random_number:27$vapi_domain:cdw.com$dc_visit:13$ses_id:1685605110432%3Bexp-session$_pn:6%3Bexp-session$dcsyncran:1%3Bexp-session$dc_event:20%3Bexp-session$dc_region:ap-east-1%3Bexp-session; bc_invalidateUrlCache_targeting=1685607922195; OptanonConsent=isGpcEnabled=0&datestamp=Thu+Jun+01+2023+13%3A55%3A22+GMT%2B0530+(India+Standard+Time)&version=202301.2.0&isIABGlobal=false&hosts=&consentId=fccd4fdb-b668-4e30-9daf-4f20c0f0477a&interactionCount=3&landingPath=NotLandingPage&groups=C0003%3A1%2CC0004%3A1%2CC0001%3A1%2CC0002%3A1&AwaitingReconsent=false&geolocation=SG%3B; _abck=9520A65921B493C2FBE705085A79EF7B~-1~YAAQ5+/IF/AqZW6IAQAAuKUSdgmtmVl3FFOGdgc3xxQq6c6ivj/NCayngCwmwjaTJu/O4ILeS1prnhBvwpGkA+8PwTZDh1X46rTw2rC+NDiAijysdcJlr18dUpotAiifPPW5DQuFYZ0v19JGyTOuJRCANr3R6KaH2FOJHQ8aHNdfCHjOBRzLGcXlSbAc3Mk1Md0sRl64ZBJ305N1aRTa9YMs8iVdBdjaRJm4qu2PzhAzvwXwrCZ2IsjS9A/5aqAut56V5CkkC7uXrvfelDXRV1kHuqRGAxPRms/im9JDRtMDB7DBvirZEB8AcJOO1Z+5jUdrnHGUtF5K6wrCsE7WstU7iFXgJnYDcG+IvUdeq9/A3LLYXvIbZYR0X9vK80VHOt0tdx3/C3VHApNXeG5kt0gOsrPV~0~-1~-1; bm_sv=86529417F8189715580FBA4774E4ECA1~YAAQ5+/IF/EqZW6IAQAAuKUSdhN7T2bSG0TzoN27y5FI15/9j7VkkNFinuHcMHlRTFT89SQmlMaLEEICTW4CrCqoEYMUeD8vXfSjfdma9BtvBv4vZLM/lExNnn+rgMii5qqzx4UWNnvv4wgHWW9EBJyxP9X6lPrXYvFm5KeyUUhJ1ffulFMM2r5bThrp51QrekAajcdTFkk1k3ZIvYDLT6lcFw9wrxsrEyNj/OdhNicXPrJ3T4dViap07qPz4w==~1',
                'origin': 'https://www.cdw.com',
                'referer': 'https://www.cdw.com/product/hamiltonbuhl-edison-educational-robot-kit-set-of-20-steam-education/5136151?pfm=srh',
                'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': get_useragent(),
                'x-requested-with': 'XMLHttpRequest'
            }

            response_1 = requests.request("POST", estimated_lead_time_url, headers=headers, data=payload)

            open(self.page_save + item['sku'] + "_estimated_lead_time_url" + ".html", "w").write(response_1.text)
            data1 = json.loads(response_1.text)
        else:

            response_1 = open(self.page_save + item['sku'] + "_estimated_lead_time_url" + ".html", "r").read()
            data1 = json.loads(response_1)


        # if data1:
        #     estimated_lead_time_result = []
        #     for iii in data1['ProductShippingMessage']:
        #         estimated_lead_time = iii['Shipsinshippingmessage']
        #         if estimated_lead_time == '':
        #             if "requestQuote" in response.text:
        #                 item['estimated_lead_time'] = ''
        #             else:
        #                 estimated_lead_time = response.xpath('//input[@name="CartItems[0].ProductInventory.ShippingStatusMessage"]//@value').get().strip()
        #                 if estimated_lead_time:
        #                     if 'today' in estimated_lead_time:
        #                         estimated_lead_time_result_1 = {"min_qty": 1,
        #                                                         "time_to_arrive": {"raw_value": f"{estimated_lead_time}"}}
        #                     else:
        #                         estimated_lead_time_result_1 = {"min_qty":1,"time_to_stock": {"raw_value": f"{estimated_lead_time}"}}
        #                     estimated_lead_time_result.append(estimated_lead_time_result_1)
        #                     # estimated_lead_time_result_final_1 = str(estimated_lead_time_result)
        #                     estimated_lead_time_result_final = json.dumps(estimated_lead_time_result,ensure_ascii=False)
        #                     item['estimated_lead_time'] = estimated_lead_time_result_final
        #                 else:
        #                     item['estimated_lead_time'] = None
        #         else:
        #             if estimated_lead_time:
        #                 if 'today' in estimated_lead_time:
        #                     estimated_lead_time_result_1 = {"min_qty": 1,
        #                                                     "time_to_arrive": {"raw_value": f"{estimated_lead_time}"}}
        #                 else:
        #                     estimated_lead_time_result_1 = {"min_qty": 1,
        #                                                     "time_to_stock": {"raw_value": f"{estimated_lead_time}"}}
        #                 estimated_lead_time_result.append(estimated_lead_time_result_1)
        #                 # estimated_lead_time_result_final_1 = str(estimated_lead_time_result)
        #                 estimated_lead_time_result_final = json.dumps(estimated_lead_time_result, ensure_ascii=False)
        #                 item['estimated_lead_time'] = estimated_lead_time_result_final
        #             else:
        #                 item['estimated_lead_time'] = None

        if 'This item was discontinued' not in response.text:
            if data1:
                # Extracting lead_time :-
                estimated_lead_time = list()

                # if data and False if data["ProductShippingMessage"] == [] else data["ProductShippingMessage"][0]["DropshipEdcShouldCallUps"]==True :
                if data1 and False if data1["ProductShippingMessage"] == [] else True:
                    estimated_lead_time_text_list = list()
                    estimated_lead_time_result = list()
                    con = False
                    for iii in data1['ProductShippingMessage']:
                        for key in iii:
                            if key == 'Arrival':
                                for i in data1['ProductShippingMessage'][0][key]:
                                    if data1['ProductShippingMessage'][0][key][i] != None:
                                        estimated_lead_time_text_list.append(
                                            data1['ProductShippingMessage'][0][key][i].strip())
                                        con = True
                            if key == 'Destination' or key == 'Urgency':
                                if con:
                                    for i in data1['ProductShippingMessage'][0][key]:
                                        if data1['ProductShippingMessage'][0][key][i] != None:
                                            try:
                                                if i == 'UtcDifference':
                                                    if data1['ProductShippingMessage'][0][key]['UtcDifference'] != None:
                                                        cutoffhours = int(
                                                            data1['ProductShippingMessage'][0]['Urgency']['CutoffHour'])
                                                        setting_time = cutoffhours - int(
                                                            key_value['ShippingCutoffHour'])
                                                        total_hours = int(
                                                            key_value['ShippingHoursLeft'].split(' ')[1]) + setting_time
                                                        within_time_list = key_value['ShippingHoursLeft'].split(' ')
                                                        within_time_list[1] = str(total_hours)
                                                        estimated_lead_time_text_list.append(" ".join(within_time_list))
                                                        break
                                            except Exception as e:
                                                print(e)
                                            estimated_lead_time_text_list.append(
                                                data1['ProductShippingMessage'][0][key][i].strip())

                    if estimated_lead_time_text_list:
                        estimated_lead_time_str = " ".join(estimated_lead_time_text_list)
                        if 'today' in estimated_lead_time:
                            estimated_lead_time_result_1 = {"min_qty": 1,
                                                            "time_to_arrive": {
                                                                "raw_value": f"{estimated_lead_time_str}"}}
                        else:
                            estimated_lead_time_result_1 = {"min_qty": 1,
                                                            "time_to_stock": {
                                                                "raw_value": f"{estimated_lead_time_str}"}}
                        estimated_lead_time_result.append(estimated_lead_time_result_1)
                        # estimated_lead_time_result_final_1 = str(estimated_lead_time_result)
                        estimated_lead_time_result_final = json.dumps(estimated_lead_time_result, ensure_ascii=False)
                        estimated_lead_time = estimated_lead_time_result_final

                    if not estimated_lead_time_result:
                        for iii in data1['ProductShippingMessage']:
                            estimated_lead_time = iii['Shipsinshippingmessage']
                            if estimated_lead_time == '':
                                if "requestQuote" in response.text:
                                    estimated_lead_time = ''
                                else:
                                    estimated_lead_time = response.xpath(
                                        '//input[@name="CartItems[0].ProductInventory.ShippingStatusMessage"]//@value').get().strip()
                                    if estimated_lead_time:
                                        if 'today' in estimated_lead_time:
                                            estimated_lead_time_result_1 = {"min_qty": 1,
                                                                            "time_to_arrive": {
                                                                                "raw_value": f"{estimated_lead_time}"}}
                                        else:
                                            estimated_lead_time_result_1 = {"min_qty": 1,
                                                                            "time_to_stock": {
                                                                                "raw_value": f"{estimated_lead_time}"}}
                                        estimated_lead_time_result.append(estimated_lead_time_result_1)
                                        # estimated_lead_time_result_final_1 = str(estimated_lead_time_result)
                                        estimated_lead_time_result_final = json.dumps(estimated_lead_time_result,
                                                                                      ensure_ascii=False)
                                        estimated_lead_time = estimated_lead_time_result_final
                                    else:
                                        estimated_lead_time = None
                            else:
                                if estimated_lead_time:
                                    if 'today' in estimated_lead_time:
                                        estimated_lead_time_result_1 = {"min_qty": 1,
                                                                        "time_to_arrive": {
                                                                            "raw_value": f"{estimated_lead_time}"}}
                                    else:
                                        estimated_lead_time_result_1 = {"min_qty": 1,
                                                                        "time_to_stock": {
                                                                            "raw_value": f"{estimated_lead_time}"}}
                                    estimated_lead_time_result.append(estimated_lead_time_result_1)
                                    # estimated_lead_time_result_final_1 = str(estimated_lead_time_result)
                                    estimated_lead_time_result_final = json.dumps(estimated_lead_time_result,
                                                                                  ensure_ascii=False)
                                    estimated_lead_time = estimated_lead_time_result_final
                                else:
                                    estimated_lead_time = None

                # appends lead_time to item dictionary :-
                item['estimated_lead_time'] = json.dumps(estimated_lead_time) if not isinstance(estimated_lead_time, str) else estimated_lead_time

            else:
                item['estimated_lead_time'] = None

            if item['estimated_lead_time'] == []:
                item['estimated_lead_time'] = None
        else:
            item['status'] = 'discontinued'

        description = response.xpath('//div[@itemprop="description"]//text()').getall()
        description = ' '.join(description)
        if description:
            item['description'] = re.sub("\s+"," ",description).strip()
        else:
            item['description'] = None

        if item['description'] == None:
            item['description_html'] = None
        else:
            description_html = response.xpath('//div[@class="market-text"]').getall()
            description_html = ' '.join(description_html)
            item['description_html'] = re.sub("\s+"," ",description_html).strip()

        f_ = []

        f_text = response.xpath('//div[@class="quick-tech-spec-row"]//div//ul//li//text()').getall()
        f_group = response.xpath('//div[@class="main-features"]//div[@class="title"]//text()').get()

        for k in f_text:
            feature = dict()
            feature['text'] = re.sub("\s+"," ",k.strip()).strip()
            feature['group'] = f_group if f_group else 'Quick Tech Specs'
            f_.append(feature)

        item['features'] = json.dumps(f_)

        category = list()

        category = response.xpath('//ul[@class="breadcrumbs"]//li//a//span//text()').getall()
        category_url = response.xpath('//ul[@class="breadcrumbs"]//li//a//@href').getall()
        category_url1 = list()
        for kk in category_url:
            category_url = 'https://www.cdw.com' + kk
            category_url1.append(category_url)

        cat_list = list()
        for mm, nn in zip(category, category_url1):
            cat_list.append({
                "name": mm.strip(),
                "url": nn.strip(),
            })

        scrape_metadata = dict()
        scrape_metadata['url'] = kwargs['url']
        scrape_metadata['breadcrumbs'] = cat_list
        scrape_metadata['date_visited'] = str(datetime.now()).replace(" ", "T")[:-3] + "Z"

        item['_scrape_metadata'] = json.dumps(scrape_metadata)

        if not os.path.exists(self.page_save + item['sku'] + "_attribut_url" + ".html"):
            attribut_url = f'https://www.cdw.com/api/product/1/data/technicalspecifications/{item["sku"]}?_=1685704296432'

            cookies = {
                'optimizelyEndUserId': 'oeu1685001507617r0.352993028636466',
                '_gcl_au': '1.1.581762258.1685001721',
                'bluecoreNV': 'false',
                '_rdt_uuid': '1685001721892.07cc02a6-06ca-4a7d-b81b-71bc40fe2330',
                '_lc2_fpi': '464f01cb1133--01h18yvp2f7hbcvs74y3y6s2sh',
                '_fbp': 'fb.1.1685001722393.1590691643',
                '__qca': 'P0-1840470368-1685001722354',
                'OptanonAlertBoxClosed': '2023-05-25T09:42:07.412Z',
                'rr_rcs': 'eF5j4cotK8lM4TMyMNU11DVkKU32MDA0sLQwN0vSTUoFEibGqRa6lpZGSbrmxmZGhiYWialJaSkAe84OBw',
                'A8A8F83D13EA4F8B917AA5F211762060': '88723E4C891C469C9BC9719F786DA34A',
                'BA9AA5C91598458BA251A10B273627B6': '85FBC097543F4D5D8BDF6F7602421BFC',
                'dtCookie': 'v_4_srv_12_sn_006F887D659D413DC2F9EF6F9135D170_perc_100000_ol_0_mul_1_app-3A9daca7aae537f807_1_rcs-3Acss_0',
                'rxVisitor': '16856051091577GAJNQVG46GS9DBQHEC9BU4CMC3BNOPO',
                'newVisitor': 'true',
                '265B10B0AD854F37A02410D8F39E9723': 'A4D6C57D-2D33-4E02-924D-7149DD11E015',
                'CartKey': '88b9cab9fd58445fb07faab66baf9428',
                'AMCVS_6B61EE6A54FA17010A4C98A7%40AdobeOrg': '1',
                's_cc': 'true',
                '_li_dcdm_c': '.cdw.com',
                '__pdst': 'fad83dfd6e0149eab10fcb8b541100c0',
                '70549A6B29AD46CF90DA19BC17972419': 'n9zwH4unV6g1osuTXxiTpF-j6qzLrAPaIRBi3d6Fs5mA4vO-yPXDUATAkuhS7W3QW40SD-Zq_V2bG4va0mdMABGKzLE1',
                'QSI_HistorySession': '',
                'ln_or': 'eyIzMTI3IjoiZCJ9',
                '_abck': '9520A65921B493C2FBE705085A79EF7B~0~YAAQ34fTFwf+0XWIAQAAIVSSewmk12/kA5ZWuNzD7CgOYdgvq4Vb1ku57yNwnjlhhoMDO35AKKDpZgWInepvCcG38YQw7Xuf8gAgAAgePBEksfDZz00i6KZPOKPO1JPZYG3wLV2ofzp5NuhoAwjJWcqlXueQd/P/VK1wF3w7MtTmpMUL1FIEsuwyVR0MIKjL/ykJ3iQ0ooj2u1qaxyizsR1xKJZW1m+2n+fl01sOcYW+jfDIhdBWhcilybbKOSq43v3XY0NNW35JPqqtOxvcS1t/Vk/nZkhkGbveVo9VduMoXvVcFM4EtCqwSnmCd+Zcw9P71/oUIIJj6jAkJcQS4i3KCcSvvS45HrQwXTv7fMgLrKScaWBP3TbIpLwShgNMfVwDohT3MTcRaHm7hmV3WzIUH01w~-1~-1~-1',
                'bm_sz': '003F68ED2B291D28C10365AE97803D74~YAAQ34fTFwj+0XWIAQAAIVSSexPuyD5SnOnN7uAnpVMIxYnrN8SDRhGFfegdv6fcb6lQZi0Sup81fH6p6xqhm5FAkcTO6NRimMTXSUrqP+iMJ8KoX3ZqenjlM2WDIy+OQ6NGlY3vsdfil/CG6SOtTotFdlinzUWKBGA4NNPoFgCDtJChYM59O+vvkDGjwR76FNNk8JMRSic7siHc3ZFS98B09Qq3GxSjGctzLNVRgRGJmTQbIEmkLAU0IQutOwEUQH/c9plFt3t+5Dlo0emEVzkpx+N9L67dd2wgze6WipM=~4272690~3750196',
                '4112525968F44D5C99DF0BDE0C235561': '_6745331,5800217,5136151,7360426,717516,6738755,559124,2565617',
                'AKA_A2': 'A',
                's_dfa': 'cdwglobalstaging',
                's_visit': '1',
                's_dl': '1',
                's_dl1': '1',
                's_dl2': '1',
                's_dl3': '1',
                'gpv_pn': 'C2G%206ft%20USB%20C%20to%20DisplayPort%20Adapter%20Cable%20-%20M%2FM',
                'bc_invalidateUrlCache_targeting': '1685704023175',
                'bm_mi': '61B46F1AB168978FE5BB73CFE2419E87~YAAQ34fTF3JJ03WIAQAANBzKexP3Ole1/ZULbe24Bg7AETM+768pStIjCekG6RfrnAN/CS7mnf9uGxlcP1qqWHFN7tPvh5DJKnmw+8Oy6HGpHK+Jh6KUViz4UHNoz1bHhSqubY+0yH7nIYNannFaXPTDZ05C/ZLWd2iFECtxH8kJyq1/bjnSeMflAenF2YjlcV2VrgHuAsDLAoF5AXyRcylQ3lAxzX3cK3H1Ou2oZf5pICgHFqO1dAhOKAhj1KX8xW44gpXnSFNolLidkx5TgaoIFGmAnbOqtFuUhqVUA7877XvjT8LVErqrFWxVcDcqOx0Hn8LEPcoPkM8Md7yzwnezwRyzOhj+9DSYBq2C0+8GCmvbWLCI+wzfspme6bym8y/A4WtaArA=~1',
                'cto_bundle': 'JzZBx19sMCUyQjdjZlF2Y1Z4NFo4empsUGhWZVFwbEZ5N1BlOSUyQjN4Q29rZ2VEZXA5dVI1VXdnVFRFTlVwMXk5N2hUSzlBYXNHN1F6aDZlRjY5N2c1RExkUU1yRXhwOUJmYmNwbjVUNVNsOE1pNVhoYTNVVjFXWVRJOWNsc2cwZGRmbVFucyUyRm9YOW9uRFFOQUQ3dWhKU1hyeTI2YUElM0QlM0Q',
                'ak_bmsc': '61D972BFB0B9FF9EF43EB460D6C323F8~000000000000000000000000000000~YAAQ34fTFxxK03WIAQAA9ibKexNg3PyeRQO2BdqOJ2bwPtkvwv5KOnO3shwyL4U/QVtV2pqvHp+3FUaUPeqBolOJ3+NMJ3I4lh3jvcWAH3G67p2u9JRL+3bess5pGiyBZLgC58MjzmWJZbLAFgEChr7B+KvPp+/24kO1Kg7m0nR6d28a3DsOJx3w6PdkxuaOi2Qtqt2Gy72hU4xY+FHWhbChNnFaWqkbSxdHCo3wBq2sKcXQSUpZdH6sTKuldgCfbWZxD1pWSfKnB2vwRYLbVk6BQXIVA7LKKWVKSkuU6KmfNG+i+Fe6fTdLDfxAsTLIfgUbYgBFQa81quRM27SQxuNd4o+6e21fHip2dwkr2yXxG0FS4A7VwHkdW6SfZtQVLMKzTG/N9ySkG6zqkTEFoAE35fSpzl1dkp4nBH8duaSvco2sFsMekvE4hsP14C18qiOGiXZV726uifnlRGF074gOvStTZOyDfNqwQfWaGbUP5ZzU742eSwYaETYuOrY57B4IyquRX/KSziuhKoFbvnlpy21M6uf/Ti/4j5hrM2fIu+ko2ipYNpi15xK6JczpYsSr98hQAYpSYA+n',
                'SC_LINKS': '%5B%5BB%5D%5D',
                's_sq': '%5B%5BB%5D%5D',
                'dtPC': '12$304295124_946h1vCGDDFGMECRACFPFCACQEGFBUHKHEAQCU-0e0',
                'dtLatC': '5',
                'dtSa': '-',
                'rxvt': '1685706095144|1685703065139',
                'RT': '"z=1&dm=cdw.com&si=440164a2-b63c-46f4-8d7c-efcbaa7839d4&ss=liegne03&sl=0&tt=0&bcn=%2F%2F684d0d43.akstat.io%2F"',
                's_ppvl': '6745331%2C78%2C88%2C3195%2C1920%2C534%2C1920%2C1080%2C1%2CL',
                's_ptc': '%5B%5BB%5D%5D',
                'OptanonConsent': 'isGpcEnabled=0&datestamp=Fri+Jun+02+2023+16%3A41%3A37+GMT%2B0530+(India+Standard+Time)&version=202301.2.0&isIABGlobal=false&hosts=&consentId=fccd4fdb-b668-4e30-9daf-4f20c0f0477a&interactionCount=3&landingPath=NotLandingPage&groups=C0003%3A1%2CC0004%3A1%2CC0001%3A1%2CC0002%3A1&AwaitingReconsent=false&geolocation=SG%3B',
                'mp_cdw_mixpanel': '%7B%22distinct_id%22%3A%20%2218851ead4b95d9-01f9259ca068d8-26031a51-1fa400-18851ead4bac22%22%2C%22bc_persist_updated%22%3A%201685001524412%7D',
                'utag_main': 'v_id:018851ea957a0000de717a3bd91a0506f001406700bd0$_sn:18$_se:8$_ss:0$_st:1685706095991$random_number:27$vapi_domain:cdw.com$dc_visit:18$ses_id:1685704022397%3Bexp-session$_pn:2%3Bexp-session$dcsyncran:1%3Bexp-session$dc_event:8%3Bexp-session$dc_region:ap-east-1%3Bexp-session',
                's_ppv': '6745331%2C22%2C34%2C834%2C1920%2C534%2C1920%2C1080%2C1%2CL',
                '_uetsid': '55801c70004f11eea86fb7f830d3c4bf',
                '_uetvid': '6df960f0fad211eda0653d8cf158d25e',
                'needlepin': 'N190d168500152592143f5800210310381823d53e8182e8d578182e8e69002220008182e8e6928c00000000138182e8d6200000000000005invT20138182d7af233a3',
                'AMCV_6B61EE6A54FA17010A4C98A7%40AdobeOrg': '1585540135%7CMCMID%7C40407086489455280136413274095147520423%7CMCOPTOUT-1685711499s%7CNONE%7CvVersion%7C4.4.0',
                'bm_sv': 'ABA4663569F79E4F2D56D89B2D2310DD~YAAQ34fTF/9j03WIAQAAkFHOexMcnbXkTrUaTW+pwLiwBaEcGbKPIDxUK+phXjLcevTmUO/1wsrtmXrfb99hV33u48BIdCftqEfjHcsopNlUekv2FrYICksCrEdpb5/9/tgtV8h43FEQ789TMLYdpHOsKbIaHxrwSrnQ2VpWm2sl0butBrtKs6z16+HoArqXwaznklgHfKukMqNjo5xbeHx2cxP8GZJBxzXHFkv0jwRWO3nVtnqJx3S5BvcFEQ==~1',
            }

            headers = {
                'authority': 'www.cdw.com',
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                # 'cookie': 'optimizelyEndUserId=oeu1685001507617r0.352993028636466; _gcl_au=1.1.581762258.1685001721; bluecoreNV=false; _rdt_uuid=1685001721892.07cc02a6-06ca-4a7d-b81b-71bc40fe2330; _lc2_fpi=464f01cb1133--01h18yvp2f7hbcvs74y3y6s2sh; _fbp=fb.1.1685001722393.1590691643; __qca=P0-1840470368-1685001722354; OptanonAlertBoxClosed=2023-05-25T09:42:07.412Z; rr_rcs=eF5j4cotK8lM4TMyMNU11DVkKU32MDA0sLQwN0vSTUoFEibGqRa6lpZGSbrmxmZGhiYWialJaSkAe84OBw; A8A8F83D13EA4F8B917AA5F211762060=88723E4C891C469C9BC9719F786DA34A; BA9AA5C91598458BA251A10B273627B6=85FBC097543F4D5D8BDF6F7602421BFC; dtCookie=v_4_srv_12_sn_006F887D659D413DC2F9EF6F9135D170_perc_100000_ol_0_mul_1_app-3A9daca7aae537f807_1_rcs-3Acss_0; rxVisitor=16856051091577GAJNQVG46GS9DBQHEC9BU4CMC3BNOPO; newVisitor=true; 265B10B0AD854F37A02410D8F39E9723=A4D6C57D-2D33-4E02-924D-7149DD11E015; CartKey=88b9cab9fd58445fb07faab66baf9428; AMCVS_6B61EE6A54FA17010A4C98A7%40AdobeOrg=1; s_cc=true; _li_dcdm_c=.cdw.com; __pdst=fad83dfd6e0149eab10fcb8b541100c0; 70549A6B29AD46CF90DA19BC17972419=n9zwH4unV6g1osuTXxiTpF-j6qzLrAPaIRBi3d6Fs5mA4vO-yPXDUATAkuhS7W3QW40SD-Zq_V2bG4va0mdMABGKzLE1; QSI_HistorySession=; ln_or=eyIzMTI3IjoiZCJ9; _abck=9520A65921B493C2FBE705085A79EF7B~0~YAAQ34fTFwf+0XWIAQAAIVSSewmk12/kA5ZWuNzD7CgOYdgvq4Vb1ku57yNwnjlhhoMDO35AKKDpZgWInepvCcG38YQw7Xuf8gAgAAgePBEksfDZz00i6KZPOKPO1JPZYG3wLV2ofzp5NuhoAwjJWcqlXueQd/P/VK1wF3w7MtTmpMUL1FIEsuwyVR0MIKjL/ykJ3iQ0ooj2u1qaxyizsR1xKJZW1m+2n+fl01sOcYW+jfDIhdBWhcilybbKOSq43v3XY0NNW35JPqqtOxvcS1t/Vk/nZkhkGbveVo9VduMoXvVcFM4EtCqwSnmCd+Zcw9P71/oUIIJj6jAkJcQS4i3KCcSvvS45HrQwXTv7fMgLrKScaWBP3TbIpLwShgNMfVwDohT3MTcRaHm7hmV3WzIUH01w~-1~-1~-1; bm_sz=003F68ED2B291D28C10365AE97803D74~YAAQ34fTFwj+0XWIAQAAIVSSexPuyD5SnOnN7uAnpVMIxYnrN8SDRhGFfegdv6fcb6lQZi0Sup81fH6p6xqhm5FAkcTO6NRimMTXSUrqP+iMJ8KoX3ZqenjlM2WDIy+OQ6NGlY3vsdfil/CG6SOtTotFdlinzUWKBGA4NNPoFgCDtJChYM59O+vvkDGjwR76FNNk8JMRSic7siHc3ZFS98B09Qq3GxSjGctzLNVRgRGJmTQbIEmkLAU0IQutOwEUQH/c9plFt3t+5Dlo0emEVzkpx+N9L67dd2wgze6WipM=~4272690~3750196; 4112525968F44D5C99DF0BDE0C235561=_6745331,5800217,5136151,7360426,717516,6738755,559124,2565617; AKA_A2=A; s_dfa=cdwglobalstaging; s_visit=1; s_dl=1; s_dl1=1; s_dl2=1; s_dl3=1; gpv_pn=C2G%206ft%20USB%20C%20to%20DisplayPort%20Adapter%20Cable%20-%20M%2FM; bc_invalidateUrlCache_targeting=1685704023175; bm_mi=61B46F1AB168978FE5BB73CFE2419E87~YAAQ34fTF3JJ03WIAQAANBzKexP3Ole1/ZULbe24Bg7AETM+768pStIjCekG6RfrnAN/CS7mnf9uGxlcP1qqWHFN7tPvh5DJKnmw+8Oy6HGpHK+Jh6KUViz4UHNoz1bHhSqubY+0yH7nIYNannFaXPTDZ05C/ZLWd2iFECtxH8kJyq1/bjnSeMflAenF2YjlcV2VrgHuAsDLAoF5AXyRcylQ3lAxzX3cK3H1Ou2oZf5pICgHFqO1dAhOKAhj1KX8xW44gpXnSFNolLidkx5TgaoIFGmAnbOqtFuUhqVUA7877XvjT8LVErqrFWxVcDcqOx0Hn8LEPcoPkM8Md7yzwnezwRyzOhj+9DSYBq2C0+8GCmvbWLCI+wzfspme6bym8y/A4WtaArA=~1; cto_bundle=JzZBx19sMCUyQjdjZlF2Y1Z4NFo4empsUGhWZVFwbEZ5N1BlOSUyQjN4Q29rZ2VEZXA5dVI1VXdnVFRFTlVwMXk5N2hUSzlBYXNHN1F6aDZlRjY5N2c1RExkUU1yRXhwOUJmYmNwbjVUNVNsOE1pNVhoYTNVVjFXWVRJOWNsc2cwZGRmbVFucyUyRm9YOW9uRFFOQUQ3dWhKU1hyeTI2YUElM0QlM0Q; ak_bmsc=61D972BFB0B9FF9EF43EB460D6C323F8~000000000000000000000000000000~YAAQ34fTFxxK03WIAQAA9ibKexNg3PyeRQO2BdqOJ2bwPtkvwv5KOnO3shwyL4U/QVtV2pqvHp+3FUaUPeqBolOJ3+NMJ3I4lh3jvcWAH3G67p2u9JRL+3bess5pGiyBZLgC58MjzmWJZbLAFgEChr7B+KvPp+/24kO1Kg7m0nR6d28a3DsOJx3w6PdkxuaOi2Qtqt2Gy72hU4xY+FHWhbChNnFaWqkbSxdHCo3wBq2sKcXQSUpZdH6sTKuldgCfbWZxD1pWSfKnB2vwRYLbVk6BQXIVA7LKKWVKSkuU6KmfNG+i+Fe6fTdLDfxAsTLIfgUbYgBFQa81quRM27SQxuNd4o+6e21fHip2dwkr2yXxG0FS4A7VwHkdW6SfZtQVLMKzTG/N9ySkG6zqkTEFoAE35fSpzl1dkp4nBH8duaSvco2sFsMekvE4hsP14C18qiOGiXZV726uifnlRGF074gOvStTZOyDfNqwQfWaGbUP5ZzU742eSwYaETYuOrY57B4IyquRX/KSziuhKoFbvnlpy21M6uf/Ti/4j5hrM2fIu+ko2ipYNpi15xK6JczpYsSr98hQAYpSYA+n; SC_LINKS=%5B%5BB%5D%5D; s_sq=%5B%5BB%5D%5D; dtPC=12$304295124_946h1vCGDDFGMECRACFPFCACQEGFBUHKHEAQCU-0e0; dtLatC=5; dtSa=-; rxvt=1685706095144|1685703065139; RT="z=1&dm=cdw.com&si=440164a2-b63c-46f4-8d7c-efcbaa7839d4&ss=liegne03&sl=0&tt=0&bcn=%2F%2F684d0d43.akstat.io%2F"; s_ppvl=6745331%2C78%2C88%2C3195%2C1920%2C534%2C1920%2C1080%2C1%2CL; s_ptc=%5B%5BB%5D%5D; OptanonConsent=isGpcEnabled=0&datestamp=Fri+Jun+02+2023+16%3A41%3A37+GMT%2B0530+(India+Standard+Time)&version=202301.2.0&isIABGlobal=false&hosts=&consentId=fccd4fdb-b668-4e30-9daf-4f20c0f0477a&interactionCount=3&landingPath=NotLandingPage&groups=C0003%3A1%2CC0004%3A1%2CC0001%3A1%2CC0002%3A1&AwaitingReconsent=false&geolocation=SG%3B; mp_cdw_mixpanel=%7B%22distinct_id%22%3A%20%2218851ead4b95d9-01f9259ca068d8-26031a51-1fa400-18851ead4bac22%22%2C%22bc_persist_updated%22%3A%201685001524412%7D; utag_main=v_id:018851ea957a0000de717a3bd91a0506f001406700bd0$_sn:18$_se:8$_ss:0$_st:1685706095991$random_number:27$vapi_domain:cdw.com$dc_visit:18$ses_id:1685704022397%3Bexp-session$_pn:2%3Bexp-session$dcsyncran:1%3Bexp-session$dc_event:8%3Bexp-session$dc_region:ap-east-1%3Bexp-session; s_ppv=6745331%2C22%2C34%2C834%2C1920%2C534%2C1920%2C1080%2C1%2CL; _uetsid=55801c70004f11eea86fb7f830d3c4bf; _uetvid=6df960f0fad211eda0653d8cf158d25e; needlepin=N190d168500152592143f5800210310381823d53e8182e8d578182e8e69002220008182e8e6928c00000000138182e8d6200000000000005invT20138182d7af233a3; AMCV_6B61EE6A54FA17010A4C98A7%40AdobeOrg=1585540135%7CMCMID%7C40407086489455280136413274095147520423%7CMCOPTOUT-1685711499s%7CNONE%7CvVersion%7C4.4.0; bm_sv=ABA4663569F79E4F2D56D89B2D2310DD~YAAQ34fTF/9j03WIAQAAkFHOexMcnbXkTrUaTW+pwLiwBaEcGbKPIDxUK+phXjLcevTmUO/1wsrtmXrfb99hV33u48BIdCftqEfjHcsopNlUekv2FrYICksCrEdpb5/9/tgtV8h43FEQ789TMLYdpHOsKbIaHxrwSrnQ2VpWm2sl0butBrtKs6z16+HoArqXwaznklgHfKukMqNjo5xbeHx2cxP8GZJBxzXHFkv0jwRWO3nVtnqJx3S5BvcFEQ==~1',
                'referer': 'https://www.cdw.com/product/c2g-6ft-usb-c-to-displayport-adapter-cable-m-m/6745331?pfm=srh',
                'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': get_useragent(),
                'x-requested-with': 'XMLHttpRequest',
            }

            params = {
                '_': '1685704296432',
            }

            response_attributs = requests.get(
                url=attribut_url,
                params=params,
                cookies=cookies,
                headers=headers,
            )
            open(self.page_save + item['sku'] + "_attribut_url" + ".html", "w", encoding='utf-8').write(response_attributs.text)
            data_attributs = json.loads(response_attributs.text)
        else:
            data = open(self.page_save + item['sku'] + "_attribut_url" + ".html", "r", encoding='utf-8').read()
            data_attributs = json.loads(data)


        if data_attributs:
            myattribute_llist = list()
            if 'AttributeGroups' in data_attributs:
                key = []
                value = []
                group = []
                for kkk in data_attributs['AttributeGroups']:

                    for lll in kkk['Attributes']:
                        key = lll['Key']
                        value = lll['Value']
                        group =  kkk['FolderName']
                        myattribute_llist.append(
                            {"name": key.strip(),
                             "value": value.strip(),
                             "group": group
                             }
                        )



                    item['attributes'] = json.dumps(myattribute_llist,ensure_ascii=False)

        # key = response.xpath(
        #     '//table[@class="woocommerce-product-attributes shop_attributes desc-attr-table"]//th//text()').getall()
        # value = response.xpath(
        #     '//table[@class="woocommerce-product-attributes shop_attributes desc-attr-table"]//td//text()').getall()
        #
        # if key == [] and value == []:
        #     key = response.xpath(
        #         '//table[@class="woocommerce-product-attributes shop_attributes"]//tr//th//text()').getall()
        #
        #     value = response.xpath(
        #         '//table[@class="woocommerce-product-attributes shop_attributes"]//tr//td//text()').getall()
        #
        # value = [elem for elem in value if elem != '\n']
        #
        # myattribute_llist = list()
        # for m, n in zip(key, value):
        #     myattribute_llist.append(
        #         {"name": m.strip(),
        #          "value": n.strip(),
        #          "group": "Specifications"
        #          }
        #     )
        # item['attributes']  =


#pricing

        item1 = IcsV1PricingItem()
        item1['vendor_id'] = 'ACT-B3-010'
        item1['sku'] = item['sku']
        price_main = response.xpath('//span[@class="price"]//span//text()').get()
        if price_main == 'Request Pricing' or price_main == None:
            if response.xpath('//div[@class="ui-messageselector"]//p//text()'):
                item1['price_string'] = None
            else:
                item1['price_string'] = 'call for price'
        else:
            price_float = price_main.replace('$','').replace(',','')

            price_main_1 = response.xpath('//span[@class="price"]//span//text()').get()
            price_float_1 = price_main.replace('$', '').replace(',', '')
            if price_float_1 != 'Request Pricing':
                item1['price'] = price_float

        item1['currency'] = 'USD'

        item1['hash_key'] = item['hash_key']
        item2 = IcsV1AssetItem()
        item2['vendor_id'] = 'ACT-B3-010'
        item2['sku'] = item['sku']

        item2['hash_key'] =  item['hash_key']

        image_response_url  = f'https://webobjects2.cdw.com/is/image/CDW/{item["sku"]}_IS?req=set,json&handler=cbImageGallery1685693998540&callback=cbImageGallery1685693998540&_=1685693995859'

        image_response_url_cookies = {
            'optimizelyEndUserId': 'oeu1685001507617r0.352993028636466',
            '_gcl_au': '1.1.581762258.1685001721',
            '_rdt_uuid': '1685001721892.07cc02a6-06ca-4a7d-b81b-71bc40fe2330',
            '_lc2_fpi': '464f01cb1133--01h18yvp2f7hbcvs74y3y6s2sh',
            '_fbp': 'fb.1.1685001722393.1590691643',
            '__qca': 'P0-1840470368-1685001722354',
            'OptanonAlertBoxClosed': '2023-05-25T09:42:07.412Z',
            'rr_rcs': 'eF5j4cotK8lM4TMyMNU11DVkKU32MDA0sLQwN0vSTUoFEibGqRa6lpZGSbrmxmZGhiYWialJaSkAe84OBw',
            'A8A8F83D13EA4F8B917AA5F211762060': '88723E4C891C469C9BC9719F786DA34A',
            'BA9AA5C91598458BA251A10B273627B6': '85FBC097543F4D5D8BDF6F7602421BFC',
            'dtCookie': 'v_4_srv_12_sn_006F887D659D413DC2F9EF6F9135D170_perc_100000_ol_0_mul_1_app-3A9daca7aae537f807_1_rcs-3Acss_0',
            'rxVisitor': '16856051091577GAJNQVG46GS9DBQHEC9BU4CMC3BNOPO',
            '265B10B0AD854F37A02410D8F39E9723': 'A4D6C57D-2D33-4E02-924D-7149DD11E015',
            'CartKey': '88b9cab9fd58445fb07faab66baf9428',
            'AMCVS_6B61EE6A54FA17010A4C98A7%40AdobeOrg': '1',
            's_cc': 'true',
            '_li_dcdm_c': '.cdw.com',
            '_abck': '9520A65921B493C2FBE705085A79EF7B~0~YAAQ9IfTFymwnyeIAQAAkrWyegnZbNpOCjNSYB4EMEi5ldEE7LtpbQaIG3hsjl6B4MX88ITkQhfXU5qOxzSA/pV3AOMxdpaTzqfmoN5X+d7k7Bu1Ap9ijQKwQELCcu0bOFQrKgZ/y2T3KnrGyYdqU/WtgFJC5osytm5tmGy87pQ1BS/fdgANRNKI/EzArIIx8zbQJuMLfTn1MWNt8wcPAdaQWigkgBw4DfenZReVw0rxdkXrliawzLpnnqKAL2Ub/4HSkoVeyDa4zeAd6oQPdSTmN+DmBUFnkBG/JtuQkVeUPDJExgCffI9YTgo/y+JdkN9ehqkHuvLHLAwPUFV1JplxuyGtRQuzNr5kYSZON5QQZM4o+NLynct2kkYg5pWwhFyi0X1JiJ7/H1Pd5oXUxM8gVKaR~-1~-1~-1',
            'bm_sz': 'F5BF2DE7C9D160B3F23C2349E135A25C~YAAQ9IfTFyuwnyeIAQAAkrWyehP6TvBj3NX78stwRxBAtcGeGw1EY2Tq9wfTRdAaU7soyeiEyUgn+jsexF0jzEs2o7AKtzbIg0arboYJ9E8rcyEqS/mcF9IeGlLVYb4N4HE+MHvOsiORsCn12zB9pg8ZsAlbMaq95YXSXC7ExEhaqXwvy8npAN2uQrG3fs5W/sdgw5XzIVsHxkJiJMOxwWpJBKcttgxyn5qx7vn87vG+4lh810GmO5FowTmsh5Jyr49DuyeRk3dkP82GQYC3OpXWoP1vWZHFmiv5SmGXoGQ=~3748152~4539448',
            'AKA_A2': 'A',
            'bm_mi': '3C59EBE7056A427D488FAAE3BA102B86~YAAQ34fTFwyQz3WIAQAA5j4rexO84FlGSmV7boDWbE5bUm8uvZRaEwYMkHWyrySqCWTF9mcuIEkxvcICXwp8qOGfptNAGBB5Ff/54P+HKRkdmOaijun2/gQFPWwkVQileeEEl0HQ37mCdHUmvH74XMKik1BDvy5yDvakenn7N9x1qJ7MDnJoBrO0bvNoE6Lr5c/QHa79r6zUCMOqcpTzDHY+dm+w3B9KjAlHDn1mpisQlIhPQlYv6JvMse3Xxw38Bezc4dGEN3VYkWElqFyLQGLNNeGs0yJOHJFm8PkEkLaRJqpDyzef8OFFFJOQ31Gsb2g+/0vmgQtKns96OUYnDpjNmVoip9Tp6aL9Ne/MHTy8AxQll7La504R4cpcP+ojASyjUc1QNrq7~1',
            's_dfa': 'cdwglobalstaging',
            'ak_bmsc': '429F0EF5B0370988C0C2866AC347E31D~000000000000000000000000000000~YAAQ34fTF4eQz3WIAQAAMEorexOdDTlYHMHI7wP25OzqO3YUnMKM9jvwmNc+wuGlYlu18ZOlsGFP/H490lvofMuqcSgI2HzA4Ok3tWthHdulxmv3ZAw/+UOfgTs2FXU57Iw1OBsWGZKC6ydalN4zVOSm//7i7/gh2PxQGs0K2UyU6oROkM/azMc1c2tHzVQRZ9at63VEXsgkn0A5xcLAeSElYOWJvYhsLyqHow5PttYy5Zo//f6tsSU2pItU2GiWjDvVfhAFbS91twezZB3uzPo1dryRWeVtGWVOzUTz7IeQ5DTXcpGZRBVxc/LIvPUw5QlzpoRrnF96y8c5h+XhiMm3GrA4fr+lZglKgQ6c7NjEWknnZl+cLdBmX+VV0kQfYf5qTdoFsf54jpWzTiySgvJz7doNIhmdeO29w/ZFIlkQdyD/uu3+eRMSaH2quhZ9zaQYMO8g6ONZ2bPKy796UB2KOdA1cUyYhcldOJ7Dn8p1/4uvc2mOKg==',
            's_visit': '1',
            's_dl': '1',
            's_dl1': '1',
            's_dl2': '1',
            's_dl3': '1',
            '4112525968F44D5C99DF0BDE0C235561': '_5800217,5136151,6745331,7360426,717516,6738755,559124,2565617',
            'gpv_pn': 'Proline%2012ft%20RJ-45%20%28M%29%2FRJ-45%20%28M%29%20Black%20Cat6%20Straight%20UTP%20PVC%20Patch%20Cable',
            'cto_bundle': 'hFBGAl9sMCUyQjdjZlF2Y1Z4NFo4empsUGhWZVhGeHNzV2cwYnNUSiUyRk9VSnd2ZmNKY0Z3OXVWSExvbHN5NzBZeHFMendJVHJzNzM5Q2xNSEJ3Y2dOOEMyb0xwWGoxYndraFBEeE1ZWkNDRDZva2FPNXZTSER0OVJsUUt0aSUyQlpyZ1pwM3V2RGJ3VnIzRTVXb3dydiUyRkh5VVZyM0thdyUzRCUzRA',
            '_uetsid': '55801c70004f11eea86fb7f830d3c4bf',
            '_uetvid': '6df960f0fad211eda0653d8cf158d25e',
            'SC_LINKS': '%5B%5BB%5D%5D',
            's_sq': '%5B%5BB%5D%5D',
            'needlepin': 'N190d168500152592142e23001f310081823d53e8182e46b28182e6619002220008182e65f928700000000138182e46e700000000000005invT20138182d7af233a3',
            'dtPC': '12$293994849_361h1vDAPGKSDHCWIACAWGKVWTUSMDROKHCEIU-0e0',
            'dtLatC': '10010',
            'dtSa': '-',
            'rxvt': '1685695794878|1685693157189',
            'RT': '"z=1&dm=cdw.com&si=440164a2-b63c-46f4-8d7c-efcbaa7839d4&ss=lieagehg&sl=8&tt=tld&bcn=%2F%2F684d0d49.akstat.io%2F"',
            'bm_sv': 'DB458953552DDAD892E37DC743260657~YAAQ34fTF+6pz3WIAQAA4BwxexMddHqE3bJsbZnw7uj0rN/LNqiJaAdTHL4DgvA6pBJgsxpG8woukcP1V5iaQ9K42gOIDd/2iP7Qq8obzXYe1kAyMZZl9INNmEY2gIl45lzo0jP5Ozfv9F4L6bClRw97vYoPiM+pSi3ttnlyfBWk/65j8oCBxhXW4DPQLfi2g4GFP3PGrPXqOGmwdxsE0XaBUrxEW240m58SGGFtypibVe7zmHX1hlHxU7rCVQ==~1',
            's_ppvl': '5136151%2C54%2C60%2C1512%2C1920%2C306%2C1920%2C1080%2C1%2CL',
            'AMCV_6B61EE6A54FA17010A4C98A7%40AdobeOrg': '1585540135%7CMCMID%7C40407086489455280136413274095147520423%7CMCOPTOUT-1685701196s%7CNONE%7CvVersion%7C4.4.0',
            'mp_cdw_mixpanel': '%7B%22distinct_id%22%3A%20%2218851ead4b95d9-01f9259ca068d8-26031a51-1fa400-18851ead4bac22%22%2C%22bc_persist_updated%22%3A%201685001524412%7D',
            'utag_main': 'v_id:018851ea957a0000de717a3bd91a0506f001406700bd0$_sn:17$_se:7$_ss:0$_st:1685695795206$random_number:27$vapi_domain:cdw.com$dc_visit:17$ses_id:1685693613980%3Bexp-session$_pn:5%3Bexp-session$dcsyncran:1%3Bexp-session$dc_event:7%3Bexp-session$dc_region:ap-east-1%3Bexp-session',
            's_ptc': '0.06%5E%5E0.00%5E%5E0.00%5E%5E0.00%5E%5E0.47%5E%5E0.00%5E%5E8.56%5E%5E0.06%5E%5E9.33',
            'OptanonConsent': 'isGpcEnabled=0&datestamp=Fri+Jun+02+2023+13%3A49%3A57+GMT%2B0530+(India+Standard+Time)&version=202301.2.0&isIABGlobal=false&hosts=&consentId=fccd4fdb-b668-4e30-9daf-4f20c0f0477a&interactionCount=3&landingPath=NotLandingPage&groups=C0003%3A1%2CC0004%3A1%2CC0001%3A1%2CC0002%3A1&AwaitingReconsent=false&geolocation=SG%3B',
            's_ppv': '5136151%2C48%2C47%2C1033%2C1920%2C306%2C1920%2C1080%2C1%2CL',
        }

        image_response_url_headers = {
            'authority': 'webobjects2.cdw.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            # 'cookie': 'optimizelyEndUserId=oeu1685001507617r0.352993028636466; _gcl_au=1.1.581762258.1685001721; _rdt_uuid=1685001721892.07cc02a6-06ca-4a7d-b81b-71bc40fe2330; _lc2_fpi=464f01cb1133--01h18yvp2f7hbcvs74y3y6s2sh; _fbp=fb.1.1685001722393.1590691643; __qca=P0-1840470368-1685001722354; OptanonAlertBoxClosed=2023-05-25T09:42:07.412Z; rr_rcs=eF5j4cotK8lM4TMyMNU11DVkKU32MDA0sLQwN0vSTUoFEibGqRa6lpZGSbrmxmZGhiYWialJaSkAe84OBw; A8A8F83D13EA4F8B917AA5F211762060=88723E4C891C469C9BC9719F786DA34A; BA9AA5C91598458BA251A10B273627B6=85FBC097543F4D5D8BDF6F7602421BFC; dtCookie=v_4_srv_12_sn_006F887D659D413DC2F9EF6F9135D170_perc_100000_ol_0_mul_1_app-3A9daca7aae537f807_1_rcs-3Acss_0; rxVisitor=16856051091577GAJNQVG46GS9DBQHEC9BU4CMC3BNOPO; 265B10B0AD854F37A02410D8F39E9723=A4D6C57D-2D33-4E02-924D-7149DD11E015; CartKey=88b9cab9fd58445fb07faab66baf9428; AMCVS_6B61EE6A54FA17010A4C98A7%40AdobeOrg=1; s_cc=true; _li_dcdm_c=.cdw.com; _abck=9520A65921B493C2FBE705085A79EF7B~0~YAAQ9IfTFymwnyeIAQAAkrWyegnZbNpOCjNSYB4EMEi5ldEE7LtpbQaIG3hsjl6B4MX88ITkQhfXU5qOxzSA/pV3AOMxdpaTzqfmoN5X+d7k7Bu1Ap9ijQKwQELCcu0bOFQrKgZ/y2T3KnrGyYdqU/WtgFJC5osytm5tmGy87pQ1BS/fdgANRNKI/EzArIIx8zbQJuMLfTn1MWNt8wcPAdaQWigkgBw4DfenZReVw0rxdkXrliawzLpnnqKAL2Ub/4HSkoVeyDa4zeAd6oQPdSTmN+DmBUFnkBG/JtuQkVeUPDJExgCffI9YTgo/y+JdkN9ehqkHuvLHLAwPUFV1JplxuyGtRQuzNr5kYSZON5QQZM4o+NLynct2kkYg5pWwhFyi0X1JiJ7/H1Pd5oXUxM8gVKaR~-1~-1~-1; bm_sz=F5BF2DE7C9D160B3F23C2349E135A25C~YAAQ9IfTFyuwnyeIAQAAkrWyehP6TvBj3NX78stwRxBAtcGeGw1EY2Tq9wfTRdAaU7soyeiEyUgn+jsexF0jzEs2o7AKtzbIg0arboYJ9E8rcyEqS/mcF9IeGlLVYb4N4HE+MHvOsiORsCn12zB9pg8ZsAlbMaq95YXSXC7ExEhaqXwvy8npAN2uQrG3fs5W/sdgw5XzIVsHxkJiJMOxwWpJBKcttgxyn5qx7vn87vG+4lh810GmO5FowTmsh5Jyr49DuyeRk3dkP82GQYC3OpXWoP1vWZHFmiv5SmGXoGQ=~3748152~4539448; AKA_A2=A; bm_mi=3C59EBE7056A427D488FAAE3BA102B86~YAAQ34fTFwyQz3WIAQAA5j4rexO84FlGSmV7boDWbE5bUm8uvZRaEwYMkHWyrySqCWTF9mcuIEkxvcICXwp8qOGfptNAGBB5Ff/54P+HKRkdmOaijun2/gQFPWwkVQileeEEl0HQ37mCdHUmvH74XMKik1BDvy5yDvakenn7N9x1qJ7MDnJoBrO0bvNoE6Lr5c/QHa79r6zUCMOqcpTzDHY+dm+w3B9KjAlHDn1mpisQlIhPQlYv6JvMse3Xxw38Bezc4dGEN3VYkWElqFyLQGLNNeGs0yJOHJFm8PkEkLaRJqpDyzef8OFFFJOQ31Gsb2g+/0vmgQtKns96OUYnDpjNmVoip9Tp6aL9Ne/MHTy8AxQll7La504R4cpcP+ojASyjUc1QNrq7~1; s_dfa=cdwglobalstaging; ak_bmsc=429F0EF5B0370988C0C2866AC347E31D~000000000000000000000000000000~YAAQ34fTF4eQz3WIAQAAMEorexOdDTlYHMHI7wP25OzqO3YUnMKM9jvwmNc+wuGlYlu18ZOlsGFP/H490lvofMuqcSgI2HzA4Ok3tWthHdulxmv3ZAw/+UOfgTs2FXU57Iw1OBsWGZKC6ydalN4zVOSm//7i7/gh2PxQGs0K2UyU6oROkM/azMc1c2tHzVQRZ9at63VEXsgkn0A5xcLAeSElYOWJvYhsLyqHow5PttYy5Zo//f6tsSU2pItU2GiWjDvVfhAFbS91twezZB3uzPo1dryRWeVtGWVOzUTz7IeQ5DTXcpGZRBVxc/LIvPUw5QlzpoRrnF96y8c5h+XhiMm3GrA4fr+lZglKgQ6c7NjEWknnZl+cLdBmX+VV0kQfYf5qTdoFsf54jpWzTiySgvJz7doNIhmdeO29w/ZFIlkQdyD/uu3+eRMSaH2quhZ9zaQYMO8g6ONZ2bPKy796UB2KOdA1cUyYhcldOJ7Dn8p1/4uvc2mOKg==; s_visit=1; s_dl=1; s_dl1=1; s_dl2=1; s_dl3=1; 4112525968F44D5C99DF0BDE0C235561=_5800217,5136151,6745331,7360426,717516,6738755,559124,2565617; gpv_pn=Proline%2012ft%20RJ-45%20%28M%29%2FRJ-45%20%28M%29%20Black%20Cat6%20Straight%20UTP%20PVC%20Patch%20Cable; cto_bundle=hFBGAl9sMCUyQjdjZlF2Y1Z4NFo4empsUGhWZVhGeHNzV2cwYnNUSiUyRk9VSnd2ZmNKY0Z3OXVWSExvbHN5NzBZeHFMendJVHJzNzM5Q2xNSEJ3Y2dOOEMyb0xwWGoxYndraFBEeE1ZWkNDRDZva2FPNXZTSER0OVJsUUt0aSUyQlpyZ1pwM3V2RGJ3VnIzRTVXb3dydiUyRkh5VVZyM0thdyUzRCUzRA; _uetsid=55801c70004f11eea86fb7f830d3c4bf; _uetvid=6df960f0fad211eda0653d8cf158d25e; SC_LINKS=%5B%5BB%5D%5D; s_sq=%5B%5BB%5D%5D; needlepin=N190d168500152592142e23001f310081823d53e8182e46b28182e6619002220008182e65f928700000000138182e46e700000000000005invT20138182d7af233a3; dtPC=12$293994849_361h1vDAPGKSDHCWIACAWGKVWTUSMDROKHCEIU-0e0; dtLatC=10010; dtSa=-; rxvt=1685695794878|1685693157189; RT="z=1&dm=cdw.com&si=440164a2-b63c-46f4-8d7c-efcbaa7839d4&ss=lieagehg&sl=8&tt=tld&bcn=%2F%2F684d0d49.akstat.io%2F"; bm_sv=DB458953552DDAD892E37DC743260657~YAAQ34fTF+6pz3WIAQAA4BwxexMddHqE3bJsbZnw7uj0rN/LNqiJaAdTHL4DgvA6pBJgsxpG8woukcP1V5iaQ9K42gOIDd/2iP7Qq8obzXYe1kAyMZZl9INNmEY2gIl45lzo0jP5Ozfv9F4L6bClRw97vYoPiM+pSi3ttnlyfBWk/65j8oCBxhXW4DPQLfi2g4GFP3PGrPXqOGmwdxsE0XaBUrxEW240m58SGGFtypibVe7zmHX1hlHxU7rCVQ==~1; s_ppvl=5136151%2C54%2C60%2C1512%2C1920%2C306%2C1920%2C1080%2C1%2CL; AMCV_6B61EE6A54FA17010A4C98A7%40AdobeOrg=1585540135%7CMCMID%7C40407086489455280136413274095147520423%7CMCOPTOUT-1685701196s%7CNONE%7CvVersion%7C4.4.0; mp_cdw_mixpanel=%7B%22distinct_id%22%3A%20%2218851ead4b95d9-01f9259ca068d8-26031a51-1fa400-18851ead4bac22%22%2C%22bc_persist_updated%22%3A%201685001524412%7D; utag_main=v_id:018851ea957a0000de717a3bd91a0506f001406700bd0$_sn:17$_se:7$_ss:0$_st:1685695795206$random_number:27$vapi_domain:cdw.com$dc_visit:17$ses_id:1685693613980%3Bexp-session$_pn:5%3Bexp-session$dcsyncran:1%3Bexp-session$dc_event:7%3Bexp-session$dc_region:ap-east-1%3Bexp-session; s_ptc=0.06%5E%5E0.00%5E%5E0.00%5E%5E0.00%5E%5E0.47%5E%5E0.00%5E%5E8.56%5E%5E0.06%5E%5E9.33; OptanonConsent=isGpcEnabled=0&datestamp=Fri+Jun+02+2023+13%3A49%3A57+GMT%2B0530+(India+Standard+Time)&version=202301.2.0&isIABGlobal=false&hosts=&consentId=fccd4fdb-b668-4e30-9daf-4f20c0f0477a&interactionCount=3&landingPath=NotLandingPage&groups=C0003%3A1%2CC0004%3A1%2CC0001%3A1%2CC0002%3A1&AwaitingReconsent=false&geolocation=SG%3B; s_ppv=5136151%2C48%2C47%2C1033%2C1920%2C306%2C1920%2C1080%2C1%2CL',
            'referer': 'https://www.cdw.com/',
            'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'script',
            'sec-fetch-mode': 'no-cors',
            'sec-fetch-site': 'same-site',
            'user-agent': get_useragent(),
        }

        item12 = IcsV1AssetItem()
        item12['vendor_id'] = self.VENDOR_ID
        item12['sku'] = item['sku']
        item12['hash_key'] = hash_key

        count=0
        for index, images in enumerate(response.xpath("//div[@class='main-image']/img")):
            image_item = item12.copy()
            if not index:
                image_item['is_main_image'] = True
                count = 1
            image_item['name']  =images.xpath('./@alt').get('').strip()
            image_item['source'] = images.xpath('./@src').get('')
            image_item['file_name'] = image_item['source'].split("?")[0].split("/")[-1]
            image_item['type'] = 'image/product'
            yield image_item

        if not os.path.exists(self.page_save + str(item['sku']) + "_image_response_url.html"):
            yield scrapy.Request(url=image_response_url,
                                 headers=image_response_url_headers,
                                 cookies=image_response_url_cookies,
                                 cb_kwargs={'count':count},
                                 callback=self.parse2,
                                 meta={"item":item,"item2":item2,"item1":item1},
                                 dont_filter=True)
        else:
            yield scrapy.Request(url="file:///" +self.page_save + str(item['sku']) + "_image_response_url.html",
                                 # headers=image_response_url_headers,
                                 # cookies=image_response_url_cookies,
                                 cb_kwargs={'count': count},
                                 callback=self.parse2,
                                 meta={"item": item, "item2": item2, "item1": item1})

    def parse2(self, response, **kwargs):

        item2 = IcsV1AssetItem()
        item = response.meta['item']
        item2 = response.meta['item2']
        item1 = response.meta['item1']
        item2['vendor_id'] = 'ACT-B3-010'
        item2['sku'] = item['sku']
        item2['hash_key'] = item['hash_key']
        open(self.page_save + str(item['sku']) + "_image_response_url" + ".html", "wb").write(response.body)
        a = response.text
        a = a.replace('/*jsonp*/cbImageGallery1685693998540(','').replace(',"");','')
        if a != '/*jsonp*/s7jsonError({"message":"Error while processing Fvctx image","title":"Error while processing Fvctx image"}':
            data_image = json.loads(a)
            # print(data_image)
            source_item1 = item2.copy()

            for index,iii in enumerate(data_image['set']['item']):
                if iii == 'i' or iii=='n' or iii=='s' or iii == 'dx' or iii == 'dy' or iii == 'iv':
                    source_item1[
                        'source'] = f'https://webobjects2.cdw.com/is/image/CDW/{item["sku"]}?$product-1024x768$'
                    main_image = f'https://webobjects2.cdw.com/is/image/CDW/{item["sku"]}?$product-1024x768$'
                    if main_image == source_item1['source']:
                        if kwargs['count'] == 0 :
                            source_item1['is_main_image'] = True
                        else:
                            source_item1['is_main_image'] = False
                    elif main_image != source_item1['source'] and not index:
                        source_item1['is_main_image'] = True
                    else:
                        source_item1['is_main_image'] = False
                    source_item1['type'] = 'image/product'
                    file_name = source_item1['source'].split('?')[0]
                    source_item1['file_name'] = file_name.split('/')[-1]
                    source_item1['vendor_id'] = 'ACT-B3-010'
                    source_item1['sku'] = item['sku']
                    source_item1['hash_key'] = item['hash_key']
                    source_item1['name'] = item['name']
                    yield source_item1
                else:
                    source_final = iii['i']['n']
                    source_item1['source'] = 'https://webobjects2.cdw.com/is/image/' + source_final + '?$product-1024x768$'
                    main_image = f'https://webobjects2.cdw.com/is/image/CDW/{item["sku"]}?$product-1024x768$'
                    if main_image == source_item1['source']:
                        if kwargs['count'] == 0:
                            source_item1['is_main_image'] = True
                        else:
                            source_item1['is_main_image'] = False
                    elif main_image != source_item1['source'] and not index:
                        source_item1['is_main_image'] = True
                    else:
                        source_item1['is_main_image'] = False
                    source_item1['type'] = 'image/product'
                    file_name = source_item1['source'].split('?')[0]
                    source_item1['file_name'] = file_name.split('/')[-1]
                    source_item1['vendor_id'] = 'ACT-B3-010'
                    source_item1['sku'] = item['sku']
                    source_item1['hash_key'] = item['hash_key']
                    source_item1['name'] = item['name']

                    yield source_item1
        yield item
        yield item1

if __name__ == '__main__':
    execute(f'scrapy crawl data_cdw -a start=247 -a end=133062'.split())