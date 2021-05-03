# -*- coding: utf-8 -*-
import asyncio
import re
import sys

import aiofiles
import aiohttp
import pytesseract
from PIL import Image
from lxml import etree

sys.path.append("..")
from db.log import Logger
from db import aio_mysql_op

logger = Logger.get()

proxy_url = "https://proxy.mimvp.com/freeopen"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/86.0.4240.193 Safari/537.36"}


async def parse_url(url):
    async with aiohttp.ClientSession() as sess:  # 实例化一个请求对象
        # get/post(url,headers,params/data,proxy="http://ip:port")
        async with await sess.get(url=url, headers=headers) as response:  # 使用get发起请求，返回一个相应对象
            if url.find("common/ygrandimg") == -1:
                page_text = await response.text()  # text()获取字符串形式的相应数据  read()获取byte类型的响应数据
            else:
                page_text = await response.read()
            return page_text


async def img_recognition(url):
    r = await parse_url(url)
    image_name_list = re.findall('id=(\d+)&port', url)
    image_name = "".join(image_name_list)
    image_name = image_name + ".png"
    async with aiofiles.open(image_name, 'wb') as f:
        await f.write(r)
    image = Image.open(image_name)
    result_str = pytesseract.image_to_string(image).strip()
    result = result_str.replace("B", "8").replace("O", "0").replace("S", "5") \
        .replace("Z", "2").replace("l", "1").replace("g", "9")
    return result


async def parse():
    logger.info("米扑代理...")
    page_text = await parse_url(proxy_url)
    tree = etree.HTML(page_text)
    tr_list = tree.xpath("//div[@class='free-content']/table[@class='mimvp-tbl free-proxylist-tbl']/tbody/tr")
    proxy_list = []
    for tr in tr_list:
        ip = tr.xpath("./td[@class='free-proxylist-tbl-proxy-ip']/text()")
        ip = ip[0].strip()
        port_url = tr.xpath("./td[@class='free-proxylist-tbl-proxy-port']/img/@src")
        port_url = port_url[0].strip()
        port_url = "https://proxy.mimvp.com/" + port_url
        port = await img_recognition(port_url)
        proxy_str = ip + ":" + port
        proxy_list.append(proxy_str.replace(",", ""))
    await save_to_mysql(proxy_list)


async def save_to_mysql(proxy_list):
    for proxy in proxy_list:
        r = await aio_mysql_op.check(proxy)
        if r:
            proxy_list.remove(proxy)
    await aio_mysql_op.insert_many(proxy_list)


async def save_to_file(proxy_list):
    file_path = "ip_in_file.txt"
    async with aiofiles.open(file_path, "w+", encoding="utf-8") as f:
        for content in proxy_list:
            await f.write(content)
            await f.write("\n")


if __name__ == '__main__':
    task = asyncio.ensure_future(parse())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(task)
