# -*- coding: utf-8 -*-
import asyncio

from proxy import detect
from web_session import WebSession
from proxy import ip3366
from proxy import kuaidaili


async def close():
    # run this before the app ends
    await WebSession.close()


if __name__ == '__main__':
    # 创建会话
    if WebSession.session is None:
        session = WebSession.create()
    else:
        session = WebSession.session

    task = asyncio.ensure_future(detect.update(session))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(task)
    loop.run_until_complete(close())
    loop.close()
