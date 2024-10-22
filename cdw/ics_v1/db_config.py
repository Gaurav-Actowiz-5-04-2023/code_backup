import datetime

date = datetime.datetime.now()
month = date.strftime('%B')

# DATABASE DETAILS
db_host = 'localhost'
db_user = 'root'
db_password = 'actowiz'
db_name = f'ics_master_db_v1_cdw_{month}'

asset_table = "asset_table"
product_table = "product_table"
pricing_table = "pricing_table"

# follow Procedures :-
category_sitemap_final = "category_sitemap_final"
sitemap_table_3 = "category_link_brand_sep"
sitemap_table_final = 'site_map_link_table'

Category_table = "category_sitemap_table"
sitemap_table = "site_map_link_table"
sitemap_table_2 = "Category_sitemap_final_sep"
