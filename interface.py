# -*- coding: utf-8 -*-
import asyncio
import random
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from proxy import db_select
from proxy import mimvp
from proxy import kuaidaili
from setting.db_mysql import DBMysql


async def get_proxy():
    """获得一个可用ip"""
    return db_select.get()


if __name__ == '__main__':
    db_mysql = DBMysql()
    # 定时任务
    scheduler = AsyncIOScheduler()
    # 每几分钟获取一次 ip
    scheduler.add_job(mimvp.parse, 'interval', minutes=1)
    # scheduler.add_job(kuaidaili.parse, 'interval', minutes=5, max_instances=3)
    # 每天的9点15分清空一次ip池
    scheduler.add_job(db_select.purge, 'cron', hour=9, minute=15)
    # 每分钟更新一次ip
    scheduler.add_job(db_select.update, 'interval', minutes=1, max_instances=10)
    scheduler.start()
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        db_mysql.close_spider()
