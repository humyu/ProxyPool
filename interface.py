# -*- coding: utf-8 -*-
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from proxy import db_select, jiangxianli
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
    scheduler.add_job(mimvp.parse, 'interval', minutes=5)
    scheduler.add_job(kuaidaili.parse, 'interval', minutes=60)
    # scheduler.add_job(jiangxianli.parse, 'interval', minutes=5)
    scheduler.add_job(db_select.clean, 'interval', minutes=15)
    # 每分钟更新一次ip
    scheduler.add_job(db_select.update, 'interval', minutes=5)
    scheduler.start()
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        db_mysql.close_spider()
