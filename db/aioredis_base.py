# -*- coding: utf-8 -*-
import aioredis


class DBAioRedis:
    pool = None

    @classmethod
    async def init_pool(cls):
        cls.pool = aioredis.ConnectionPool.from_url(
            "redis://default:foobared@localhost:6379/7",
            encoding="utf-8",
            decode_responses=True
        )
        print(f"统一连接池: {cls.pool}")
        return cls.pool

    @classmethod
    async def close(cls):
        if cls.pool is not None:
            await cls.pool.disconnect()

    async def excute(self, key, member):
        pass
