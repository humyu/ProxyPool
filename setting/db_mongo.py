# -*- coding: utf-8 -*-
import pymongo
from setting import db_setting


class DBMongo:
    def __init__(self):
        # self.mongo_uri = db_setting.MONGO_URI
        # self.mongo_db = db_setting.MONGO_DB
        self.client = pymongo.MongoClient(db_setting.MONGO_URI)
        self.db = self.client[db_setting.MONGO_DB]

    def close_spider(self):
        self.client.close()

    def insert_one(self, item):
        self.db[db_setting.MONGO_COLLECTION].insert(dict(item))
        # return item
