import pymysql
import datetime

date = datetime.datetime.now()
month = date.strftime('%B')

db_host = 'localhost'
db_user = 'root'
db_password = 'actowiz'
db_name = f"ics_master_db_v1_thorlabs_{month}"

asset_table = "asset_table"
product_table = "product_table"
sitemap_table = "site_map_link_table"
pricing_table = "pricing_table"

spider_name = 'thorlabs_data_m'
# spider_name = 'download_assest'
# spider_name = 'req_download_assest'
# select 0 for sitemap_link_table and 1 for asset_table

parts = 20
asset_table_parts = 0

vendor_id = "ACT-B1-002"

def database_create(parts):

    con = pymysql.connect(host=db_host, user=db_user, password=db_password, db=db_name)
    cursor = con.cursor()

    if not asset_table_parts:
        query = f'select id from {sitemap_table} where status="pending"'
    elif asset_table_parts == 1:
        query = f'select id from {asset_table} where status="pending"'
    else:
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
            pass
        else:
            if not asset_table_parts:
                print(f'start "{db_name}_{count}" scrapy crawl {spider_name} -a start={previous_value} -a end={id_list[i]}')
            elif asset_table_parts == 1:
                print(f'start "{db_name}_{count}" scrapy crawl download_assest -a vendor_id={vendor_id} -a start={previous_value} -a end={id_list[i]}')
            else:
                print(f'start "{db_name}_{count}" python {spider_name}.py {previous_value} {id_list[i]}')
            if count % 5 == 0:
                print("timeout /t 30")
        count+=1
        previous_value = id_list[i]

database_create(parts)



