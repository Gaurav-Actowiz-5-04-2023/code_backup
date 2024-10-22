import pymysql
import db_config as db
from datetime import datetime


class DatabaseMake:
    def __init__(self):
        # DATABASE CONNECTION
        self.con = pymysql.connect(host=db.db_host, user=db.db_user, password=db.db_password, db=db.db_name)
        self.cursor = self.con.cursor()
        # Month :-
        date = datetime.now()
        self.month = date.strftime('%B')

    def database_make(self):
        query = f'''CREATE DATABASE  IF NOT EXISTS `ics_master_db_v1_cdw_{self.month}` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;'''
        self.cursor.execute(query)
        self.con.commit()

    def table_maker(self):
        query_make = open('E:\DATA\gaurav\Projects\cdw\category\ics_master_db_v1_cdw_march_category_sitemap_final.sql', 'r').read()
        try:
            self.cursor.execute(query_make)
            self.con.commit()
        except Exception as e:
            print(e)


if __name__ == '__main__':
    class_object = DatabaseMake()
    class_object.table_maker()