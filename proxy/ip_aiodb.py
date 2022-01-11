# -*- coding: utf-8 -*-
import asyncio
import random
import sys

sys.path.append("..")

from db import aioredis_op
from db.log import Logger

logger = Logger.get()

test_url = "http://httpbin.org/get"

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "no-cache",
    "Dnt": "1",
    "Host": "httpbin.org",
    "Pragma": "no-cache",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
}

# 限制并发量为 10
semaphore = asyncio.Semaphore(10)


async def test(ip, session):
    await asyncio.sleep(random.uniform(2, 4))
    """测试ip"""
    proxy = f"http://{ip}"
    try:
        async with semaphore:
            async with session.get(url=test_url, headers=headers, proxy=proxy, timeout=10) as response:
                return "bad" if response.status != 200 else 200
    except Exception as e:
        # logger.error(f"错误:{e}")
        return "disabled"


async def update(session):
    """更新ip集合，作为定时任务"""
    # 1.从数据库获取ip集
    proxy_list = await aioredis_op.all()
    if proxy_list:
        logger.info("=ip池更新中=")
        for proxy in proxy_list:
            # 2.测试单个ip
            status = await test(proxy, session)
            # logger.info(f" {proxy} {status}")
            if status == "disabled" or "bad":
                # 不合格的扣分
                await aioredis_op.decrease(proxy)
            else:
                await aioredis_op.max(proxy)
        logger.info("=ip池已更新=")
    else:
        logger.warning("暂无可用ip")
