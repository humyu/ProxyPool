# -*- coding: utf-8 -*-
import sys

import aiohttp
import asyncio

sys.path.append("..")
from setting.db_mysql import DBMysql
from setting.log import Logger
import time
import random

db_mysql = DBMysql()
logger = Logger.get()

test_url = "http://httpbin.org/get"

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/71.0.3578.98 Safari/537.36'}


async def test(ip, url):
    """测试ip"""
    proxy = f"http://{ip}"
    conn = aiohttp.TCPConnector(verify_ssl=False)
    async with aiohttp.ClientSession(connector=conn) as session:
        try:
            async with session.get(url=url, headers=headers, proxy=proxy, timeout=10) as response:
                return response.status
        except Exception as e:
            logger.error(f"错误:{e}")
            return "disabled"


async def update():
    """更新ip集合，作为定时任务"""
    # 1.从数据库获取ip集
    proxy_list = db_mysql.get_all()
    if proxy_list:
        logger.warning("更新ip池...")
        for proxy in proxy_list:
            # 2.测试单个ip
            status = await test(proxy["ip"], test_url)
            # 不合格的删除
            logger.warning(f" {proxy} {status}")
            if status == "disabled":
                db_mysql.delete_one(proxy)
            elif status != 200:
                proxy["score"] -= 1
                db_mysql.update_score(proxy)
                logger.warning(f" {proxy} 超时")
            else:
                proxy["score"] += 1
                db_mysql.update_score(proxy)
                logger.warning(f" {proxy} {status}")
            time.sleep(random.randint(2, 4))
        # logger.warning("更新ip池完毕!")
    else:
        logger.warning("暂无ip,请等待...")


async def clean():
    """删除质量差的ip"""
    db_mysql.delete_useless()
    logger.warning("删除质量差的ip!")


async def get():
    """接口，作为外部使用的 ip """
    ip_list = db_mysql.get_all()
    if not ip_list:
        logger.warning("暂无ip,请等待...")
    else:
        while True:
            ip = random.choice(ip_list)
            status = await test(ip, test_url)
            if status != 200:
                break
        return ip


if __name__ == '__main__':
    task = asyncio.ensure_future(update())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(task)