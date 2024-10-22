# import hashlib
#
# import pymysql as sql
# import pymongo as mongo
#
#
# class ConfigDatabase():
#
#
#     def __init__(self, database, table, host = "192.168.1.23", user = "root", password = "actowiz", type1 = "sql"):
#
#         self.host = host
#         self.user = user
#         self.password = password
#         self.database = database
#         self.table = table
#         self.con1 = sql.connect(host=self.host, user=self.user, password=self.password)
#         self.con1.cursor().execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
#         self.connSql = sql.connect(
#             host = self.host,
#             user = self.user,
#             passwd = self.password,
#             database = self.database
#         )
#         self.connSql.cursor().execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
#         if type1 == 'mongo':
#             self.connMongo = mongo.MongoClient(f"mongodb://{host}:27017/")
#             self.dbmongo = self.connMongo[self.database]
#         self.crsrSql = self.connSql.cursor(sql.cursors.DictCursor)
#
#     def hash_generate(self, fields):
#         hashid = int(hashlib.md5(bytes("".join(fields), "utf8")).hexdigest(), 16) % (10 ** 30)
#         return hashid
#
#     def fetchResultsfromSql(self, fields = [], conditions = {} ,start=0, end=1):
#
#         fieldtofetch = ",".join(fields) if fields else "*"
#         cond = [f"`{key}`='{value}'" for key,value in conditions.items() if conditions]
#         cond = f'where {",".join(cond)} ' if cond else ""
#         self.crsrSql.execute(f"select {fieldtofetch} from {self.table} {cond} limit {start},{end}")
#         # self.crsrSql.execute(f"select {fieldtofetch} from {self.table} {cond} and Id BETWEEN {start} AND {end}")
#         results = self.crsrSql.fetchall()
#         return results
#
#
#     def insertItemToSql(self, item):
#
#         try:
#             field_list = []
#             value_list = []
#             for field in item:
#                 field_list.append(str(field))
#                 value_list.append(str(item[field]).replace("'", "’"))
#             fields = ','.join(field_list)
#             values = "','".join(value_list)
#             insert_db = f"insert into {self.table}" + "( " + fields + " ) values ( '" + values + "' )"
#             self.crsrSql.execute(insert_db)
#             self.connSql.commit()
#             print(f"Item Successfully Inserted...")
#         except Exception as e:
#             print(str(e))
#
#
#     def insertItemToMongo(self, item):
#
#         try:
#             self.dbmongo[self.table].insert_one(item)
#         except Exception as e:
#             print(e)
#
#
#     def updateStatusSql(self, item,):
#
#         try:
#             update = f"update {self.table} set status='done' where cat = '{item['StoreId']}'"
#             self.crsrSql.execute(update)
#             self.connSql.commit()
#         except Exception as e:
#             print(e)