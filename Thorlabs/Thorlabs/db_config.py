import datetime

date = datetime.datetime.now()
month = date.strftime('%B')

# DATABASE DETAILS
db_host = "localhost"
db_user = "root"
db_password = "actowiz"
db_name = f"ics_master_db_v1_thorlabs_{month}"

asset_table = "asset_table"
product_table = "product_table"
sitemap_table = "site_map_link_table"
pricing_table = "pricing_table"
