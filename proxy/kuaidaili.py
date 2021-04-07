# -*- coding: utf-8 -*-
import aiohttp
import time
import random
from lxml import etree
import sys

sys.path.append("..")
from setting.db_mysql import DBMysql
from setting.log import Logger

db_mysql = DBMysql()
logger = Logger.get()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/86.0.4240.193 Safari/537.36"}


def get_url_list():
    return [f"https://www.kuaidaili.com/free/inha/{i}/" for i in range(1, 5)]


async def parse_url(url):
    async with aiohttp.ClientSession() as sess:  # 实例化一个请求对象
        # get/post(url,headers,params/data,proxy="http://ip:port")
        try:
            async with await sess.get(url=url, headers=headers) as response:  # 使用get发起请求，返回一个相应对象
                page_text = await response.text()  # text()获取字符串形式的相应数据  read()获取byte类型的响应数据
                return page_text
        except Exception as e:
            logger.error(f"错误:{e}")


async def parse():
    logger.warning("获取快代理...")
    url_list = get_url_list()
    for url in url_list:
        page_text = await parse_url(url)
        tree = etree.HTML(page_text)
        tr_list = tree.xpath("//div[@id='list']/table/tbody/tr")
        proxy_list = []
        for tr in tr_list:
            ip = tr.xpath("./td[@data-title='IP']/text()")
            ip = ip[0].strip()
            port = tr.xpath("./td[@data-title='PORT']/text()")
            port = port[0].strip()
            proxy = ip + ":" + port
            proxy_list.append(proxy.replace(",", ""))
        await save_to_mysql(proxy_list)
        time.sleep(random.randint(1,3))
    logger.warning("获取快代理完毕!")


async def save_to_mysql(proxy_list):
    for proxy in proxy_list:
        item = {"proxy": proxy}
        db_mysql.insert_one(item)


