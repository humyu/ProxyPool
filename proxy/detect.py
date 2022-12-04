# -*- coding: utf-8 -*-
import asyncio
import random
import sys

sys.path.append("..")

from db import aioredis_op
from db.log import Logger

logger = Logger.get()

test_url = "https://mmzztt.com/"

headers = {'authority': 'www.csdn.net', 'method': 'GET', 'path': '/', 'scheme': 'https',
               'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
               'accept-encoding': 'gzip, deflate, br', 'accept-language': 'zh-CN,zh;q=0.9', 'cache-control': 'no-cache',
               'cookie': 'uuid_tt_dd=10_9771887390-1621431052510-918125; Hm_ct_6bcd52f51e9b3dce32bec4a3997715ac=6525*1*10_9771887390-1621431052510-918125; Hm_up_6bcd52f51e9b3dce32bec4a3997715ac=%7B%22islogin%22%3A%7B%22value%22%3A%220%22%2C%22scope%22%3A1%7D%2C%22isonline%22%3A%7B%22value%22%3A%220%22%2C%22scope%22%3A1%7D%2C%22isvip%22%3A%7B%22value%22%3A%220%22%2C%22scope%22%3A1%7D%7D; _ga=GA1.2.2147159111.1621524892; c_dl_fref=https://www.baidu.com/link; c_dl_um=-; c_dl_prid=1638867376842_512466; c_dl_rid=1638867451080_221813; c_dl_fpage=/download/qq_29442537/8911787; firstDie=1; unlogin_scroll_step=1641196672393; ssxmod_itna=YqjxcDgD0QYxnQDzZD2YL08crDyDQTK4PKDsaKbDSxGKidDqxBmnMqDt3bqQK3Bl7S5YQGYi0m54BQOr20zIGUM4GLDmKDyD=gheDx=q0rD74irDDxD3DbbdDSDWKD9D0bSyuEXKGWDbo=Di4D+bkQDmqG0DDUF04G2D7UnDrhdTwijiWtYhqe4yY=DjTbD/SxTLY=KN=c30wiiyBpxDxDHKA+kLDHeScGVQOQDzw7DtwtgRTdYXp=ZfMNzz0mx/8vx0r4qireCiBxPtSLWQDveY5qGW0GWR0qQmAfgxDf+fbD==; ssxmod_itna2=YqjxcDgD0QYxnQDzZD2YL08crDyDQTK4PikpGzzDlx4Gwx03ee2EjD6WwHEeu645+7lCZkDAbDKT23DLxiQP4D==; dc_session_id=10_1641214879954.374370; csrfToken=0ObLDQ5mtHKnrnTz2ikUYkj0; c_first_ref=default; c_first_page=https%3A//www.csdn.net/; c_segment=13; dc_sid=a00ad418b93d6b2556a28a13595dd641; Hm_lvt_6bcd52f51e9b3dce32bec4a3997715ac=1641196639,1641196692,1641202639,1641214885; log_Id_click=63; c_pref=https%3A//blink.csdn.net/; c_ref=https%3A//bbs.csdn.net/topics/603958232; c_page_id=default; dc_tos=r54xkg; log_Id_pv=208; Hm_lpvt_6bcd52f51e9b3dce32bec4a3997715ac=1641214964; log_Id_view=715',
               'pragma': 'no-cache', 'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
               'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'document',
               'sec-fetch-mode': 'navigate', 'sec-fetch-site': 'none', 'sec-fetch-user': '?1',
               'upgrade-insecure-requests': '1',
               'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}

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
        logger.info(">>>ip池更新中>>>")
        for proxy in proxy_list:
            # 2.测试单个ip
            status = await test(proxy, session)
            # logger.info(f" {proxy} {status}")
            if status == "disabled":
                # 不合格的扣分
                await aioredis_op.decrease(proxy)
            else:
                await aioredis_op.max(proxy)
        logger.info("<<<ip池已更新<<<")
    else:
        logger.warning("暂无可用ip")
