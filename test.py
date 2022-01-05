# -*- coding: utf-8 -*-
import asyncio

from proxy import ip_aiodb
from web_session import WebSession


async def close():
    # run this before the app ends
    await WebSession.close()


if __name__ == '__main__':
    # 创建会话
    if WebSession.session is None:
        session = WebSession.create()
    else:
        session = WebSession.session

    task = asyncio.ensure_future(ip_aiodb.update(session))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(task)
    loop.run_until_complete(close())
