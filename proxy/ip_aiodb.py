# -*- coding: utf-8 -*-
import asyncio
import random
import sys

sys.path.append("..")

from db import aioredis_op
from db.log import Logger

logger = Logger.get()

test_url = "https://blog.csdn.net"

headers = {'authority': 'blog.csdn.net',
           'method': 'GET',
           'path': '/',
           'scheme': 'https',
           'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
           'accept-encoding': 'gzip, deflate, br',
           'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
           'cookie': 'uuid_tt_dd=10_37461587960-1640091597010-224989; ssxmod_itna=eqUxnD9DgQ=DqiKGHIhCGQieD5y47KP4LxvdD/KDfr4iNDnD8x7YDvmm=lmG+F10hD3GGUD4x4WeSGf+q+/ixZmPDHxY=DUx8+xoD4RKGwD0eG+DD4DWKqB=yDtqDkD3qDdEx7PGSIq7=D4TLnKDDHG0i57qGEDBtjD0QDAwr74eDRfqDgbqD+fqDM04G2fLr/DiQHBn=Dbh=5DDN5fcx8C0uuCcclzWR3XWut2CTj4pTOFrrP1PpymuUnDYo6Yci9GIUSC65qix+Xtx4tm7PaDODtW0D5iSLKDgwmK0GXGGGGDOpa9V4of4DxDW3DGHiDD=; ssxmod_itna2=eqUxnD9DgQ=DqiKGHIhCGQieD5y47KP4Lx5G9t5GBDBqeAIxGaQafOkhvx8hAzidYtSODW=7t8rw5eCdMgWxnIcQn+7c44M1eqavPtx7QpDFqG7teD==; log_Id_click=9; dc_session_id=10_1643290637698.975242; csrfToken=Wgbr7dUdokm7TYq6L_es_0xL; c_pref=default; c_ref=default; c_first_ref=default; c_first_page=https%3A//blog.csdn.net/; c_segment=13; c_page_id=default; dc_tos=r6df67; log_Id_pv=22; dc_sid=bac5adf6994fb249eb858eb90200bd26; log_Id_view=88',
           'dnt': '1',
           'sec-ch-ua': '" Not;A Brand";v="99", "Microsoft Edge";v="97", "Chromium";v="97"',
           'sec-ch-ua-mobile': '?0',
           'sec-ch-ua-platform': '"Windows"',
           'sec-fetch-dest': 'document',
           'sec-fetch-mode': 'navigate',
           'sec-fetch-site': 'none',
           'sec-fetch-user': '?1',
           'upgrade-insecure-requests': '1',
           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36 Edg/97.0.1072.69'}

# 限制并发量为 8
semaphore = asyncio.Semaphore(8)


async def test(ip, session):
    await asyncio.sleep(random.uniform(2, 4))
    """测试ip"""
    proxy = f"http://{ip}"
    try:
        async with semaphore:
            async with session.get(url=test_url, headers=headers, proxy=proxy, timeout=10) as response:
                return "disabled" if response.status != 200 else "ok"
    except Exception as e:
        # logger.error(f"错误:{e}")
        return "disabled"


async def update(session):
    """更新ip集合，作为定时任务"""
    # 1.从数据库获取ip集
    proxy_list = await aioredis_op.get_all()
    if proxy_list:
        logger.info("=ip池更新中=")
        for proxy in proxy_list:
            # 2.测试单个ip
            status = await test(proxy, session)
            # logger.info(f" {proxy} {status}")
            if status == "disabled":
                # 不合格的扣分
                await aioredis_op.decrease(proxy)
            else:
                await aioredis_op.max(proxy)
        logger.info("=ip池已更新=")
    else:
        logger.warning("暂无可用ip")
