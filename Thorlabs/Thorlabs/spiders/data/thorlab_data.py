import datetime
import json
import os.path
import re
import hashlib
import pandas as pd
import requests
import pymysql
import scrapy
from itemloaders import ItemLoader
from itemloaders.processors import TakeFirst, Join
from scrapy.cmdline import execute
from scrapy import Selector
from bs4 import BeautifulSoup
import Thorlabs.db_config as db
from Thorlabs.items import IcsV1PDPItem, IcsV1PricingItem, IcsV1AssetItem
from icecream import ic

# Extracting attributes :-
def spec_table(html_table, sku):
    try:
        df = pd.read_html(html_table.xpath('.').get(''))
        print(df[0])
    except:
        return []
    i_key = list()
    if not df:
        return []
    for ij in df[0].keys():
        if isinstance(ij, tuple):
            i_key.append(ij[0])
            continue
        i_key.append(ij)
    if ['Item #', 'Qty', 'Description'] == i_key:
        return []
    try:
        if sku not in df[0].keys()[0]:
            attributes = list()
            if sku in df[0].keys():
                group = df[0].keys()[0]
                keys_ = df[0][group]
                values = df[0][sku]
                for index, value in enumerate(values):
                    if str(value) != 'nan':
                        attributes.append({"name": f"{keys_[index]}", "value": f"{value}", "group": f"{group}"})
                return attributes

            else:
                df_keys = list()
                try:
                    for key in df[0].keys():
                        if isinstance(key, tuple):
                            try:
                                df_keys.append(key[1])
                            except:
                                df_keys.append(key[0])
                        else:
                            df_keys.append(key)
                except:
                    return None

                attributes = list()
                for data in range(0, len(df[0]), 1):
                    try:
                        if df[0].iloc[data][0] == sku:
                            group = ""
                            key = False
                            unnamed = False
                            for index, value in enumerate(df[0].iloc[data]):
                                if not index:
                                    group = df_keys[index]
                                    if 'Unnamed' in group:
                                        group = df[0][df_keys[index]][0]
                                        key = True
                                    continue
                                if not key:
                                    if str(value) != 'nan':
                                        if 'Unnamed' in df_keys[index]:
                                            unnamed = True
                                        if unnamed:
                                            attributes.append({"name": f"{df[0].keys()[index][0]}", "value": f"{value}", "group": f"{df[0].keys()[0][0]}"})
                                        else:
                                            attributes.append({"name": f"{df_keys[index]}", "value": f"{value}", "group": f"{group}"})
                                else:
                                    if str(value) != 'nan':
                                        attributes.append({"name": f"{df[0][df_keys[index]][0]}", "value": f"{value}", "group": f"{group}"})

                    except:
                        pass

                if attributes:
                    return attributes
                else:
                    key_=False
                    for key in df[0].keys():
                        if not key_:
                            for i in df[0][key]:
                                if sku == str(i):
                                    for data in range(0, len(df[0]), 1):
                                        try:
                                            if df[0].iloc[data][1] == sku:
                                                group = ""
                                                for index, value in enumerate(df[0].iloc[data][1:]):
                                                    if not index:
                                                        group = df_keys[index+1]
                                                        continue
                                                    if str(value) != 'nan':
                                                        attributes.append({"name": f"{df_keys[index+1]}", "value": f"{value}",
                                                                           "group": f"{group}"})
                                                    else:
                                                        attributes.append({"name": f"{df_keys[index+1]}", "value": f"-",
                                                                           "group": f"{group}"})
                                        except:
                                            pass
                        ic(attributes)
                        return attributes

        else:
            group = df[0].keys()[0]
            attributes = list()
            for data in range(0, len(df[0]), 1):
                try:
                    for index, value in enumerate(df[0].iloc[data]):
                        if not index:
                            continue
                        if str(value) != 'nan':
                            attributes.append({"name": f"{df[0].iloc[data][0]}", "value": f"{value}", "group": f"{group}"})
                except:
                    pass

            return attributes
    except Exception as e:
        attributes = list()
        attr_con = False
        group = str()
        for i in df[0].keys():
            if sku in str(df[0][i]):
                for name, value in zip(df[0][df[0].keys()[0]], df[0][i]):
                    if value == sku:
                        attr_con = True
                        group = name
                        continue
                    if attr_con:
                        if str(value).lower() != 'nan':
                            attributes.append({"name": name, "value": value, "group": f"{group}"})
        return attributes




