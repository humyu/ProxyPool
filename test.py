# -*- coding: utf-8 -*-
import asyncio

from proxy import aio_detect
from web_session import WebSession
from proxy import ip3366
from proxy import kxdaili
from proxy import seofangfa
from proxy import jiangxianli
from db.aioredis_base import DBAioRedis


async def close():
    # run this before the app ends
    await WebSession.close()


if __name__ == '__main__':
    # 创建会话
    if WebSession.session is None:
        session = WebSession.create()
    else:
        session = WebSession.session

    print(f"统一会话 WebSession：{WebSession}")

    # if DBAioRedis.pool is None:
    #     pool = DBAioRedis.init_pool()
    # else:
    #     pool = DBAioRedis.pool

    task = asyncio.ensure_future(aio_detect.update(session))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(task)
    loop.run_until_complete(close())
