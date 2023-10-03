# -*- coding: utf-8 -*-
import asyncio
import random
import sys

sys.path.append("..")
from lxml import etree

from db import aioredis_op
from db.log import Logger

logger = Logger.get()

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Cookie': 'ASPSESSIONIDSAQSCARC=EMJCLMEDMFMKPJBCCBLGOMGM',
    'DNT': '1',
    'Host': 'www.kxdaili.com',
    'Pragma': 'no-cache',
    'Referer': 'http://www.kxdaili.com/dailiip.html',
    'sec-gpc': '1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}


def get_url_list():
    return [f"http://www.kxdaili.com/dailiip/1/{i}.html" for i in range(10)]


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
    tr_list = tree.xpath("//div[@class='hot-product-content']/table/tbody/tr")
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
    url_list = get_url_list()
    logger.info("获取开心代理..")
    for url in url_list:
        # logger.info(f"提取 {url}")
        await parse(url, session)
    logger.info("开心代理已获取")
