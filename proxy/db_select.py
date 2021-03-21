# -*- coding: utf-8 -*-
import aiohttp
import random
import sys

sys.path.append("..")
from setting.db_mysql import DBMysql

db_mysql = DBMysql()

test_url = "http://httpbin.org/get"


async def test(ip, url):
    """测试ip"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
    conn = aiohttp.TCPConnector(verify_ssl=False)
    async with aiohttp.ClientSession(connector=conn) as session:
        try:
            proxy = f"http://{ip}"
            async with session.get(url=url, headers=headers, proxy=proxy, timeout=10) as response:
                return response.status
        except Exception as e:
            return e.args


async def update():
    """更新ip集合，作为定时任务"""
    print("更新ip池...")
    # 1.从数据库获取ip集
    ip_list = db_mysql.get()
    if not ip_list:
        print("数据库暂无ip")
    else:
        for ip in ip_list:
            # 2.测试单个ip
            status = await test(ip, test_url)
            print(f"ip:{ip}:{status}")
            # 不合格的删除
            if status != 200:
                db_mysql.delete(ip)
            ip_list.remove(ip)
    print("更新ip池完毕!")


def purge():
    """清空 ip 池"""
    db_mysql.delete_all()
    print("清空 ip 池!")


async def get():
    """接口，作为外部使用的 ip """
    ip_list = db_mysql.get()
    if not ip_list:
        print("数据库暂无ip")
    else:
        while True:
            ip = random.choice(ip_list)
            status = await test(ip, test_url)
            if status !=200:
                break
        return ip
