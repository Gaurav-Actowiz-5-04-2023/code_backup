taskkill /f /im scrapy.exe
taskkill /f /im python.exe
start "ics_master_db_v1_cdw_October_1" scrapy crawl download_assest -a vendor_id=ACT-B3-010 -a start=2445683 -a end=2462731
start "ics_master_db_v1_cdw_October_2" scrapy crawl download_assest -a vendor_id=ACT-B3-010 -a start=2462731 -a end=2479510
start "ics_master_db_v1_cdw_October_3" scrapy crawl download_assest -a vendor_id=ACT-B3-010 -a start=2479510 -a end=2488668
start "ics_master_db_v1_cdw_October_4" scrapy crawl download_assest -a vendor_id=ACT-B3-010 -a start=2488668 -a end=2520218
start "ics_master_db_v1_cdw_October_5" scrapy crawl download_assest -a vendor_id=ACT-B3-010 -a start=2520218 -a end=2529711
timeout /t 30
start "ics_master_db_v1_cdw_October_6" scrapy crawl download_assest -a vendor_id=ACT-B3-010 -a start=2529711 -a end=2531437
start "ics_master_db_v1_cdw_October_7" scrapy crawl download_assest -a vendor_id=ACT-B3-010 -a start=2531437 -a end=2535122
start "ics_master_db_v1_cdw_October_8" scrapy crawl download_assest -a vendor_id=ACT-B3-010 -a start=2535122 -a end=2549301
start "ics_master_db_v1_cdw_October_9" scrapy crawl download_assest -a vendor_id=ACT-B3-010 -a start=2549301 -a end=2573931
start "ics_master_db_v1_cdw_October_10" scrapy crawl download_assest -a vendor_id=ACT-B3-010 -a start=2573931 -a end=2629072