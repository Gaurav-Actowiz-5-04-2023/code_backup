import gc
import json
import os
import re
import time
import pymysql
import html
import pandas as pd
from datetime import datetime
from urllib.parse import quote
from validator import do_validation

# DATABASE DETAILS
db_host = '192.168.1.54'
db_user = 'root'
db_password = 'actowiz'
db_name = 'ics_iewc_june'

asset_table = "asset_table"
product_table = "product_table"
pricing_table = "pricing_table"

# DEFINING THE GLOBALS
VENDOR_ID = "ACT-B8-003"
TODAY_DATE = datetime.now().strftime('%Y-%m-%d')
OUTPUT_LOCATION = "D:/DATA/Gaurav/output_file/"

output_part_files = OUTPUT_LOCATION + f"{db_name}/{TODAY_DATE}/excel/"
if not os.path.exists(output_part_files):
    os.makedirs(output_part_files)

output_folder = OUTPUT_LOCATION + f"{db_name}/{TODAY_DATE}/json/"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

file_name = rf"\\192.168.1.223\File Server\ICS_QA\tequipment\2024-07-12\json\sample_2024-07-15-v1.json"

# For Excel making in project directory parameter :-
current_directory = os.getcwd()

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
            data.append(product_dataframe.iloc[key])
    final_df = pd.DataFrame(data)
    make_excel(product_dataframe_final=final_df, error_type=f'{column_name}_junk', vendor_name=vendor_name, column_name=column_name)


def check_spaces(product_space_dataframe, column_name, vendor_name):
    space_product_df = product_space_dataframe[column_name].str.contains(re.compile('  '))
    if len(product_df):
        data = list()
        indexes = [key[0] for key in zip(space_product_df.index, space_product_df) if key[1]]
        for main_index in indexes:
            data.append(product_space_dataframe.iloc[main_index])
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
    if len(lead_time_df):
        lead_time_df_index = [value[1] for value in zip(lead_time_df['lead_time'], lead_time_df.index) if not isinstance(value[0], list)]
        data = list()
        for main_index in lead_time_df_index:
            data.append(product_dataframe.iloc[main_index])
        lead_time_final_df = pd.DataFrame(data)
        make_excel(product_dataframe_final=lead_time_final_df, error_type=f'lead_time_format', vendor_name=vendor_name, column_name='lead_time')

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

product_df = pd.read_json(fr'\\192.168.1.223\File Server\ICS_QA\tequipment\2024-07-12\json\sample_2024-07-15-v1.json')
validate = data_validations(product_data=product_df)