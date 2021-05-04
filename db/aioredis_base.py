# -*- coding: utf-8 -*-
import aioredis


class DBAioRedis:

    def __init__(self):
        self.pool = None

    async def init_pool(self):
        if not self.pool:
            self.pool = await aioredis.create_redis_pool(
                ('127.0.0.1', 6379),
                db=7,
                password="foobared",
                encoding='utf-8')
        return self.pool

    async def close(self):
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()

    async def excute(self, key, member):
        pass
