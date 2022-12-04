# -*- coding: utf-8 -*-
"""
该网站数据大概每五分钟检测一次
"""
import asyncio
import json
import random
import sys

sys.path.append("..")
import time

from db import aioredis_op
from db.log import Logger

logger = Logger.get()

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Cookie": "UM_distinctid=178b05e7fa419d-000f2abdce6b45-c3f3568-100200-178b05e7fa5660; CNZZDATA1278691459=1517096328-1617864977-https%253A%252F%252Fcn.bing.com%252F%7C1617864977; Hm_lvt_b72418f3b1d81bbcf8f99e6eb5d4e0c3=1617866686,1617868243; Hm_lpvt_b72418f3b1d81bbcf8f99e6eb5d4e0c3=1617869636",
    "Host": "ip.jiangxianli.com",
    "Referer": "https://github.com/jiangxianli/ProxyIpLib",
    "sec-ch-ua": "'Google Chrome';v='89', 'Chromium';v='89', ';Not A Brand';v='99'",
    "sec-ch-ua-mobile": "?0",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/86.0.4240.193 Safari/537.36"}


async def parse_url(url, session):
    await asyncio.sleep(random.uniform(1, 3))
    try:
        async with await session.get(url=url, headers=headers) as response:  # 使用get发起请求，返回一个相应对象
            return await response.text()  # text()获取字符串形式的相应数据  read()获取byte类型的响应数据
    except Exception as e:
        logger.error(f"错误:{e}")


async def parse(session):

    current_page = last_page = 1
    while current_page <= last_page:
        url = f"https://ip.jiangxianli.com/api/proxy_ips?page={current_page}"
        # logger.info(f"jiangxianli 代理第 {current_page} 页")
        page_text = await parse_url(url, session)
        json_str = json.loads(page_text)
        data_list = json_str.get("data").get("data")
        # 当前页码
        current_page = json_str.get("data").get("current_page")
        # 最后一页页码
        last_page = json_str.get("data").get("last_page")
        proxy_list = []
        for data in data_list:
            country = data.get("country")
            anonymity = data.get("anonymity")
            if country == "中国" and anonymity == 2:
                ip = data.get("ip")
                port = data.get("port")
                proxy = ip + ":" + port
                proxy_list.append(proxy)
        await save_to_redis(proxy_list)
        time.sleep(random.randint(2, 4))
        current_page = current_page + 1


async def save_to_redis(proxy_list):
    for proxy in proxy_list:
        await aioredis_op.add(proxy)


async def run(session):
    logger.info("获取jiangxianli代理..")
    await parse(session)
    logger.info("jiangxianli代理已获取")
