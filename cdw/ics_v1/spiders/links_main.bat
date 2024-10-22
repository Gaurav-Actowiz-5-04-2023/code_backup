taskkill /f /im scrapy.exe
taskkill /f /im python.exe
start "ics_master_db_v1_cdw_June_1" scrapy crawl links_main -a start=49 -a end=2698
start "ics_master_db_v1_cdw_June_2" scrapy crawl links_main -a start=2698 -a end=4429
start "ics_master_db_v1_cdw_June_3" scrapy crawl links_main -a start=4429 -a end=6277
start "ics_master_db_v1_cdw_June_4" scrapy crawl links_main -a start=6277 -a end=9624
start "ics_master_db_v1_cdw_June_5" scrapy crawl links_main -a start=9624 -a end=11211
timeout /t 60
start "ics_master_db_v1_cdw_June_6" scrapy crawl links_main -a start=11211 -a end=13275
start "ics_master_db_v1_cdw_June_7" scrapy crawl links_main -a start=13275 -a end=15415
start "ics_master_db_v1_cdw_June_8" scrapy crawl links_main -a start=15415 -a end=16980
start "ics_master_db_v1_cdw_June_9" scrapy crawl links_main -a start=16980 -a end=18579
start "ics_master_db_v1_cdw_June_10" scrapy crawl links_main -a start=18579 -a end=18827