# -*- coding: utf-8 -*-
import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from proxy import ip_db
from proxy import ip_aiodb
from proxy import jiangxianli
from proxy import kuaidaili
from proxy import mimvp

if __name__ == '__main__':
    # 定时任务
    scheduler = AsyncIOScheduler()
    # 每几分钟获取一次 ip
    scheduler.add_job(mimvp.parse, 'interval', minutes=5)
    scheduler.add_job(kuaidaili.parse, 'interval', minutes=60)
    scheduler.add_job(ip_aiodb.update, 'interval', minutes=6)
    # scheduler.add_job(ip_db.clean, 'interval', minutes=15)
    # 每周每周一到周日下午定时运行一次
    scheduler.add_job(jiangxianli.parse, 'cron', day_of_week='mon-sun', hour=10, minute=00)
    # 每分钟更新一次ip
    scheduler.start()
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        print("退出!")
