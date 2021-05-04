# -*- coding: utf-8 -*-
import asyncio
import random
import sys

import aiohttp

sys.path.append("..")

from db import aioredis_op
from db.log import Logger

logger = Logger.get()

test_url = "https://www.baidu.com"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/71.0.3578.98 Safari/537.36'}


async def test(ip, url):
    """测试ip"""
    proxy = f"http://{ip}"
    conn = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=conn) as session:
        try:
            async with session.get(url=url, headers=headers, proxy=proxy,timeout=10) as response:
                return "disabled" if response.status != 200 else 200
        except Exception as e:
            logger.error(f"错误:{e}")
            return "disabled"


async def update():
    """更新ip集合，作为定时任务"""
    # 1.从数据库获取ip集
    proxy_list = await aioredis_op.all()
    if proxy_list:
        logger.info("更新ip池...")
        for proxy in proxy_list:
            # 2.测试单个ip
            status = await test(proxy, test_url)
            logger.info(f" {proxy} {status}")
            if status == "disabled":
                # 不合格的扣分
                await aioredis_op.decrease(proxy)
            else:
                await aioredis_op.max(proxy)
            await asyncio.sleep(random.randint(2, 4))
    else:
        logger.warning("暂无可用ip")


if __name__ == '__main__':
    task = asyncio.ensure_future(update())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(task)
