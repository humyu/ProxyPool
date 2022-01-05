# -*- coding: utf-8 -*-
import aiohttp


class WebSession(object):
    session = None

    @classmethod
    def create(cls):
        cls.session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=20, ssl=False))
        return cls.session

    @classmethod
    def close(cls):
        if cls.session is not None:
            return cls.session.close()
