taskkill /f /im scrapy.exe
taskkill /f /im python.exe
start "ics_master_db_v1_cdw_1" scrapy crawl links_brand -a start=1 -a end=25
start "ics_master_db_v1_cdw_2" scrapy crawl links_brand -a start=26 -a end=50
start "ics_master_db_v1_cdw_3" scrapy crawl links_brand -a start=51 -a end=75
start "ics_master_db_v1_cdw_4" scrapy crawl links_brand -a start=76 -a end=100
start "ics_master_db_v1_cdw_5" scrapy crawl links_brand -a start=101 -a end=125
timeout /t 60
start "ics_master_db_v1_cdw_6" scrapy crawl links_brand -a start=126 -a end=150
start "ics_master_db_v1_cdw_7" scrapy crawl links_brand -a start=151 -a end=175
start "ics_master_db_v1_cdw_8" scrapy crawl links_brand -a start=176 -a end=200
start "ics_master_db_v1_cdw_9" scrapy crawl links_brand -a start=201 -a end=226