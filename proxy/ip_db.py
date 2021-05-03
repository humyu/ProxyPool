# -*- coding: utf-8 -*-
import asyncio
import sys

import aiohttp

sys.path.append("..")
from db.log import Logger
import time
import random
from db import aio_mysql_op

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
    proxy_list = await aio_mysql_op.get()
    if proxy_list:
        logger.info("更新ip池...")
        for proxy in proxy_list:
            # 2.测试单个ip
            status = await test(proxy["ip"], test_url)
            # 不合格的删除
            if status == "disabled":
                proxy["score"] = 0
            elif status != 200:
                proxy["score"] -= 1
            else:
                proxy["score"] += 1
            await aio_mysql_op.update_score(proxy)
            logger.info(f" {proxy} {status}")
            await asyncio.sleep(random.randint(2, 4))
    else:
        logger.warning("暂无可用ip")


async def clean():
    """删除质量差的ip"""
    await aio_mysql_op.delete_useless()
    logger.info("删除质量差的ip!")


if __name__ == '__main__':
    task = asyncio.ensure_future(update())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(task)
