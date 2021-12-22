# -*- coding: utf-8 -*-
import asyncio
import random
import sys

sys.path.append("..")

from db import aioredis_op
from db.log import Logger

logger = Logger.get()

test_url = "https://www.csdn.net/"

headers = {':authority': 'www.csdn.net', ':method': 'GET', ':path': '/', ':scheme': 'https',
           'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
                     'application/signed-exchange;v=b3;q=0.9',
           'accept-encoding': 'gzip, deflate, br', 'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
           'cookie': 'uuid_tt_dd=10_37461587960-1640091597010-224989; log_Id_pv=1', 'dnt': '1',
           'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Microsoft Edge";v="96"', 'sec-ch-ua-mobile': '?0',
           'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'document', 'sec-fetch-mode': 'navigate',
           'sec-fetch-site': 'none', 'sec-fetch-user': '?1', 'upgrade-insecure-requests': '1',
           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62'}


async def test(ip, session):
    """测试ip"""
    proxy = f"http://{ip}"
    try:
        async with session.get(url=test_url, headers=headers, proxy=proxy, timeout=10) as response:
            return "disabled" if response.status != 200 else 200
    except Exception as e:
        # logger.error(f"错误:{e}")
        return "disabled"


async def update(session):
    """更新ip集合，作为定时任务"""
    # 1.从数据库获取ip集
    proxy_list = await aioredis_op.all()
    if proxy_list:
        logger.info("ip池更新...")
        for proxy in proxy_list:
            # 2.测试单个ip
            status = await test(proxy, session)
            # logger.info(f" {proxy} {status}")
            if status == "disabled":
                # 不合格的扣分
                await aioredis_op.decrease(proxy)
            else:
                await aioredis_op.max(proxy)
            await asyncio.sleep(random.randint(2, 4))
        logger.info("ip池已更新")
    else:
        logger.warning("暂无可用ip")
