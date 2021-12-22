# -*- coding: utf-8 -*-
"""
该网站每天更新一次 ip，每小时获取一个新 ip
"""
import random
import asyncio
# import sys
#
# sys.path.append("..")
import time

import aiohttp
from lxml import etree

# from db import aiomysql_op
from db import aioredis_op
from db.log import Logger

logger = Logger.get()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/86.0.4240.193 Safari/537.36"}


def get_url_list():
    return [f"https://www.kuaidaili.com/free/inha/{i}/" for i in range(1, 8)]


async def parse_url(url, session):
    # get/post(url,headers,params/data,proxy="http://ip:port")
    try:
        async with await session.get(url=url, headers=headers) as response:
            page_text = await response.text()
            return page_text
    except Exception as e:
        logger.error(f"错误:{e}")


async def parse(url, session):
    page_text = await parse_url(url, session)
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
    await save_to_redis(proxy_list)
    time.sleep(random.randint(1, 3))


# async def save_to_mysql(proxy_list):
#     for proxy in proxy_list:
#         r = await aiomysql_op.check(proxy)
#         if r:
#             proxy_list.remove(proxy)
#     await aiomysql_op.insert_many(proxy_list)

async def save_to_redis(proxy_list):
    for proxy in proxy_list:
        await aioredis_op.add(proxy)


async def run(session):
    url_list = get_url_list()
    tasks = []  # 多任务列表
    # 1.创建协程对象
    for url in url_list:
        logger.info(f"快代理...{url}")
        c = parse(url, session)
        # 2.创建任务对象
        task = asyncio.ensure_future(c)
        tasks.append(task)
    logger.info("快代理已获取")

