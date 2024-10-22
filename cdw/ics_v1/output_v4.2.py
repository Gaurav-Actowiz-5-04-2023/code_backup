import gc
import html
import os
import re
import json
import time
import pymysql
import pandas as pd
from datetime import datetime
from urllib.parse import quote
from ics_v1 import db_config as db
from validator import do_validation

t1 = time.time()

db_host = db.db_host
db_user = db.db_user
db_password = db.db_password
db_name = db.db_name

asset_table = db.asset_table
product_table = db.product_table
sitemap_table = db.sitemap_table
pricing_table = db.pricing_table

# DEFINING THE GLOBALS :-
VENDOR_ID = "ACT-B3-010"
TODAY_DATE = datetime.now().strftime('%Y-%m-%d')
OUTPUT_LOCATION = "E:/DATA/gaurav/outputfile/october/"

output_part_files = OUTPUT_LOCATION + f"{db_name}/{TODAY_DATE}/excel/"
if not os.path.exists(output_part_files):
    os.makedirs(output_part_files)

output_folder = OUTPUT_LOCATION + f"{db_name}/{TODAY_DATE}/json/"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

file_name = output_folder + f"sample_{TODAY_DATE}-v1.json"

# For Excel making in project directory parameter :-
current_directory = os.getcwd()


def process_asset_df(input_asset_df):
    print("\n\nStarted processing the asset df ...")

    # Convert 'media_type' to lowercase in the input_asset_df
    print("Updating the media_type")
    input_asset_df['media_type'] = input_asset_df['media_type'].str.lower()

    # Apply quote function to 'source' preserving certain characters
    print("Updating the source")
    input_asset_df['source'] = input_asset_df['source'].apply(lambda url: quote(url, safe='/:?=&%'))

    # Separate rows into 'asset_df' and 'main_image_df' based on 'is_main_image'
    print("Partitioning the asset and main image df")
    asset_df = input_asset_df[input_asset_df['is_main_image'] != 1]
    main_image_df = input_asset_df[input_asset_df['is_main_image'] == 1]

    # Define the columns to include in the json_container
    columns_to_include = ['name', 'source', 'sha256', 'type', 'media_type']

    # Group and aggregate rows into the first dictionary for 'asset_df'
    print("Generating the final asset df")
    if len(asset_df):
        asset_df_grouped = asset_df.groupby('hash_key')[columns_to_include].apply(
            lambda group: group.to_dict('records') if not group.empty else []).reset_index(name='json_container')
    else:
        asset_df_grouped = pd.DataFrame([{'hash_key': None, 'json_container': None}])

    # Group and aggregate rows into the first dictionary for 'main_image_df'
    print("Generating the final main image df")
    if len(main_image_df):
        main_image_df_grouped = main_image_df.groupby('hash_key')[columns_to_include].apply(
            lambda group: group.to_dict('records')[0] if not group.empty else {}).reset_index(name='json_container')
    else:
        main_image_df_grouped = pd.DataFrame([{'hash_key': None, 'json_container': None}])

    # Rename columns
    asset_df_grouped = asset_df_grouped.rename(
        columns={'hash_key': 'hash_key', 'json_container': 'assets'}
    )
    main_image_df_grouped = main_image_df_grouped.rename(
        columns={'hash_key': 'hash_key', 'json_container': 'main_image'}
    )

    print("Asset DF processed ...\n\n")

    del input_asset_df, main_image_df, asset_df
    gc.collect()

    return asset_df_grouped, main_image_df_grouped


def process_pricing_df(input_price_df):
    print("\n\nStarted Processing the price df")
    # Step 1: Fill NaN and 0 values in 'min_qty' with 1, set data type to integer, and replace 0 with 1
    input_price_df['min_qty'] = input_price_df['min_qty'].fillna(1).astype(int)
    input_price_df['min_qty'] = input_price_df['min_qty'].replace(0, 1)
    input_price_df.sort_values(by=['min_qty'], inplace=True)

    # Step 2: Drop duplicate rows based on all columns
    print("Dropping duplicates from df is any.")
    input_price_df = input_price_df.drop_duplicates()

    # Step 3: Generate 'price_df' with 'hash_key' and 'json_container' containing specific columns
    print("Generating the final structure of price df")
    columns_to_include = ['min_qty', 'price', 'currency', 'price_string']
    price_df = input_price_df.groupby('hash_key')[columns_to_include].apply(
        lambda group: group.to_dict('records') if not group.empty else []
    ).reset_index(name='json_container')

    # step 4: Fill NaN values in price_string with ""
    input_price_df['price_string'] = input_price_df['price_string'].fillna("")

    # Step 5: Modify dictionaries in 'json_container' based on 'price_string'
    def modify_dict(record):
        if record['price_string']:
            record.pop('price', None)
            record.pop('currency', None)
        else:
            record.pop('price_string', None)
        return record

    print("Filtering value of price and price-string ")
    price_df['json_container'] = price_df['json_container'].apply(lambda records: [modify_dict(d) for d in records])

    # Rename columns
    price_df = price_df.rename(
        columns={'hash_key': 'hash_key', 'json_container': 'price'}
    )

    del input_price_df
    gc.collect()

    print("Price DF processed ...\n\n")
    return price_df


