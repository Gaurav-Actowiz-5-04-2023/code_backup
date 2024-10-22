import os
import json
import pymysql
import pandas as pd

file_path = 'Y:/Gaurav/ICS_QA/Thorlab/2024-01-05/json'

conn = pymysql.connect(host='localhost', user='root', password='actowiz', database='ics_master_db_v1_Thorlabs', autocommit=True)
cursor = conn.cursor()

for file_directory, folder_name, files in os.walk(file_path):
    for file in files:
        Directory = file_directory+'/'+file
        file_data = open(Directory, 'r').read()
        attr_df = pd.read_json(Directory)

        try:
            select_query = f"select pdp_url from product_table"
            cursor.execute(select_query)
            print("query execute successfully")
        except Exception as error:
            print(error)

        link_list = list()
        for link in cursor.fetchall():
            link_list.append(link[0])

        for links in attr_df['pdp_url']:
            if links not in link_list:
                index = attr_df.query(f"pdp_url=='{links}'")['_scrape_metadata'].keys()[0]
                meta_data = json.dumps(attr_df['_scrape_metadata'][index]['breadcrumbs'][1:])
                try:
                    insert_query = (f"insert into site_map_link_table (vendor_name, vendor_id, product_urls, meta_data) "
                                    f"values ('Thorlabs', 'ACT-B1-002', '{links}', '{meta_data}')")
                    print(insert_query)
                    cursor.execute(insert_query)
                    conn.commit()
                    print("Link inserted successfully")
                except Exception as error:
                    print(error)


