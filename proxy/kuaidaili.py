# -*- coding: utf-8 -*-
"""
该网站每天更新一次 ip，每小时获取一个新 ip
"""
import asyncio
import aiohttp
import random
import sys

sys.path.append("..")
from lxml import etree

from db import aioredis_op
from db.log import Logger

logger = Logger.get()

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Cookie': 'channelid=0; _gcl_au=1.1.2076749374.1665903149; _ga=GA1.2.1701248196.1665903149; Hm_lvt_7ed65b1cc4b810e9fd37959c9bb51b31=1665903149,1667764377; _gid=GA1.2.938075472.1667764377; sid=1667764178868245; Hm_lpvt_7ed65b1cc4b810e9fd37959c9bb51b31=1667764408',
    'DNT': '1',
    'Host': 'www.kuaidaili.com',
    'Pragma': 'no-cache',
    'Referer': 'https://www.kuaidaili.com/free/inha',
    'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'}


def get_url_list():
    return [f"https://www.kuaidaili.com/free/inha/{i}/" for i in range(1, 3)]


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
        ip = tr.xpath("./td[@data-title='IP']/text()")
        ip = ip[0].strip()
        port = tr.xpath("./td[@data-title='PORT']/text()")
        port = port[0].strip()
        proxy = ip + ":" + port
        proxy_list.append(proxy.replace(",", ""))
    await save_to_redis(proxy_list)


async def save_to_redis(proxy_list):
    for proxy in proxy_list:
        await aioredis_op.add(proxy)


async def run(session):
    url_list = get_url_list()
    logger.info("获取快代理..")
    for url in url_list:
        # logger.info(f"提取 {url}")
        await parse(url, session)
    logger.info("快代理已获取")