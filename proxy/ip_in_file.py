# -*- coding: utf-8 -*-
import asyncio
import sys

import aiofiles

sys.path.append("..")
from db import aioredis_op


async def run():
    async with aiofiles.open("代理.txt", 'r') as f:
        data_list = await f.readlines()
    for data in data_list:
        data = data.strip()
        await aioredis_op.add(data)


if __name__ == '__main__':
    asyncio.run(run())
