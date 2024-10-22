import re
from datetime import datetime
import json
import os
import time
from icecream import ic
import pymysql
import pandas as pd

t1 = time.time()

# DATABASE DETAILS
db_host = 'localhost'
db_user = 'root'
db_password = 'actowiz'
db_name = 'ics_master_db_v2_Thorlabs'

asset_table = "asset_table"
product_table = "product_table"
pricing_table = "pricing_table"

# DEFINING THE GLOBALS
VENDOR_ID = "ACT-B1-002"
TODAY_DATE = datetime.now().strftime('%Y-%m-%d')
OUTPUT_LOCATION = "C:/Gaurav/Output_file/"

output_part_files = OUTPUT_LOCATION + f"{db_name}/{TODAY_DATE}/excel/"
if not os.path.exists(output_part_files):
    os.makedirs(output_part_files)

output_folder = OUTPUT_LOCATION + f"{db_name}/{TODAY_DATE}/json/"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

file_name = output_folder + f"sample_{TODAY_DATE}-v1.json"
t1 = time.time()

# DATABASE DETAILS
db_host = 'localhost'
db_user = 'root'
db_password = 'actowiz'
db_name = 'ics_master_db_v2_Thorlabs'

asset_table = "asset_table"
product_table = "product_table"
pricing_table = "pricing_table"

# DEFINING THE GLOBALS
VENDOR_ID = "ACT-B1-002"
TODAY_DATE = datetime.now().strftime('%Y-%m-%d')
OUTPUT_LOCATION = "C:/Gaurav/Output_file_final/"

output_part_files = OUTPUT_LOCATION + f"{db_name}/{TODAY_DATE}/excel/"
if not os.path.exists(output_part_files):
    os.makedirs(output_part_files)

output_folder = OUTPUT_LOCATION + f"{db_name}/{TODAY_DATE}/json/"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

file_name = output_folder + f"sample_{TODAY_DATE}-v1.json"

# Json Load :-
json_data = open("C:/Gaurav/Output_file/ics_master_db_v2_Thorlabs/2024-01-05/json/sample_2024-01-05-v1.json", "r").read()
json_loaded = json.loads(json_data)
df = pd.DataFrame(json_loaded)


# Data Solved code :-
con = pymysql.Connect(host='localhost', user='root', password='actowiz', db='ics_master_db_v2_thorlabs')
cursor = con.cursor()

query = 'select product_urls, meta_data from site_map_link_table'
cursor.execute(query)

for data in cursor.fetchall():

    category = [i['name'] for i in json.loads(data[1])]

    cat_list = list()
    cat_list.append({"name":'Home',"url": 'https://www.thorlabs.com/navigation.cfm'})
    for cate in json.loads(data[1]):
        cat_list.append({
            "name": cate['name'],
            "url": cate['url'],
        })

    scrape_metadata = dict()
    scrape_metadata['url'] = data[0]
    scrape_metadata['breadcrumbs'] = cat_list
    scrape_metadata['date_visited'] = str(datetime.now()).replace(" ", "T")[:-3] + "Z"


    try:
        index = df.query(f"`pdp_url` == '{data[0]}'").index[0]
        # print(f'OLD: {df["category"][index]}')
        # print("Before :- ",data[0])
        df['category'][index] = category
        # print("After :- ",data[0])
        # print(f'NEW: {df["category"][index]}')
        df['_scrape_metadata'][index] = scrape_metadata
    except:
        pass

empty_price_rows = df['price'].apply(lambda x: len(x) == 0)

df.drop(df[empty_price_rows].index, inplace=True)

df = df.apply(lambda x: re.sub('\s+',' ',x) if isinstance(x, str) else x)

print("\n\nGENERATING THE FILES.")
df.to_json(file_name, orient="records")
print("\n\nFILE GENERATED SUCCESSFULLY")

# VALIDATION CODE.
# validated = do_validation(file_name=file_name)

# EXCEL FILE SIZE, NUMBER OF ROWS IN A SINGLE FILE, MAX 1000000 (1M)
size = 300000

# if validated:
k = df.shape[0]
for i in range(int(k / size) + 1):
    df = df[size * i:size * (i + 1)]
    writer = pd.ExcelWriter(
        f"{output_part_files}/{TODAY_DATE}_PART_{str(i + 1).zfill(3)}.xlsx",
        engine='xlsxwriter',
        engine_kwargs={'options': {'strings_to_urls': False}}
    )
    writer.book.use_zip64()
    df.to_excel(writer)
    writer.close()

print("\n\nTOTAL PRODUCTS: ", len(df))