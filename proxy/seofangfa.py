# -*- coding: utf-8 -*-
"""
https://proxy.seofangfa.com/
该网站大概每十分钟更新一次
"""
import asyncio
import random
import sys

sys.path.append("..")
from lxml import etree

from db import aioredis_op
from db.log import Logger

logger = Logger.get()

headers = {
    ':authority': 'proxy.seofangfa.com',
    ':method': 'GET',
    ':path': '/',
    ':scheme': 'https',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    'cookie': 'Hm_lvt_994f6022e29faa53cf80c2dcc32d823a=1668361441; Hm_lpvt_994f6022e29faa53cf80c2dcc32d823a=1668361491',
    'dnt': '1',
    'pragma': 'no-cache',
    'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
}


async def parse_url(url, session):
    await asyncio.sleep(random.uniform(1, 3))
    try:
        async with await session.get(url=url, headers=headers) as response:
            return await response.text()
    except Exception as e:
        logger.error(f"错误:{e}")


async def parse(url, session):
    page_text = await parse_url(url, session)
    tree = etree.HTML(page_text)
    tr_list = tree.xpath("//table/tbody/tr")
    proxy_list = []
    for tr in tr_list:
        ip = tr.xpath("./td[1]/text()")
        ip = ip[0].strip()
        port = tr.xpath("./td[2]/text()")
        port = port[0].strip()
        proxy = ip + ":" + port
        proxy_list.append(proxy)
    await save_to_redis(proxy_list)


async def save_to_redis(proxy_list):
    for proxy in proxy_list:
        await aioredis_op.add(proxy)


async def run(session):
    url = "https://proxy.seofangfa.com/"
    logger.info("获取seo代理..")
    await parse(url, session)
    logger.info("seo代理已获取")