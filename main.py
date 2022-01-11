# -*- coding: utf-8 -*-
import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from web_session import WebSession
from proxy import ip_aiodb
from proxy import jiangxianli
from proxy import kuaidaili
from proxy import mimvp
from proxy import ip3366


async def start_scheduler():
    # 创建会话
    if WebSession.session is None:
        session = WebSession.create()
    else:
        session = WebSession.session

    # 发布定时任务
    scheduler = AsyncIOScheduler()
    # 每周每周一到周日定时运行一次
    scheduler.add_job(mimvp.run, 'cron', args=(session,), day_of_week='mon-sun', hour=22, minute=00)
    # 每小时运行一次
    scheduler.add_job(kuaidaili.run, 'interval', args=(session,), hours=1)
    # 每两小时运行一次
    scheduler.add_job(ip3366.run, 'interval', args=(session,), hours=1.5)
    # 每十分钟运行一次
    scheduler.add_job(jiangxianli.run, 'interval', args=(session,), minutes=9)
    # 每二十分钟更新一次ip
    scheduler.add_job(ip_aiodb.update, 'interval', args=(session,), minutes=20, max_instances=2)
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
