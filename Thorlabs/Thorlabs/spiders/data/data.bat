taskkill /f /im scrapy.exe
start "ics_master_db_v1_thorlabs_October_1" scrapy crawl thorlabs_data_m -a start=1 -a end=1573
start "ics_master_db_v1_thorlabs_October_2" scrapy crawl thorlabs_data_m -a start=1573 -a end=3030
start "ics_master_db_v1_thorlabs_October_3" scrapy crawl thorlabs_data_m -a start=3030 -a end=4340
start "ics_master_db_v1_thorlabs_October_4" scrapy crawl thorlabs_data_m -a start=4340 -a end=5565
start "ics_master_db_v1_thorlabs_October_5" scrapy crawl thorlabs_data_m -a start=5565 -a end=6930
timeout /t 30
start "ics_master_db_v1_thorlabs_October_6" scrapy crawl thorlabs_data_m -a start=6930 -a end=8347
start "ics_master_db_v1_thorlabs_October_7" scrapy crawl thorlabs_data_m -a start=8347 -a end=9904
start "ics_master_db_v1_thorlabs_October_8" scrapy crawl thorlabs_data_m -a start=9904 -a end=11174
start "ics_master_db_v1_thorlabs_October_9" scrapy crawl thorlabs_data_m -a start=11174 -a end=12451
start "ics_master_db_v1_thorlabs_October_10" scrapy crawl thorlabs_data_m -a start=12451 -a end=14867
timeout /t 30
start "ics_master_db_v1_thorlabs_October_11" scrapy crawl thorlabs_data_m -a start=14867 -a end=16519
start "ics_master_db_v1_thorlabs_October_12" scrapy crawl thorlabs_data_m -a start=16519 -a end=17672
start "ics_master_db_v1_thorlabs_October_13" scrapy crawl thorlabs_data_m -a start=17672 -a end=18771
start "ics_master_db_v1_thorlabs_October_14" scrapy crawl thorlabs_data_m -a start=18771 -a end=19862
start "ics_master_db_v1_thorlabs_October_15" scrapy crawl thorlabs_data_m -a start=19862 -a end=20960
timeout /t 30
start "ics_master_db_v1_thorlabs_October_16" scrapy crawl thorlabs_data_m -a start=20960 -a end=22941
start "ics_master_db_v1_thorlabs_October_17" scrapy crawl thorlabs_data_m -a start=22941 -a end=24048
start "ics_master_db_v1_thorlabs_October_18" scrapy crawl thorlabs_data_m -a start=24048 -a end=25139
start "ics_master_db_v1_thorlabs_October_19" scrapy crawl thorlabs_data_m -a start=25139 -a end=26230
start "ics_master_db_v1_thorlabs_October_20" scrapy crawl thorlabs_data_m -a start=26230 -a end=60153