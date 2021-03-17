# -*- coding: utf-8 -*-
import aiohttp
import asyncio
import time
import random
import sys

sys.path.append("..")
from setting.db_mysql import DBMysql
from apscheduler.schedulers.asyncio import AsyncIOScheduler

db_mysql = DBMysql()

test_url = "http://httpbin.org/get"


async def test(ip, url):
    """测试ip"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
    conn = aiohttp.TCPConnector(verify_ssl=False)
    async with aiohttp.ClientSession(connector=conn) as session:
        try:
            proxy_ip = 'http://' + ip
            print(f"proxy_ip:{proxy_ip}")
            async with session.get(url=url, headers=headers, proxy=proxy_ip, timeout=10) as response:
                if response.status == 200:
                    return "success"
                else:
                    return "failure"
        except:
            return "failure"


async def update():
    """更新ip集合，作为定时任务"""
    # 1.从数据库获取ip集
    ip_list = db_mysql.get()
    for ip in ip_list:
        # 2.测试单个ip
        status = await test(ip, test_url)
        # 不合格的删除
        if status == "failure":
            db_mysql.delete(ip)
        ip_list.remove(ip)


async def get_proxy():
    """接口，作为外部使用的 ip """
    ip_list = db_mysql.get()
    while True:
        ip = random.choice(ip_list)
        status = await test(ip, test_url)
        if status == "success":
            break
    return ip


def purge():
    """清空 ip 池"""
    db_mysql.delete_all()
    print("清空 ip 池!")


if __name__ == '__main__':
    # 定时任务
    # AsyncIOScheduler : 当你的程序使用了asyncio（一个异步框架）的时候使用
    scheduler = AsyncIOScheduler()
    # 每天只运行一次，每天的9点15分能够准时启动
    scheduler.add_job(purge, 'cron', hour=9, minute=15)
    # 每5分钟测试并更新一次 ip
    scheduler.add_job(update, 'interval', minutes=5)
    scheduler.start()
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        db_mysql.close_spider()
