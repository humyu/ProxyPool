# -*- coding: utf-8 -*-
import asyncio

import aiohttp
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from proxy import ip_aiodb
from proxy import jiangxianli
from proxy import kuaidaili
from proxy import mimvp


class WebSession(object):
    session = None

    @classmethod
    def create(cls):
        cls.session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=20, ssl=False))
        return cls.session

    @classmethod
    def close(cls):
        if cls.session is not None:
            return cls.session.close()


async def start_scheduler():
    # 创建会话
    if WebSession.session is None:
        session = WebSession.create()
    else:
        session = WebSession.session

    # 发布定时任务
    scheduler = AsyncIOScheduler()
    # 每周每周一到周日定时运行一次
    scheduler.add_job(mimvp.parse, 'cron', args=(session,), day_of_week='mon-sun', hour=22, minute=00)
    # 每小时运行一次
    scheduler.add_job(kuaidaili.run, 'interval', args=(session,), hours=1)
    # 每六分钟运行一次
    scheduler.add_job(jiangxianli.parse, 'interval', args=(session,), minutes=6)
    # 每二十分钟更新一次ip
    scheduler.add_job(ip_aiodb.update, 'interval', args=(session,), minutes=25, max_instances=3)
    # 开启任务
    scheduler.start()


async def close():
    # run this before the app ends
    await WebSession.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(start_scheduler())
    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit) as e:
        print(e)
    finally:
        loop.run_until_complete(close())
        loop.close()
        print("退出!")
