taskkill /f /im scrapy.exe
start "ics_master_db_v1_thorlabs_August_1" scrapy crawl download_assest -a vendor_id=ACT-B1-002 -a start=5896733 -a end=6128935
start "ics_master_db_v1_thorlabs_August_2" scrapy crawl download_assest -a vendor_id=ACT-B1-002 -a start=6128935 -a end=6129232
start "ics_master_db_v1_thorlabs_August_3" scrapy crawl download_assest -a vendor_id=ACT-B1-002 -a start=6129232 -a end=6129529
start "ics_master_db_v1_thorlabs_August_4" scrapy crawl download_assest -a vendor_id=ACT-B1-002 -a start=6129529 -a end=6129826
start "ics_master_db_v1_thorlabs_August_5" scrapy crawl download_assest -a vendor_id=ACT-B1-002 -a start=6129826 -a end=6130123
timeout /t 30
start "ics_master_db_v1_thorlabs_August_6" scrapy crawl download_assest -a vendor_id=ACT-B1-002 -a start=6130123 -a end=6130420
start "ics_master_db_v1_thorlabs_August_7" scrapy crawl download_assest -a vendor_id=ACT-B1-002 -a start=6130420 -a end=6130717
start "ics_master_db_v1_thorlabs_August_8" scrapy crawl download_assest -a vendor_id=ACT-B1-002 -a start=6130717 -a end=6131014
start "ics_master_db_v1_thorlabs_August_9" scrapy crawl download_assest -a vendor_id=ACT-B1-002 -a start=6131014 -a end=6131311
start "ics_master_db_v1_thorlabs_August_10" scrapy crawl download_assest -a vendor_id=ACT-B1-002 -a start=6131311 -a end=6131608
timeout /t 30
start "ics_master_db_v1_thorlabs_August_11" scrapy crawl download_assest -a vendor_id=ACT-B1-002 -a start=6131608 -a end=6131905
start "ics_master_db_v1_thorlabs_August_12" scrapy crawl download_assest -a vendor_id=ACT-B1-002 -a start=6131905 -a end=6132202
start "ics_master_db_v1_thorlabs_August_13" scrapy crawl download_assest -a vendor_id=ACT-B1-002 -a start=6132202 -a end=6132499
start "ics_master_db_v1_thorlabs_August_14" scrapy crawl download_assest -a vendor_id=ACT-B1-002 -a start=6132499 -a end=6132796
start "ics_master_db_v1_thorlabs_August_15" scrapy crawl download_assest -a vendor_id=ACT-B1-002 -a start=6132796 -a end=6133093
timeout /t 30
start "ics_master_db_v1_thorlabs_August_16" scrapy crawl download_assest -a vendor_id=ACT-B1-002 -a start=6133093 -a end=6133390
start "ics_master_db_v1_thorlabs_August_17" scrapy crawl download_assest -a vendor_id=ACT-B1-002 -a start=6133390 -a end=6133687
start "ics_master_db_v1_thorlabs_August_18" scrapy crawl download_assest -a vendor_id=ACT-B1-002 -a start=6133687 -a end=6133984
start "ics_master_db_v1_thorlabs_August_19" scrapy crawl download_assest -a vendor_id=ACT-B1-002 -a start=6133984 -a end=6134281
start "ics_master_db_v1_thorlabs_August_20" scrapy crawl download_assest -a vendor_id=ACT-B1-002 -a start=6134281 -a end=6134578