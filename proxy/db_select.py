# -*- coding: utf-8 -*-
import aiohttp
import random
import logging
import sys

sys.path.append("..")
from setting.db_mysql import DBMysql
from aiohttp import ClientOSError

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)

db_mysql = DBMysql()

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
        except (TimeoutError, ClientOSError) as e:
            logging.error(e)
            return e.args


async def update():
    """更新ip集合，作为定时任务"""
    logging.info("更新ip池...")
    # 1.从数据库获取ip集
    ip_list = db_mysql.get_all()
    if not ip_list:
        logging.info("数据库暂无ip")
    else:
        for ip in ip_list:
            # 2.测试单个ip
            status = await test(ip, test_url)
            # print(f"ip:{ip}:{status}")
            logging.info(f"ip:{ip}:{status}")
            # 不合格的删除
            if status != 200:
                db_mysql.delete_one(ip)
            ip_list.remove(ip)
    # print("更新ip池完毕!")
    logging.info("更新ip池完毕!")


def purge():
    """清空 ip 池"""
    db_mysql.delete_all()
    logging.info("清空 ip 池!")


async def get():
    """接口，作为外部使用的 ip """
    ip_list = db_mysql.get_all()
    if not ip_list:
        logging.info("数据库暂无ip")
    else:
        while True:
            ip = random.choice(ip_list)
            status = await test(ip, test_url)
            if status != 200:
                break
        return ip
