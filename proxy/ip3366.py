# -*- coding: utf-8 -*-
"""
该网站每天更新一次 ip，每小时获取一个新 ip
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
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Cookie': 'Hm_lvt_c4dd741ab3585e047d56cf99ebbbe102=1639652493,1641406423,1641567388,1641642057; ASPSESSIONIDCCSBASBR=MCDDOILAMKAIFPHPOFPMNGGD; Hm_lpvt_c4dd741ab3585e047d56cf99ebbbe102=1641642412',
    'DNT': '1',
    'Host': 'www.ip3366.net',
    'Pragma': 'no-cache',
    'Referer': 'http://www.ip3366.net/?stype=1&page=7',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}


def get_url_list():
    return [f"http://www.ip3366.net/?stype=1&page={i}" for i in range(1, 3)]


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
    tr_list = tree.xpath("//div[@id='list']/table/tbody/tr")
    proxy_list = []
    for tr in tr_list:
        ip = tr.xpath("./td[1]/text()")
        ip = ip[0].strip()
        port = tr.xpath("./td[2]/text()")
        port = port[0].strip()
        proxy = ip + ":" + port
        proxy_list.append(proxy.replace(",", ""))
    await save_to_redis(proxy_list)


async def save_to_redis(proxy_list):
    for proxy in proxy_list:
        await aioredis_op.add(proxy)


async def run(session):
    logger.info("获取云代理..")
    url_list = get_url_list()
    for url in url_list:
        logger.info(f"提取 {url}")
        await parse(url, session)
    logger.info("云代理已获取")