def make_excel(product_dataframe_final, error_type, vendor_name, column_name):
    # File path :-
    file_path = f'{current_directory}/{vendor_name}/{TODAY_DATE}/'
    if not os.path.exists(file_path):
        os.makedirs(file_path)

    # Create excel if dataframe has a data :-
    if len(product_dataframe_final) >= 1:
        if column_name in ['pdp_url', 'sku', 'name', 'category']:
            product_dataframe = product_dataframe_final[['pdp_url', 'sku', 'name', 'category']]
        else:
            product_dataframe = product_dataframe_final[['pdp_url', 'sku', 'name', 'category', column_name]]
        product_dataframe.sort_values(by=['sku'], inplace=True)
        writer = pd.ExcelWriter(
            f"{file_path}{error_type}.xlsx",
            engine='xlsxwriter',
            engine_kwargs={'options': {'strings_to_urls': False}}
        )
        writer.book.use_zip64()
        product_dataframe.to_excel(writer)
        writer.close()
        print(f'validation of {column_name} Failed.....')
    else:
        print(f'validation of {column_name} Done....')


def check_junk_character(product_dataframe, column_name, vendor_name):
    product_dataframe[f'{column_name}_junk'] = product_dataframe[column_name].astype(str).apply(html.unescape)
    junk_character_df = product_dataframe[f'{column_name}_junk'] != product_dataframe[column_name].astype(str)
    data = list()
    for key in junk_character_df.index:
        if junk_character_df[key]:
            data.append(product_dataframe.loc[key])
    final_df = pd.DataFrame(data)
    make_excel(product_dataframe_final=final_df, error_type=f'{column_name}_junk', vendor_name=vendor_name, column_name=column_name)


def check_spaces(product_space_dataframe, column_name, vendor_name):
    space_product_df = product_space_dataframe[column_name].str.contains(re.compile('  '))
    if len(product_df):
        data = list()
        indexes = [key[0] for key in zip(space_product_df.index, space_product_df) if key[1]]
        for main_index in indexes:
            data.append(product_space_dataframe.loc[main_index])
        space_final_df = pd.DataFrame(data)
        make_excel(product_dataframe_final=space_final_df, error_type=f'{column_name}_find_space', vendor_name=vendor_name,
                   column_name=column_name)


