# -*- coding: utf-8 -*-
import asyncio
import aiohttp
import time

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from lxml import etree
import tesserocr
from PIL import Image
import requests
import db_select
import sys

sys.path.append("..")
from setting.db_mysql import DBMysql

db_mysql = DBMysql()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/86.0.4240.193 Safari/537.36"}


async def parse_img(url):
    response = requests.get(url, headers=headers)
    return response.content


async def parse_url(url):
    async with aiohttp.ClientSession() as sess:  # 实例化一个请求对象
        # get/post(url,headers,params/data,proxy="http://ip:port")
        async with await sess.get(url=url, headers=headers) as response:  # 使用get发起请求，返回一个相应对象
            page_text = await response.text()  # text()获取字符串形式的相应数据  read()获取byte类型的响应数据
            return page_text


async def img_recognition(url):
    r = await parse_img(url)
    with open('img.png', 'wb') as f:
        f.write(r)
    image = Image.open("img.png")
    result = tesserocr.image_to_text(image).strip()
    return result


async def parse(url):
    page_text = await parse_url(url)
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
    # return proxy_list


async def save_to_mysql(proxy_list):
    for proxy in proxy_list:
        item = {"proxy": proxy}
        db_mysql.insert(item)


async def save_to_file(proxy_list):
    file_path = "ip_in_file.txt"
    with open(file_path, "w+", encoding="utf-8") as f:
        for content in proxy_list:
            f.write(content)
            f.write("\n")


if __name__ == '__main__':
    proxy_url = "https://proxy.mimvp.com/freesecret"
    # 定时任务
    # AsyncIOScheduler : 当你的程序使用了asyncio（一个异步框架）的时候使用
    scheduler = AsyncIOScheduler()
    # 每5分钟获取一次 ip
    scheduler.add_job(parse, 'interval', [proxy_url], minutes=5)
    scheduler.start()
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        db_mysql.close_spider()
