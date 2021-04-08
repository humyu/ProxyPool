# -*- coding: utf-8 -*-
import pymysql
from setting import db_setting


class DBMysql:
    def __init__(self):
        self.host = db_setting.MYSQL_HOST
        self.database = db_setting.MYSQL_DATABASE
        self.user = db_setting.MYSQL_USER
        self.password = db_setting.MYSQL_PASSWORD
        self.port = db_setting.MYSQL_PORT
        self.table = db_setting.MYSQL_TABLE
        self.db = pymysql.connect(self.host, self.user, self.password, self.database, charset='utf8', port=self.port)
        self.cursor = self.db.cursor()

    def close_spider(self):
        self.db.close()

    def insert_one(self, item):
        data = dict(item)
        keys = ', '.join(data.keys())
        values = ', '.join(['% s'] * len(data))
        sql = 'insert into % s (% s) values (% s)' % (self.table, keys, values)
        self.cursor.execute(sql, tuple(data.values()))
        self.db.commit()

    def insert_many(self, item_list):
        tuple_list = [(item,5,0) for item in item_list]
        sql = 'insert into t_proxy (ip,score,times) values (% s, % s, % s)'
        self.cursor.executemany(sql, tuple_list)
        self.db.commit()

    def get_all(self):
        sql = 'select distinct ip,score from % s where score > 0' % self.table
        self.cursor.execute(sql)
        self.db.commit()
        # 返回多个元组
        fetch_list = list(self.cursor.fetchall())
        results = [{"ip":i[0],"score":i[1]} for i in fetch_list]
        return results

    def delete_one(self, item):
        param = item["ip"]
        sql = 'delete from % s where ip = % s' % (self.table, '% s')
        self.cursor.execute(sql, param)
        self.db.commit()

    def delete_useless(self):
        sql = 'delete from % s where score <= 0' % self.table
        self.cursor.execute(sql)
        self.db.commit()

    def update_score(self, item):
        data = dict(item)
        sql = 'update % s set score = %s where ip = %s' % (self.table, '%s', '%s')
        param = list(data.values())
        param.reverse()
        self.cursor.execute(sql, param)
        self.db.commit()