def data_validations(product_data):
    # Copy DataFrame :-
    product_dataframe = product_data.copy()
    # Vendor_name :-
    vendor_name = product_dataframe['vendor_name'][0]

    # Remove previous files :-
    current_directory = os.getcwd()
    TODAY_DATE = datetime.now().strftime('%Y-%m-%d')
    file_path = f'{current_directory}/{vendor_name}/{TODAY_DATE}/'
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    else:
        file_list = os.listdir(file_path)
        for file in file_list:
            os.remove(file_path + file)

    # Check Junk Character in some columns :-
    for column in ['name', 'manufacturer', 'attributes', 'features', 'description']:
        check_junk_character(product_dataframe=product_dataframe, column_name=column, vendor_name=vendor_name)

    # Check for Duplications skus:-
    sku_name_duplication_df = product_dataframe.groupby(['sku', 'name']).size() > 1
    sku_list = [key[0][0] for key in zip(sku_name_duplication_df.index, sku_name_duplication_df) if key[1]]
    sku_final_df = product_dataframe[product_dataframe['sku'].isin(sku_list)]
    make_excel(product_dataframe_final=sku_final_df, error_type=f'Duplication_sku_name', vendor_name=vendor_name, column_name='sku')

    # Check that anchor_tags in description :-
    description_df = product_dataframe[['sku', 'description']]
    product_df = description_df['description'].str.contains(re.compile('\<a.*?\>|\<\/a\>'))
    if len(product_df):
        indexes = [value for value in product_df.keys() if product_df[value] == True]
        sku_list = [product_dataframe['sku'][index] for index in indexes if not product_dataframe['sku'][index]]
        sku_final_df = product_dataframe[product_dataframe['sku'].isin(sku_list)]
        make_excel(product_dataframe_final=sku_final_df, error_type=f'description_anchor_tags', vendor_name=vendor_name, column_name='description')

    # Check Lead_time Format that array or not:-
    lead_time_df = product_dataframe
    lead_time_df['lead_time'] = lead_time_df['lead_time'].dropna()
    lead_time_df['lead_time'] = lead_time_df['lead_time'].dropna()
    # if len(lead_time_df):
    #     lead_time_df_index = [value[1] for value in zip(lead_time_df['lead_time'], lead_time_df.index) if not isinstance(value[0], list)]
    #     data = list()
    #     for main_index in lead_time_df_index:
    #         data.append(product_dataframe.iloc[main_index])
    #     lead_time_final_df = pd.DataFrame(data)
    #     make_excel(product_dataframe_final=lead_time_final_df, error_type=f'lead_time_format', vendor_name=vendor_name, column_name='lead_time')

    # Finds Two or more space in name:-
    for column in ['name', 'description', 'manufacturer']:
        check_spaces(product_space_dataframe=product_dataframe, column_name=column, vendor_name=vendor_name)

    # pdp_url format:-
    pdp_url_df = product_dataframe[['sku', 'pdp_url']]
    url_df = pdp_url_df['pdp_url'].str.contains(re.compile('^(https?:)[\.^\s\/$.?#].[^\s]*$'))
    if len(product_df):
        indexes = [value for value in url_df.keys() if not url_df[value]]
        if indexes:
            for main_index in indexes:
                data.append(product_dataframe.iloc[main_index])
            pdp_url_final_df = pd.DataFrame(data)
            make_excel(product_dataframe_final=pdp_url_final_df, error_type=f'pdp_url_find_space', vendor_name=vendor_name, column_name='pdp_url')

    # check for price_string has proper Call for price :-
    call_for_price_list = list()
    for sku, price in zip(product_dataframe['sku'], product_dataframe['price']):
        if price:
            if 'price_string' in price[0]:
                if price[0]['price_string'] != 'Call for price':
                    call_for_price_list.append(sku)
    if call_for_price_list:
        call_for_price_df = product_dataframe[product_dataframe['sku'].isin(call_for_price_list)]
        make_excel(product_dataframe_final=call_for_price_df, error_type=f'call_for_price_format', vendor_name=vendor_name, column_name='price')

    # Main_image url format check :-
    main_image_skus = list()
    for sku, main_image in zip(product_dataframe['sku'], product_dataframe['main_image']):
        if main_image:
            try:
                if re.findall('\.com\.', main_image['source']):
                    main_image_skus.append(sku)
            except:continue
    if main_image_skus:
        main_image_df = product_dataframe[product_dataframe['sku'].isin(main_image_skus)]
        make_excel(product_dataframe_final=main_image_df, error_type=f'main_image_url_format', vendor_name=vendor_name, column_name='main_image')

    # Assets url format check :-
    assets_skus = list()
    for sku, assets in zip(product_dataframe['sku'], product_dataframe['assets']):
        if assets:
            try:
                for image in assets:
                    if re.findall('\.com\.', image['source']):
                        assets_skus.append(sku)
            except:continue
    if assets_skus:
        assets_df = product_dataframe[product_dataframe['sku'].isin(assets_skus)]
        make_excel(product_dataframe_final=assets_df, error_type=f'assets_url_format', vendor_name=vendor_name, column_name='assets')

    # check for that file is available or not
    current_directory = os.getcwd()
    vendor_name = product_dataframe['vendor_name'][0]
    TODAY_DATE = datetime.now().strftime('%Y-%m-%d')
    file_path = f'{current_directory}/{vendor_name}/{TODAY_DATE}/'
    if os.listdir(file_path):
        print('File not validated.......')
        return False
    else:
        print('File Validation completed......')
        return True


