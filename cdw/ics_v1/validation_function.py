import os.path
import re
import html
import pandas as pd
from datetime import datetime

def make_excel(skus, product_dataframe, error):
    vendor_name = product_dataframe['vendor_name'][0]
    current_directory = os.getcwd()
    TODAY_DATE = datetime.now().strftime('%Y-%m-%d')
    file_path = f'{current_directory}/{vendor_name}/{TODAY_DATE}/'
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    if skus:
        final_dataframe = product_dataframe[product_dataframe['sku'].isin(skus)]
        final_dataframe = final_dataframe[['pdp_url', 'sku', 'name', 'category']]
        final_dataframe.sort_values(by=['sku'], inplace=True)
        writer = pd.ExcelWriter(
            f"{file_path}{error}.xlsx",
            engine='xlsxwriter',
            engine_kwargs={'options': {'strings_to_urls': False}}
        )
        writer.book.use_zip64()
        final_dataframe.to_excel(writer)
        writer.close()


def data_validations(product_data):

    product_dataframe = product_data
    # Check for Duplications skus:-
    df_no_duplicates = product_dataframe
    new_df = df_no_duplicates.groupby(['sku', 'name']).size() > 1
    duplicates_sku = new_df[new_df == True]
    skus = [key for key in duplicates_sku.keys()]
    make_excel(skus, product_dataframe, error='sku_duplicates')

    # Check for html tags or links in description :-
    description_df = product_dataframe[['sku', 'description']]
    product_df = description_df['description'].str.contains(re.compile('\<a\>|https:'))
    if len(product_df):
        indexes = [value for value in product_df.keys() if not product_df[value]]
        skus = [product_dataframe['sku'][index] for index in indexes if not product_dataframe['sku'][index]]
        make_excel(skus, product_dataframe, error='description_html_tag_found')

    product_dataframe['description_tags'] = product_dataframe['description'].apply(lambda x: html.unescape(x) if x else x)
    product_dataframe['description_length'] = product_dataframe['description'].apply(lambda x: len(x) if x else x)
    product_dataframe['description_tags_length'] = product_dataframe['description_tags'].apply(lambda x: len(x) if x else x)

    new_df = product_dataframe[['sku', 'description', 'description_length', 'description_tags_length']]
    new_df['description'].dropna()
    product_df = new_df[new_df['description_length'] != new_df['description_tags_length']]
    product_df['description'].dropna()
    if len(product_df['description'].dropna()):
        skus = [value for value in product_df['sku'] if value]
        make_excel(skus, product_dataframe, error='description_html_character')

    # Check Lead_time Format that array or not:-
    lead_time_df = product_dataframe.dropna()
    if len(lead_time_df):
        if isinstance(lead_time_df['lead_time'][0],  list):
            skus = [value for value in lead_time_df['lead_time'] if isinstance(value,  list)]
            make_excel(skus, product_dataframe, error='lead_time_format_wrong')

    # Check for Junk Character in name :-
    product_dataframe['name_tags'] = product_dataframe['name'].apply(lambda x: html.unescape(x) if x else x)
    product_dataframe['name_length'] = product_dataframe['name'].apply(lambda x: len(x) if x else x)
    product_dataframe['name_tags_length'] = product_dataframe['name_tags'].apply(lambda x: len(x) if x else x)

    new_df = product_dataframe[['sku', 'name', 'name_length', 'name_tags_length']]
    new_df['name'].dropna()
    product_df = new_df[new_df['name_length'] != new_df['name_tags_length']]
    product_df['name'].dropna()
    if len(product_df['name']):
        skus = [value for value in product_df['sku'] if value]
        make_excel(skus, product_dataframe, error='name_junk_character')

    # Finds Two or more space in name:-
    name_space_df = product_dataframe[['sku', 'name', 'name_length', 'name_tags_length']]
    product_df = name_space_df['name'].str.contains(re.compile('  '))
    if len(product_df):
        indexes = [value for value in product_df.keys() if product_df[value]]
        skus = [product_dataframe['sku'][index] for index in indexes if product_dataframe['sku'][index]]
        make_excel(skus, product_dataframe, error='name_space')

    # pdp_url format and www is present in url :-
    pdp_url_df = product_dataframe[['sku', 'pdp_url']]
    product_df = pdp_url_df['pdp_url'].str.contains(re.compile('^(https?:\/\/)[\.^\s\/$.?#].[^\s]*$'))
    if len(product_df):
        indexes = [value for value in product_df.keys() if not product_df[value]]
        skus = [product_dataframe['sku'][index] for index in indexes if not product_dataframe['sku'][index]]
        make_excel(skus, product_dataframe, error='pdp_url_format')

    # check for price_string has proper Call for price :-
    skus = list()
    for sku, price in zip(product_dataframe['sku'], product_dataframe['price']):
        if price:
            if 'price_string' in price[0]:
                if price[0]['price_string'] != 'Call for price':
                    skus.append(sku)
    if skus:
        make_excel(skus, product_dataframe, error='call_for_price_format')

    # Main_image url format check :-
    skus = list()
    for sku, main_image in zip(product_dataframe['sku'], product_dataframe['main_image']):
        if main_image:
            try:
                if re.findall('com\.', main_image['source']):
                    skus.append(sku)
            except:continue

    # Assets url format check :-
    for sku, assets in zip(product_dataframe['sku'], product_dataframe['assets']):
        if assets:
            try:
                for image in assets:
                    if re.findall('com\.', image['source']):
                        skus.append(sku)
            except:continue
    if skus:
        make_excel(skus, product_dataframe, error='Assets_source_format')

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
        for key in ['description_length', 'description_tags', 'description_tags_length', 'name_length', 'name_tags', 'name_tags_length']:
            del product_dataframe[key]
        return True


