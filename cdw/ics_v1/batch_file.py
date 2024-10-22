import pymysql
from ics_v1 import db_config as db

db_host = db.db_host
db_user = db.db_user
db_password = db.db_password
db_name = db.db_name

asset_table = db.asset_table
product_table = db.product_table
sitemap_table = db.sitemap_table
pricing_table = db.pricing_table
category_link_brand_sep = 'category_link_brand_sep'

parts = 2
# spider_name = 'data_cdw'
spider_name = 'download_assest'

# select 0 for sitemap_link_table and 1 for asset_table and 2 for category_link_brand_sep
asset_table_parts = 1


vendor_id = "ACT-B3-010"

def database_create(parts):


    con = pymysql.connect(host=db_host, user=db_user, password=db_password, db=db_name)
    cursor = con.cursor()

    if not asset_table_parts:
        query = f'select id from {sitemap_table} where status="pending"'
    elif asset_table_parts == 1:
        query = f'select id from {asset_table} where status="pending"'
    elif asset_table_parts == 2:
        query = f'select id from {category_link_brand_sep} where status="pending"'
    else:
        # query = f'select id from {sitemap_table} where status="pending"'
        query = f'select id from {sitemap_table} where status="pending"'
    cursor.execute(query)

    id_list = []

    for i in cursor.fetchall():
        id_list.append(i[0])

    count=0
    previous_value = int()
    for i in range (0,len(id_list),(len(id_list)//parts)):
        if count == 0:
            print("taskkill /f /im scrapy.exe")
            print("taskkill /f /im python.exe")
        else:
            if not asset_table_parts:
                print(f'start "{db_name}_{count}" scrapy crawl {spider_name} -a start={previous_value} -a end={id_list[i]}')
            elif asset_table_parts == 1:
                print(f'start "{db_name}_{count}" scrapy crawl download_assest -a vendor_id={vendor_id} -a start={previous_value} -a end={id_list[i]}')
            elif asset_table_parts == 2:
                print(f'start "{db_name}_{count}" scrapy crawl {spider_name} -a start={previous_value} -a end={id_list[i]}')
            else:
                print(f'start "{db_name}_{count}" python {spider_name}.py {previous_value} {id_list[i]}')
            if count % 5 == 0:
                print("timeout /t 30")
        count+=1
        previous_value = id_list[i]

database_create(parts)
