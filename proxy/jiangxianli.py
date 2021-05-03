# -*- coding: utf-8 -*-
import asyncio
import json
import random
import sys
import time

import aiohttp

sys.path.append("..")
from db.log import Logger
from db import aio_mysql_op

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


async def parse_url(url):
    async with aiohttp.ClientSession() as sess:  # 实例化一个请求对象
        # get/post(url,headers,params/data,proxy="http://ip:port")
        try:
            async with await sess.get(url=url, headers=headers) as response:  # 使用get发起请求，返回一个相应对象
                page_text = await response.text()  # text()获取字符串形式的相应数据  read()获取byte类型的响应数据
                return page_text
        except Exception as e:
            logger.error(f"错误:{e}")


async def parse():
    logger.warning("jiangxianli...")
    current_page = last_page = 1
    while current_page <= last_page:
        url = f"https://ip.jiangxianli.com/api/proxy_ips?page={current_page}"
        logger.info(f"提取 {url}")
        page_text = await parse_url(url)
        json_str = json.loads(page_text)
        data_list = json_str.get("data").get("data")
        current_page = json_str.get("data").get("current_page")
        last_page = json_str.get("data").get("last_page")
        proxy_list = []
        for data in data_list:
            country = data.get("country")
            if country == "中国":
                ip = data.get("ip")
                port = data.get("port")
                proxy = ip + ":" + port
                proxy_list.append(proxy)
        await save_to_mysql(proxy_list)
        time.sleep(random.randint(1, 3))
        current_page = current_page + 1


async def save_to_mysql(proxy_list):
    for proxy in proxy_list:
        r = await aio_mysql_op.check(proxy)
        if r:
            proxy_list.remove(proxy)
    await aio_mysql_op.insert_many(proxy_list)


if __name__ == '__main__':
    task = asyncio.ensure_future(parse())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(task)
