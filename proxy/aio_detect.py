# -*- coding: utf-8 -*-
import asyncio
import random
import sys

sys.path.append("..")

from db import aioredis_op
from db.log import Logger

logger = Logger.get()

test_url = "https://www.csdn.net/"

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'zh-CN,zh;q=0.9', 'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Cookie': 'uuid_tt_dd=10_30851045390-1681351972101-951503; ssxmod_itna=Yq+xcD0G0=D=ZD7q0LKOb+DCDuQDgAc7AOeZ==Gx0y2eGzDAxn40iDt==yAhm+QYhIPLb0xqvYrF67u3dY3tY3aQTDCPGnDBIv3TDen=D5xGoDPxDeDADYE6DAqiOD7qDdEsNv/8DbxYpnDDoDY362DitD4qDB+odDKqGgbwqPiY=4u4rgGettYmD4bqDMmeGX8BnrOeaaoDN4xanVFOQDzMFDtwtgRkdYx0P9nLUVbEhaKAholOD=I0GFBGD=/Axeb+gqY2GNnKwPi0eqzGqWU0vnxDfn2iD===; ssxmod_itna2=Yq+xcD0G0=D=ZD7q0LKOb+DCDuQDgAc7AOeZ==DnI3rq4DsXeDLmO7Vf4QFQ08DeqhD=; c_adb=1; loginbox_strategy=%7B%22taskId%22%3A270%2C%22version%22%3A%22notInDomain%22%2C%22blog-sixH-default%22%3A1686149795357%7D; log_Id_click=106; https_waf_cookie=1bab14bb-562b-4732d94fcde71ddb0984b1e5f7dee8bbf952; dc_session_id=10_1686383521316.587915; c_pref=default; c_ref=default; c_first_ref=default; c_first_page=https%3A//www.csdn.net/; c_dsid=11_1686383523085.600463; c_segment=15; c_page_id=default; log_Id_pv=29; dc_sid=9244bac50ada5fd587cc27f3cd3539d3; www_red_day_last=red; hide_login=1; log_Id_view=113; dc_tos=rw11ux',
    'dnt': '1', 'Host': 'www.csdn.net', 'Pragma': 'no-cache',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"', 'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"', 'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none', 'Sec-Fetch-User': '?1', 'sec-gpc': '1', 'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}

# 限制并发量为 8
semaphore = asyncio.Semaphore(8)


async def test(ip, session):
    await asyncio.sleep(random.uniform(2, 4))
    """测试ip"""
    proxy = f"http://{ip}"
    try:
        async with semaphore:
            async with session.get(url=test_url, headers=headers, proxy=proxy, timeout=15) as response:
                return response.status if response.status != 200 else 200
    except Exception:
        return "disabled"


async def update(session):
    """更新ip集合，作为定时任务"""
    # 1.从数据库获取ip集
    proxy_list = await aioredis_op.get_all()
    if proxy_list:
        logger.info(">>>>>>ip池更新中>>>>>>")
        for proxy in proxy_list:
            # 2.测试单个ip
            ret = await test(proxy, session)
            if ret == 200:
                await aioredis_op.max(proxy)
            else:
                # 不合格的扣分
                await aioredis_op.decrease(proxy)
        logger.info("<<<<<<ip池已更新<<<<<<")
    else:
        logger.warning("暂无可用ip")
