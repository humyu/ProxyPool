# -*- coding: utf-8 -*-
import aioredis


class DBAioRedis:

    def __init__(self):
        self.pool = None

    async def init_pool(self):
        if not self.pool:
            self.pool = aioredis.ConnectionPool.from_url(
                "redis://default:foobared@localhost:6379/7",
                encoding="utf-8",
                decode_responses=True
            )
        return self.pool

    async def close(self):
        # if self.pool:
        #     self.pool.close()
        #     await self.pool.wait_closed()
        pass

    async def excute(self, key, member):
        pass