# CREATING THE MYSQL OBJECT
con = pymysql.connect(host=db_host, user=db_user, password=db_password, db=db_name, port=3306)

print("READING THE PRICING TABLE", end="")
pricing_df = pd.read_sql(
    sql=(
        f"select `hash_key`, `sku`, `min_qty`, `price`, `price_string`, `currency` "
        f"from {pricing_table} where vendor_id = '{VENDOR_ID}'"
    ),
    con=con
)
# pricing_df = pd.read_json(location + "pricing_table.json", dtype={"hash_key": str, 'sku': str})
print("\rPRICING TABLE LOADED: ", len(pricing_df), " TOTAL ENTRIES")

print("READING THE ASSET TABLE", end="")
asset_df = pd.read_sql(
    sql=(
        f"select `hash_key`, `sku`, `name`, `source`, `sha256`, `type`, `media_type`, `length`, `file_name`, "
        f"`download_path`, `is_main_image` from {asset_table} where vendor_id = '{VENDOR_ID}' and status ='Done';"
    ),
    con=con
)
print("\rASSET TABLE LOADED: ", len(asset_df), " TOTAL ENTRIES")

print("READING THE PRODUCT TABLE", end="")
product_df = pd.read_sql(
    sql=(
        f"select `hash_key`, `vendor_name`, `sku`, `pdp_url`, `name`, `category`, `uom`, `sku_unit`, `sku_quantity`, "
        f"`quantity_increment`, `pack_label`, `available_to_checkout`, `in_stock`, `estimated_lead_time`, "
        f"`description`, `description_html`, `manufacturer`, `mpn`, `attributes`, `features`, `_scrape_metadata` "
        f"from {product_table} where vendor_id = '{VENDOR_ID}' and status='pending';"
    ),
    con=con
)
# product_df = pd.read_json(location + 'product_table_1.json', dtype={"hash_key": str, 'sku': str, 'mpn': str})
print("\rPRODUCTS TABLE LOADED: ", len(product_df), " TOTAL ENTRIES\n\n")

# PROCESSING THE PRICING TABLE
pricing_df = process_pricing_df(pricing_df)

# PROCESSING THE ASSET TABLE
asset_df = asset_df.drop_duplicates()
TOTAL_ASSETS = asset_df.length.count()
TOTAL_UNIQUE_ASSETS = len(asset_df.sha256.unique())
asset_df, main_image_df = process_asset_df(asset_df)

# MERGING THE PRICING DF WITH PRODUCT DF
print("PRICING MAPPING PROCESS STARTING ...")
product_df = product_df.merge(pricing_df[['hash_key', 'price']], on='hash_key', how='left')
print("\nPRICING MAPPING PROCESS ENDS ...\n\n")

# MERGING THE ASSET DF WITH PRODUCT DF
print("ASSETS MAPPING PROCESS STARTING ...")
product_df = product_df.merge(asset_df[['hash_key', 'assets']], on='hash_key', how='left')
print("\nASSETS MAPPING PROCESS ENDS ...\n\n")

# MERGING THE MAIN IMAGE DF WITH PRODUCT DF
print("MAIN IMAGE MAPPING PROCESS STARTING ...")
product_df = product_df.merge(main_image_df[['hash_key', 'main_image']], on='hash_key', how='left')
print("\nMAIN IMAGE MAPPING PROCESS ENDS ...\n\n")

# DELETING THE OBJECT THAT ARE NOT USEFUL TO BETTER MANGE MEMORY CONSUMPTION
del product_df['hash_key'], main_image_df, asset_df, pricing_df
gc.collect()

# FILLING THE NOT MATCHED VALUES WITH THE EMPTY LIST
print("\n\nPROCESSING THE EMPTY DATA FIELDS")
for i in ['assets', 'price']:
    product_df[i] = product_df[i].apply(lambda x: x if isinstance(x, list) else [])

product_df['estimated_lead_time'] = product_df['estimated_lead_time'].apply(
    lambda x: json.loads(x) if not isinstance(x, float) and x is not None else x)

product_df.rename(columns={"estimated_lead_time": "lead_time"}, inplace=True)

# FILLING THE NOT MATCHED VALUES WITH THE EMPTY LIST AND CONVERTING IT AS OBJECT
for i in ['attributes', '_scrape_metadata', 'category', 'features']:
    try:
        product_df[i] = product_df[i].fillna("[]")
        product_df[i] = product_df[i].apply(json.loads)
    except Exception as e:
        print(e, i)

