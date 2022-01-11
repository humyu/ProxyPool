# -*- coding: utf-8 -*-
"""
该网站每天不定时获取一次 ip
"""
import asyncio
import random
import re
import sys

sys.path.append("..")
import aiofiles
import pytesseract
from PIL import Image
from lxml import etree

from db import aioredis_op
from db.log import Logger

logger = Logger.get()

proxy_url = "https://proxy.mimvp.com/freeopen"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/86.0.4240.193 Safari/537.36"}


async def parse_url(url, session):
    await asyncio.sleep(random.uniform(1, 3))
    try:
        async with await session.get(url=url, headers=headers) as response:
            if url.find("common/ygrandimg") == -1:
                page_text = await response.text()
            else:
                page_text = await response.read()
            return page_text
    except Exception as e:
        logger.error(f"错误:{e}")


async def img_recognition(url, session):
    r = await parse_url(url, session)
    image_name_list = re.findall(r'id=(\d+)&port', url)
    image_name = "".join(image_name_list)
    image_name = image_name + ".png"
    async with aiofiles.open(image_name, 'wb') as f:
        await f.write(r)
    image = Image.open(image_name)
    result_str = pytesseract.image_to_string(image).strip()
    result = result_str.replace("B", "8").replace("O", "0").replace("S", "5") \
        .replace("Z", "2").replace("l", "1").replace("g", "9")
    return result


async def parse(session):
    page_text = await parse_url(proxy_url, session)
    tree = etree.HTML(page_text)
    tr_list = tree.xpath(
        "//div[@class='free-content']/table[@class='mimvp-tbl free-proxylist-tbl']/tbody/tr")
    proxy_list = []
    for tr in tr_list:
        ip = tr.xpath("./td[@class='free-proxylist-tbl-proxy-ip']/text()")
        ip = ip[0].strip()
        port_url = tr.xpath(
            "./td[@class='free-proxylist-tbl-proxy-port']/img/@src")
        port_url = port_url[0].strip()
        port_url = "https://proxy.mimvp.com/" + port_url
        port = await img_recognition(port_url, session)
        proxy_str = ip + ":" + port
        proxy_list.append(proxy_str.replace(",", ""))
    await save_to_redis(proxy_list)


async def save_to_file(proxy_list):
    file_path = "ip_in_file.txt"
    async with aiofiles.open(file_path, "w+", encoding="utf-8") as f:
        for content in proxy_list:
            await f.write(content)
            await f.write("\n")


async def save_to_redis(proxy_list):
    for proxy in proxy_list:
        await aioredis_op.add(proxy)


async def run(session):
    logger.info("米扑代理..")
    await parse(session)
    logger.info("米扑代理已获取")
