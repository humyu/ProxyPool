# -*- coding: utf-8 -*-
import logging
import traceback

import aiomysql

from setting import db_setting

logobj = logging.getLogger('mysql')


class DBMysql:

    def __init__(self):
        self.conn = None
        self.pool = None

    async def init_pool(self):
        try:
            logobj.debug("will connect mysql~")
            __pool = await aiomysql.create_pool(
                minsize=5,  # 连接池最小值
                maxsize=10,  # 连接池最大值
                host=db_setting.MYSQL_HOST,
                port=db_setting.MYSQL_PORT,
                user=db_setting.MYSQL_USER,
                password=db_setting.MYSQL_PASSWORD,
                db=db_setting.MYSQL_DATABASE,
                autocommit=True,  # 自动提交模式
            )
            return __pool
        except:
            logobj.error('connect error.', exc_info=True)

    async def get_curosr(self):
        conn = await self.pool.acquire()
        # 返回字典格式
        cur = await conn.cursor(aiomysql.DictCursor)
        return conn, cur

    async def query(self, query, param=None):
        """
        查询操作
        :param query: sql语句
        :param param: 参数
        :return:
        """
        conn, cur = await self.get_curosr()
        try:
            await cur.execute(query, param)
            return await cur.fetchall()
        except:
            logobj.error(traceback.format_exc())
        finally:
            if cur:
                await cur.close()
            # 释放掉conn,将连接放回到连接池中
            await self.pool.release(conn)

    async def execute(self, query, param=None):
        """
        增删改 操作
        :param query: sql语句
        :param param: 参数
        :return:
        """
        conn, cur = await self.get_curosr()
        try:
            await cur.execute(query, param)
            if cur.rowcount == 0:
                return False
            else:
                return True
        except:
            logobj.error(traceback.format_exc())
        finally:
            if cur:
                await cur.close()
            # 释放掉conn,将连接放回到连接池中
            await self.pool.release(conn)

    async def execute_many(self, query, param=None):
        """
        批量 增删改 操作
        :param query: sql语句
        :param param: 参数
        :return:
        """
        conn, cur = await self.get_curosr()
        try:
            await cur.executemany(query, param)
            if cur.rowcount == 0:
                return False
            else:
                return True
        except:
            logobj.error(traceback.format_exc())
        finally:
            if cur:
                await cur.close()
            # 释放掉conn,将连接放回到连接池中
            await self.pool.release(conn)
