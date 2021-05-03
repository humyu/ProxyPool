# -*- coding: utf-8 -*-
from db.aio_mysql_base import DBAioMysql


async def get_mysql_obj():
    mysql_obj = DBAioMysql()
    pool = await mysql_obj.init_pool()
    mysql_obj.pool = pool
    return mysql_obj


async def check(item):
    mysql_obj = await get_mysql_obj()
    exeRtn = await mysql_obj.query("select ip from t_proxy where ip = %s", item)
    if exeRtn:
        return True
    else:
        return False


async def insert_one(item):
    mysql_obj = await get_mysql_obj()
    data = dict(item)
    await mysql_obj.execute("insert into t_proxy (ip) values (% s)", tuple(data.values()))
    # if exeRtn:
    #     print('操作成功')
    # else:
    #     print('操作失败')


async def insert_many(item_list):
    tuple_list = [(item, 5, 0) for item in item_list]
    mysql_obj = await get_mysql_obj()
    await mysql_obj.execute_many("insert into t_proxy (ip,score,times) values (% s, % s, % s)", tuple_list)
    # if exeRtn:
    #     print('操作成功')
    # else:
    #     print('操作失败')


async def get():
    mysql_obj = await get_mysql_obj()
    exeRtn = await mysql_obj.query("select distinct ip,score from t_proxy where score > 0")
    return exeRtn


async def delete_one(item):
    param = item["ip"]
    mysql_obj = await get_mysql_obj()
    await mysql_obj.execute("delete from t_proxy where ip = % s", param)
    # if exeRtn:
    #     print('操作成功')
    # else:
    #     print('操作失败')


async def delete_useless():
    mysql_obj = await get_mysql_obj()
    await mysql_obj.execute("delete from t_proxy where score <= 0")
    # if exeRtn:
    #     print('操作成功')
    # else:
    #     print('操作失败')


async def update_score(item):
    data = dict(item)
    param = list(data.values())
    param.reverse()
    mysql_obj = await get_mysql_obj()
    await mysql_obj.execute("update t_proxy set score = %s where ip = %s", param)
    # if exeRtn:
    #     print('操作成功')
    # else:
    #     print('操作失败')
