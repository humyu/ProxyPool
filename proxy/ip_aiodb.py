# -*- coding: utf-8 -*-
import asyncio
import random
import sys

import aiohttp

sys.path.append("..")
from db.log import Logger
from db import aio_redis_op

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
    proxy_list = await aio_redis_op.get_all()
    if proxy_list:
        logger.info("更新ip池...")
        for proxy in proxy_list:
            # 2.测试单个ip
            status = await test(proxy, test_url)
            if status == "disabled":
                # 不合格的删除
                await aio_redis_op.delete_one()
            logger.info(f" {proxy} {status}")
            await asyncio.sleep(random.randint(2, 4))
    else:
        logger.warning("暂无可用ip")