if __name__ == '__main__':
    # Information about Projects :-
    product_df = pd.read_json(r'\\192.168.1.223\File Server\ICS_QA\jefco_Manufacturing\2024-02-08\json\2024-02-11-v1.json')
    data_validations(product_df)

# import os.path
# import re
# import html
# import pandas as pd
# from datetime import datetime
#
#
# def make_excel(skus, product_dataframe, error):
#     vendor_name = product_dataframe['vendor_name'][0]
#     current_directory = os.getcwd()
#     TODAY_DATE = datetime.now().strftime('%Y-%m-%d')
#     file_path = f'{current_directory}/{vendor_name}/{TODAY_DATE}/'
#     if not os.path.exists(file_path):
#         os.makedirs(file_path)
#     if skus:
#         final_dataframe = product_dataframe[product_dataframe['sku'].isin(skus)]
#         if error == 'call_for_price_format':
#             final_dataframe = final_dataframe[['pdp_url', 'sku', 'name', 'category', 'price']]
#         else:
#             final_dataframe = final_dataframe[['pdp_url', 'sku', 'name', 'category']]
#         final_dataframe.sort_values(by=['sku'], inplace=True)
#         writer = pd.ExcelWriter(
#             f"{file_path}{error}.xlsx",
#             engine='xlsxwriter',
#             engine_kwargs={'options': {'strings_to_urls': False}}
#         )
#         writer.book.use_zip64()
#         final_dataframe.to_excel(writer)
#         writer.close()
#
#
# def data_validations(product_data):
#     product_dataframe = product_data
#     # Check for Duplications :-
#     df_no_duplicates = product_dataframe.drop_duplicates(subset=['sku', 'pdp_url'])
#     new_df = df_no_duplicates.groupby(['sku']).size() > 1
#     duplicates_sku = new_df[new_df == True]
#     skus = [key for key in duplicates_sku.keys()]
#     make_excel(skus, product_dataframe, error='sku_duplicates')
#
#     # Check for html tags in description :-
#     product_dataframe['description_tags'] = product_dataframe['description'].apply(lambda x: html.unescape(x) if x else x)
#     product_dataframe['description_length'] = product_dataframe['description'].apply(lambda x: len(x) if x else x)
#     product_dataframe['description_tags_length'] = product_dataframe['description_tags'].apply(lambda x: len(x) if x else x)
#
#     new_df = product_dataframe[['sku', 'description', 'description_length', 'description_tags_length']]
#     new_df['description'].dropna()
#     product_df = new_df[new_df['description_length'] != new_df['description_tags_length']]
#     product_df['description'].dropna()
#     if len(product_df['description'].dropna()):
#         skus = [value for value in product_df['sku'] if value]
#         make_excel(skus, product_dataframe, error='description_html_character')
#
#     # Check Lead_time Format that array or not:-
#     lead_time_df = product_dataframe.dropna()
#     if len(lead_time_df):
#         if isinstance(lead_time_df['lead_time'][0],  list):
#             skus = [value for value in lead_time_df['lead_time'] if isinstance(value,  list)]
#             make_excel(skus, product_dataframe, error='lead_time_format_wrong')
#
#     # Check for Junk Character in name :-
#     product_dataframe['name_tags'] = product_dataframe['name'].apply(lambda x: html.unescape(x) if x else x)
#     product_dataframe['name_length'] = product_dataframe['name'].apply(lambda x: len(x) if x else x)
#     product_dataframe['name_tags_length'] = product_dataframe['name_tags'].apply(lambda x: len(x) if x else x)
#
#     new_df = product_dataframe[['sku', 'name', 'name_length', 'name_tags_length']]
#     new_df['name'].dropna()
#     product_df = new_df[new_df['name_length'] != new_df['name_tags_length']]
#     product_df['name'].dropna()
#     if len(product_df['name']):
#         skus = [value for value in product_df['sku'] if value]
#         make_excel(skus, product_dataframe, error='name_junk_character')
#
#     # Finds Two or more space in name:-
#     name_space_df = product_dataframe[['sku', 'name', 'name_length', 'name_tags_length']]
#     product_df = name_space_df['name'].str.contains(re.compile('  '))
#     if len(product_df):
#         indexes = [value for value in product_df.keys() if product_df[value]]
#         skus = [product_dataframe['sku'][index] for index in indexes if product_dataframe['sku'][index]]
#         make_excel(skus, product_dataframe, error='name_space')
#
#     # pdp_url format and www is present in url :-
#     pdp_url_df = product_dataframe[['sku', 'pdp_url']]
#     product_df = pdp_url_df['pdp_url'].str.contains(re.compile('^(https?:\/\/www)[\.^\s\/$.?#].[^\s]*$'))
#     if len(product_df):
#         indexes = [value for value in product_df.keys() if not product_df[value]]
#         skus = [product_dataframe['sku'][index] for index in indexes if product_dataframe['sku'][index]]
#         make_excel(skus, product_dataframe, error='pdp_url_format')
#
#     # check for price_string has proper Call for price:-
#     skus = list()
#     for sku, price in zip(product_dataframe['sku'], product_dataframe['price']):
#         if price:
#             if 'price_string' in price[0]:
#                 if price[0]['price_string'] != 'Call for price':
#                     skus.append(sku)
#     if skus:
#         make_excel(skus, product_dataframe, error='call_for_price_format')
#
#     current_directory = os.getcwd()
#     vendor_name = product_dataframe['vendor_name'][0]
#     TODAY_DATE = datetime.now().strftime('%Y-%m-%d')
#     file_path = f'{current_directory}/{vendor_name}/{TODAY_DATE}/'
#     if os.listdir(file_path):
#         print('File not validated.......')
#         return False
#     else:
#         print('File Validation completed......')
#         for key in ['description_length', 'description_tags', 'description_tags_length', 'name_length', 'name_tags', 'name_tags_length']:
#             del product_dataframe[key]
#         return True
#
#
# if __name__ == '__main__':
#     # Information about Projects :-
#     product_df = pd.read_json('E:\ProjectICS\Output_file\ics_master_db_v1_cdw\2024-03-06\json\sample_2024-03-06-v1.json')
#     data_validations(product_df)