class ThorlabsDataSpider(scrapy.Spider):
    name = "thorlabs_data_m"
    # Site information :-
    VENDOR_ID = "ACT-B1-002"
    VENDOR_NAME = "Thorlabs"

    date = datetime.datetime.now()
    month = date.strftime('%B')
    # Page Save directory :-
    page_save = r'D:/PAGESAVE/Gaurav/' + VENDOR_ID + "-" + VENDOR_NAME + f"{month}/"
    common_url = 'https://www.thorlabs.com/'

    def __init__(self, name=None, start='25998', end='25998',**kwargs):
        super().__init__(name, **kwargs)
        # DATABASE CONNECTION
        self.con = pymysql.connect(host=db.db_host, user=db.db_user, password=db.db_password, db=db.db_name)
        self.cursor = self.con.cursor()
        # If Directory Not Exists Make Directory :-
        if not os.path.exists(self.page_save):
            os.makedirs(self.page_save)
        # Sets the start and end values for the fetch data id wise :-
        self.start = start
        self.end = end

    def start_requests(self):
        # Fetching Query :-
        select_query = [
            f"select id, product_urls,meta_data from {db.sitemap_table} where",
            f"vendor_id = '{self.VENDOR_ID}'",
            f"and status = 'pending'",
            f"and id between {self.start} and {self.end}"
            ]
        # Execute Query :-
        self.cursor.execute(" ".join(select_query))

        zip_list = self.cursor.fetchall()

        for data in zip_list:
            yield scrapy.Request(
                url=data[1],
                callback=self.parse,
                cb_kwargs={
                    "id": data[0],
                    "prd_url": data[1],
                    'meta_data': data[2]
                }
            )



    def parse(self, response, **kwargs):

        # Extracting SKU :-
        sku = response.xpath("//b[contains(text(),' Part Number:')]/../following-sibling::td/text()").get()
        if sku:
            sku=sku.replace('\r','').replace('\n','').replace('\t','').strip()
            if sku.strip().endswith('-'):
                sku=sku[:-1]

            if sku.endswith(' '):
                sku = sku[:-1]
            # sku = sku.replace('-', '').strip()
        else:
            sku = ""

        id = kwargs['id']
        prd_url = kwargs['prd_url']
        meta_data = kwargs['meta_data']
        hash_key = hashlib.sha256(prd_url.encode()).hexdigest()

        # Main Page Save :-
        if not os.path.exists(self.page_save + str(id) + ".html"):
            open(self.page_save + str(id) + ".html", "wb").write(response.body)

        # EXTRACTING PRODUCT DETAILS
        product_loader = ItemLoader(item=IcsV1PDPItem(), selector=response)
        product_loader.default_output_processor = TakeFirst()

        # SETTING VALUES
        product_loader.add_value('id', id)
        product_loader.add_value('vendor_id', self.VENDOR_ID)
        product_loader.add_value('vendor_name', self.VENDOR_NAME)
        product_loader.add_value('sku', sku.strip())
        product_loader.add_value('mpn', sku.strip())
        product_loader.add_value('pdp_url', kwargs['prd_url'])
        product_loader.add_value('hash_key', hash_key)

        product_loader.add_value('manufacturer', 'Thorlabs')

        pro_name1=response.xpath('//td[@class="PartTitle"]//text()').getall()
        if pro_name1:
            pro_name = ''.join(pro_name1).replace("\r","").replace("\t","").replace("\n","").strip().split(f'{sku} -')[1].strip()

        else:
            pro_name = ""
        product_loader.add_value('name', pro_name)
        avilable=response.xpath("//b[contains(text(),'Available')]/../following-sibling::td/text()").get()
        if avilable:
            product_loader.add_value('estimated_lead_time',json.dumps([{"min_qty": 1, "time_to_ship": {"raw_value": f"{avilable.strip()}"}}]))
        else:
            product_loader.add_value('estimated_lead_time',"")

        if response.xpath('//input[@value=" Add To Cart"]'):
            in_stock = True
            available_to_checkout = True
        else:
            in_stock = False
            available_to_checkout = False
        product_loader.add_value('in_stock', in_stock)
        product_loader.add_value('available_to_checkout', available_to_checkout)

        # description Request:-
        prd_discription_slug=response.xpath('//div[@class="thumbwrapper"]/following-sibling::a/@href').get()
        prd_discription_url="https://www.thorlabs.com/"+prd_discription_slug
        print(prd_discription_url)
        hash_id = int(hashlib.md5(bytes(f"{prd_discription_url}", "utf8")).hexdigest(), 16) % (10 ** 10)
        hash_save=f"{self.page_save}description_{hash_id}.html"
        if os.path.exists(hash_save):
            # discription=scrapy.FormRequest(url=f'file:///{hash_save}',meta={'filename':f'{hash_save}'})
            with open(hash_save,'r',encoding='utf-8') as file:
                data=file.read()
            prd_discription=Selector(text=data)
        else:
            cookies = {
                'LANGUAGE': 'ENGLISH',
                'LANGABBR': 'EN',
                'visid_incap_893434': 'c+Li/O1eS4SoiM9WU/x7CVzYI2QAAAAAQUIPAAAAAABwOUnqLBaolEwBbkjT2rJ4',
                'CFID': '2024017',
                'CFTOKEN': '986de87126b775f8-C3BBBC8E-B003-95FC-1DC92B740BC4A1F3',
                'LOADCURRENCY': 'Dollar',
                'LOADCURRENCYSYMBOL': '%24',
                'LOADCOUNTRY': 'IN',
                'LOADCOUNTRY2': 'India',
                'TEMPLOCAL': 'English%20%28US%29',
                'ROITRACK': '1',
                'nlbi_893434': '07SLZOlJClf6VX1DFg0eDgAAAADHSd3kXdLp2/22x6oqGhRh',
                'incap_ses_712_893434': 'Dx++BROW0VWJjt2WUYjhCe4jJGQAAAAAIEeJQKly+ghCj6N9t6cNcA==',
                'test_cookie': 'true',
            }

            headers = {
                'authority': 'www.thorlabs.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'en-US,en;q=0.9',
                'cache-control': 'max-age=0',
                # 'cookie': 'LANGUAGE=ENGLISH; LANGABBR=EN; visid_incap_893434=c+Li/O1eS4SoiM9WU/x7CVzYI2QAAAAAQUIPAAAAAABwOUnqLBaolEwBbkjT2rJ4; CFID=2024017; CFTOKEN=986de87126b775f8-C3BBBC8E-B003-95FC-1DC92B740BC4A1F3; LOADCURRENCY=Dollar; LOADCURRENCYSYMBOL=%24; LOADCOUNTRY=IN; LOADCOUNTRY2=India; TEMPLOCAL=English%20%28US%29; ROITRACK=1; nlbi_893434=07SLZOlJClf6VX1DFg0eDgAAAADHSd3kXdLp2/22x6oqGhRh; incap_ses_712_893434=Dx++BROW0VWJjt2WUYjhCe4jJGQAAAAAIEeJQKly+ghCj6N9t6cNcA==; test_cookie=true',
                'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
            }

            prd_discription1=requests.get(f'{prd_discription_url}',headers=headers,cookies=cookies)
            with open(hash_save,'w',encoding='utf-8') as file:
                file.write(prd_discription1.text)
            prd_discription=Selector(text=prd_discription1.text)

        # Extracting description :-
        desc_html_ls=list()
        if prd_discription.xpath("//h3[contains(text(),'Threading Specifications')]"):
            mytext = prd_discription.xpath(
                "//h3[contains(text(),'Threading Specifications')]/../../div//table[@class='SpecTable']").getall()
            desc_html_ls.extend(mytext)
        data2=''
        data3=''
        data1=prd_discription.xpath('//div[@id="familyImage"]//ul//text()').getall()
        data1_htm=prd_discription.xpath('//div[@id="familyImage"]//ul').get()
        if data1_htm:
            desc_html_ls.append(data1_htm)

        fordata2selec=prd_discription.xpath('//div[@class="tabContent"]')
        if fordata2selec:
            data2selec=Selector(text=' '.join(fordata2selec.xpath('.').getall()))
        else:
            data2selec = Selector(text='')
        fordata2=data2selec.xpath('//div[@class="tabContent"]')
        if fordata2:
            try:
                fordata2.xpath('//table').remove()
            except:
                pass
            try:
                fordata2.xpath('//script').remove()
            except:
                pass
            try:
                fordata2.xpath('//style').remove()
            except:
                pass
            try:
                fordata2.xpath('//h1').remove()
            except:
                pass
            try:
                fordata2.xpath('//h2').remove()
            except:
                pass
            try:
                fordata2.xpath('//h3').remove()
            except:
                pass
            try:
                fordata2.xpath('//form[@name="userFeedbackForm"]').remove()
            except:
                pass

            data2=fordata2.xpath('.//text()').getall()
            data2_html=fordata2.xpath('.').get()
            desc_html_ls.append(data2_html)

        fordata3selec = prd_discription.xpath('//div[@id="sgContainer"]').getall()
        if fordata3selec:
            data3selec = Selector(text=''.join(fordata3selec))
        else:
            data3selec = Selector(text='')

        fordata3=data3selec.xpath('//div[@id="sgContainer"]')

        if fordata3:

            try:
                fordata3.xpath('//table').remove()
            except:
                pass
            try:
                fordata3.xpath('//script').remove()
            except:
                pass
            try:
                fordata3.xpath('//style').remove()
            except:
                pass
            try:
                fordata3.xpath('//h1').remove()
            except:
                pass
            try:
                fordata3.xpath('//h2').remove()
            except:
                pass
            try:
                fordata3.xpath('//h3').remove()
            except:
                pass
            try:
                fordata3.xpath('//form[@name="userFeedbackForm"]').remove()
            except:
                pass

            data3=fordata3.xpath('.//text()').getall()

            data3_htm = fordata3.xpath('.').get()
            if data3_htm:
                desc_html_ls.append(data3_htm)


        final_disc=" ".join(data1).replace('\n',' ').strip()+" "+" ".join(data2).replace('\n',' ').strip()+" "+" ".join(data3).replace('\n',' ').strip()
        if final_disc:
            product_loader.add_value('description', final_disc.strip())
            product_loader.replace_value(
                'description',  re.sub("\s+"," "," ".join(product_loader.get_collected_values('description')).replace('\xa0',' ').strip())
            )
        else:
            description_html = prd_discription.xpath("//h3[contains(text(),'Threading Specifications')]")
            description = prd_discription.xpath("//h3[contains(text(),'Threading Specifications')]")
            product_loader.add_value('description', "")

        spc_tbl_id_f = prd_discription.xpath('//div[@class="tabTitle"][contains(text(),"Specs")]/parent::a/@name').get()
        multi_tbl_loop_f = prd_discription.xpath(f'''//div[@id="tabContainer"]//div[@id="{spc_tbl_id_f}"]//table[@class="SpecTable"]''')
        # multi_tbl_loop_f2 = prd_discription.xpath(f'''//div[@id="tabContainer"]//div[@id="{spc_tbl_id_f}"]//table[@class=" SpecTable"]''')

        # Extracting attributes :-
        attributes = list()
        for i in multi_tbl_loop_f:
            myattribute = spec_table(i, sku)
            if myattribute:
                for i in myattribute:
                    attributes.append(i)

        for i in prd_discription.xpath('//table[@class="SpecTable"]'):
            myattribute = spec_table(i, sku)
            if myattribute:
                for i in myattribute:
                    if i not in attributes:
                        attributes.append(i)

        for i in prd_discription.xpath('//table[@class=" SpecTable"]'):
            myattribute = spec_table(i, sku)
            if myattribute:
                for i in myattribute:
                    if i not in attributes:
                        attributes.append(i)

        if attributes:
            product_loader.add_value('attributes', re.sub("\s+"," ",json.dumps(attributes, ensure_ascii=False)))
        else:
            product_loader.add_value('attributes', json.dumps([]))


        val = ' '.join(desc_html_ls).strip()
        val = re.sub('href.".*?"','',re.sub('<img.*?>','',re.sub('\<a.*?\>', '', val)))
        if val:
            product_loader.add_value('description_html', re.sub("\s+"," ",val).strip())

        cat_ls = list()
        for ij in eval(meta_data):
            clean=re.compile('<.*?>')
            mycat=re.sub(clean,'',ij.get('name'))
            cat_ls.append(mycat)
        product_loader.add_value('category', json.dumps(cat_ls,ensure_ascii=False))

        scrape_metadata = dict()
        scrape_metadata['url'] = kwargs['prd_url']
        scrape_metadata['date_visited'] = str(datetime.datetime.now()).replace(" ", "T")[:-3] + "Z"

        meta_data = eval(meta_data)
        meta_data.insert(0, {"name":'Home',"url": 'https://www.thorlabs.com/navigation.cfm'})
        bcrumb = list()
        for jj in meta_data:
            bcrumb.append({'name': jj.get('name'), 'url': jj.get('url')})

        scrape_metadata['breadcrumbs'] = bcrumb
        product_loader.add_value('_scrape_metadata', json.dumps(scrape_metadata))
        product_loader.add_value('status', 'Done')
        yield product_loader.load_item()


        pricing_loaders = ItemLoader(item=IcsV1PricingItem(), selector=response)
        pricing_loaders.default_output_processor = TakeFirst()
        pricing_loaders.add_value('vendor_id', self.VENDOR_ID)
        pricing_loaders.add_value('sku', sku)

        pricing_loaders.add_value('currency', "USD")

        # Extracting pricing :-
        if response.xpath("//b[contains(text(),'Price') or contains(text(),'Pricing')]/../following-sibling::td//table[@class='bsc table table-sm table-bordered']"):
            for myprice in response.xpath("//b[contains(text(),'Price') or contains(text(),'Pricing')]/../following-sibling::td//table[@class='bsc table table-sm table-bordered']//tr[position()>1]"):
                price_item=IcsV1PricingItem()
                price_item['vendor_id'] = self.VENDOR_ID
                price_item['sku'] = sku
                price_item['currency'] = "USD"
                price_item['hash_key'] = hash_key

                if myprice.xpath('.//td[@align="center"]/text()').get():
                    qty = myprice.xpath('.//td[@align="center"]/text()').get()
                    price_item['min_qty']=qty.replace('+','').strip()
                if myprice.xpath('.//td[@align="right"]/text()').get():
                    price_my = myprice.xpath('.//td[@align="right"]/text()').get()
                    price_item['price'] = float(price_my.replace('$', '').replace(',', '').strip())
                    yield price_item
        else:
            price1 = response.xpath("//b[contains(text(),'Price')]/../following-sibling::td//text()").get()
            price = ""
            if price1:
                price = price1.replace('$', '').replace(',', '').replace('.00', '') if "$" in price1 else ""

            if price:
                pricing = price.strip()
                pstring=''

            else:
                pricing = "0.0"
                pstring='Call for price'

            if pstring:
                pricing_loaders.add_value('price_string', pstring)
            else:
                pricing_loaders.add_value('price', pricing)

            prd_qty = response.xpath('//input[@name="QTY"]/@value').get()
            prd_qty = prd_qty if prd_qty else ""
            if prd_qty:
                pricing_loaders.add_value('min_qty', prd_qty)
            else:
                pricing_loaders.add_value('min_qty', '1')


            pricing_loaders.add_value('hash_key',hash_key)

            yield pricing_loaders.load_item()

        # Extracting Assets :-
        item = IcsV1AssetItem()
        item['vendor_id'] = self.VENDOR_ID
        item['sku'] = sku

        domen = "https://www.thorlabs.com/"
        for index, images in enumerate(response.xpath('//td//img[contains(@src,"images/large") or (contains(@src,"Images/large"))]')):

            image_item = item.copy()
            if not index:
                image_item['is_main_image'] = True
            image_item['type'] = 'image/product'

            image_item['name'] = images.xpath('./@alt').get('')
            image11 = images.xpath('./@src').get('').strip()
            if 'http' not in image11:
                image_item['source'] = self.common_url + image11
            else:
                image_item['source'] =  image11

            image_item['file_name'] = image_item['source'].split("?")[0].split("/")[-1]
            if 'Button.png' in image_item['file_name']:
                continue

            # imghash_key = hashlib.sha256(f'{sku}{image_item["source"]}'.encode()).hexdigest()
            image_item['hash_key'] =hash_key

            yield image_item

        # Extracting Main Images :-
        for index, main_image in enumerate(response.xpath('//div[@class="thumbwrapper"]/a')):

            image_item = item.copy()
            if not index:
                image_item['is_main_image'] = True
            image_item['type'] = 'image/product'
            image_item['name'] = main_image.xpath('./@alt').get()
            image11 = main_image.xpath('./@href').get('').strip()
            if 'http' not in image11:
                image_item['source'] = self.common_url + image11
            else:
                image_item['source'] = image11

            image_item['file_name'] = image_item['source'].split("?")[0].split("/")[-1]
            if 'Button.png' in image_item['file_name']:
                continue

            # imghash_key = hashlib.sha256(f'{sku}{image_item["source"]}'.encode()).hexdigest()
            image_item['hash_key'] = hash_key

            yield image_item

        # Extracting data assets :-
        product_data_sheet = response.xpath('//div[@class="downloadablesleftside"]//tr/td/a[@class="downloadDoc"]')
        domen = "https://www.thorlabs.com"
        for data_sheet in product_data_sheet:
            data_sheet_item = item.copy()
            assest_name = data_sheet.xpath("./@alt").get('').strip()
            data_sheet_item['name'] = assest_name
            if assest_name:
                if 'Auto CAD PDF' in assest_name:
                    data_sheet_item['type'] = "document"
                elif 'Auto CAD DXF' in assest_name:
                    data_sheet_item['type'] = "cad/2D"
                elif 'Solidworks' in assest_name or "Step" in assest_name or "eDrawing" in assest_name:
                    data_sheet_item['type'] = "cad/3D"

                elif 'KSG101 Manual for APT' in assest_name or "KSG101 Manual for Kinesis" in assest_name:
                    data_sheet_item['type'] = "document/manual"

            sourse = data_sheet.xpath(".//@href").get('').strip()
            if 'http' not in sourse:
                data_sheet_item['source'] = self.common_url + sourse
            else:
                data_sheet_item['source'] = sourse

            if 'fileName' in data_sheet_item['source']:
                data_sheet_item['file_name'] = data_sheet_item['source'].split("fileName=")[1].split("&")[0]
            else:
                data_sheet_item['file_name'] = data_sheet_item['source'].split("?")[0].split("/")[-1]
            if data_sheet_item['source'].startswith("http") and 'View Certificate' not in data_sheet_item['name']:

                # assethash_key = hashlib.sha256(f'{sku}{data_sheet_item["source"]}'.encode()).hexdigest()
                data_sheet_item['hash_key']=hash_key

                if 'Button.png' in data_sheet_item['file_name']:
                    continue

                yield data_sheet_item

        # Extracting Extra Images :-
        # extra_imgs=prd_discription.xpath('//div[contains(@class,"Float")][not(contains(@class,"tabCallBox"))]//img')
        extra_imgs=prd_discription.xpath('//div[contains(@id,"ImgHolder")]/img|//div[contains(@class,"Float")][not(contains(@class,"tabCallBox"))]//img|//div[contains(@class,"tab-pane")]//img[contains(@src,"TabImages") or contains(@src,"tabImages") or contains(@src,"tabimages")]')

        if extra_imgs:

            for images in extra_imgs:
                    image_item1 = item.copy()

                    image_item1['name'] = images.xpath('./@alt').get('').strip()
                    image11 = images.xpath('./@src').get('').strip()
                    if 'http' not in image11:
                        image_item1['source'] = self.common_url + image11
                    else:
                        image_item1['source'] = image11
                    if ('.png' in image11 or '.gif' in image11) and ('icon' in image11 or 'downloads_button' in image11.lower() or 'button.png' in image11.lower() or 'pdf_icon' in image11.lower()):
                        continue
                    image_item1['type'] = 'image'
                    image_item1['file_name'] = image_item1['source'].split("?")[0].split("/")[-1]

                    # imghash_key1 = hashlib.sha256(f'{sku}{image_item1["source"]}'.encode()).hexdigest()
                    image_item1['hash_key'] = hash_key
                    if 'Button.png' in image_item1['file_name']:
                        continue

                    yield image_item1

        # Extracting Secondary Images :-
        secondary_imgs=response.xpath('//div[@class="ad-gallery"]//li[position()>1]/a/img')
        if secondary_imgs:
            for nim in secondary_imgs:

                image_item = item.copy()

                image_item['type'] = 'image/product'

                image_item['name'] = nim.xpath('./@alt').get('').strip()
                image11 = nim.xpath('./@src').get('').strip()
                if 'http' not in image11:
                    image_item['source'] = self.common_url + image11
                else:
                    image_item['source'] = image11

                image_item['file_name'] = image_item['source'].split("?")[0].split("/")[-1]
                if 'Button.png' in image_item['file_name']:
                    continue

                # eximghash_key1 = hashlib.sha256(f'{sku}{image_item["source"]}'.encode()).hexdigest()
                image_item['hash_key'] = hash_key

                yield image_item


if __name__ == '__main__':
    execute('scrapy crawl thorlabs_data_m -a start=62264 -a end=73252'.split())
