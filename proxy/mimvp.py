# -*- coding: utf-8 -*-
import aiohttp

from lxml import etree
import pytesseract
from PIL import Image
import requests
import sys

sys.path.append("..")
from setting.db_mysql import DBMysql
import logging

db_mysql = DBMysql()

proxy_url = "https://proxy.mimvp.com/freeopen"

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
    result_str = pytesseract.image_to_string(image).strip()
    result = result_str.replace("B", "8").replace("O", "0").replace("S", "5")\
        .replace("Z", "2").replace("l","1").replace("g", "9")
    return result


async def parse():
    logging.info("获取米扑代理...")
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
    logging.info("获取米扑代理完毕!")


async def save_to_mysql(proxy_list):
    for proxy in proxy_list:
        item = {"proxy": proxy}
        db_mysql.insert_one(item)


async def save_to_file(proxy_list):
    file_path = "ip_in_file.txt"
    with open(file_path, "w+", encoding="utf-8") as f:
        for content in proxy_list:
            f.write(content)
            f.write("\n")