# CONVERTING THE 0s AND 1s TO BOOLEAN VALUES true AND false
for i in ['in_stock', 'available_to_checkout']:
    product_df[i] = product_df[i].astype(bool)

# ENSURING THE ALL THE URL FILED ARE AS PER URL FORMAT
print("\n\nPROCESSING THE URLS")
product_df['pdp_url'] = product_df['pdp_url'].apply(lambda x: quote(x, safe='/:?=&%'))
product_df["_scrape_metadata"] = product_df["_scrape_metadata"].apply(
    lambda x: {
        **x,
        "date_visited": x['date_visited'] if len(x['date_visited']) == 24 else x['date_visited'][:-1] + ":00.000Z",
        "breadcrumbs": [{**d, "url": quote(d["url"], safe='/:?=&%')} for d in x["breadcrumbs"]],
        "url": quote(x['url'], safe='/:?=&%')
    }
)

print("\n\nDROPPING DUPLICATES FROM FINAL DATAFRAME IF ANY ")
# GENERATING THE CATEGORY_1 AS STRING TO USE IT AS DEDUPLICATION PROCESS.
product_df['category_1'] = product_df.category.apply(str)

# DROPPING DUPLICATES BASED ON THE SKU, PDP, NAME AND CATEGORY
# product_df = product_df.drop_duplicates(subset=['sku', 'pdp_url', 'name', 'category_1'])
product_df = product_df.drop_duplicates(subset=['sku','name'])

# REMOVING THE CATEGORY_1 AS NOT REQUIRED IN OUTPUT FILE
del product_df['category_1']

# SORTING THE DATA FRAME BASED ON SKU
product_df.sort_values(by=['sku'], inplace=True)

# junk character remove in all columns :-
def junk_changes(attributes):
    if isinstance(attributes, dict) and attributes and str(attributes) != 'nan':
        attr_dict =dict()
        for key in attributes:
            if attributes[key]:
                attr_dict[key] = html.unescape(attributes[key])
        return attr_dict
    elif attributes and str(attributes) != 'nan':
        attr_list = list()
        for dictionary in attributes:
            attr_dict = dict()
            for key in dictionary:
                if dictionary[key]:
                    attr_dict[key] = html.unescape(dictionary[key])
            attr_list.append(attr_dict)
        return attr_list
    else:
        return attributes

for i in ['attributes', 'features', 'main_image', 'assets']:
    product_df[i] = product_df[i].apply(junk_changes)

product_df = product_df.apply(lambda x: html.unescape(x) if isinstance(x, str) else x)

for key in product_df.keys():
    product_df[key] = product_df[key].apply(lambda x: re.sub('\s+', ' ', x) if isinstance(x, str) else x)
# remove same name and value in attributes :-
def remove_same_name_value(attributes):
    return [i for i in attributes if i['name'] != i['value']]

product_df['attributes'] = product_df['attributes'].apply(remove_same_name_value)

product_df['description'] = product_df['description'].apply(lambda x: html.unescape(x) if x else x)

validate = data_validations(product_data=product_df)

# GENERATING THE JSON FILE
print("\n\nGENERATING THE FILES.")
product_df.to_json(file_name, orient="records")
print("\n\nFILE GENERATED SUCCESSFULLY")

# VALIDATION CODE.
# validated = do_validation(file_name=file_name)
validated = True

# EXCEL FILE SIZE, NUMBER OF ROWS IN A SINGLE FILE, MAX 1000000 (1M)
size = 600000

if validated:
    k = product_df.shape[0]
    for i in range(int(k / size) + 1):
        df = product_df[size * i:size * (i + 1)]
        writer = pd.ExcelWriter(
            f"{output_part_files}/{TODAY_DATE}_PART_{str(i + 1).zfill(3)}.xlsx",
            engine='xlsxwriter',
            engine_kwargs={'options': {'strings_to_urls': False}}
        )
        writer.book.use_zip64()
        df.to_excel(writer)
        writer.close()

    print("\n\nTOTAL PRODUCTS: ", len(product_df))
    print("TOTAL ASSETS COUNT: ", TOTAL_ASSETS)
    print("TOTAL UNIQUE ASSETS: ", TOTAL_UNIQUE_ASSETS)

print(time.time() - t1)

if validate:
    print('File Validated Successfully....')
else:
    print('File not Validated please check on this path :- ')
