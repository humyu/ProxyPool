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

    def insert(self, item):
        data = dict(item)
        keys = ', '.join(data.keys())
        values = ', '.join(['% s'] * len(data))
        sql = 'insert into % s (% s) values (% s)' % (self.table, keys, values)
        self.cursor.execute(sql, tuple(data.values()))
        self.db.commit()

    def get(self):
        sql = 'select proxy from % s' % self.table
        self.cursor.execute(sql)
        self.db.commit()
        # 返回多个元组
        fetch_list = list(self.cursor.fetchall())
        results = ["".join(i) for i in fetch_list]
        return results

    def delete(self, item):
        sql = 'delete from % s where proxy = % s' % (self.table, '% s')
        self.cursor.execute(sql, item)
        self.db.commit()

    def delete_all(self):
        sql = 'delete from % s ' % self.table
        self.cursor.execute(sql)
        self.db.commit()
