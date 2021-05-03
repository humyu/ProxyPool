# -*- coding: utf-8 -*-
import random

from aio_redis_base import DBAioRedis
from db.custom_error import PoolEmptyError

MAX_SCORE = 20
MIN_SCORE = 0
INITIAL_SCORE = 5
REDIS_KEY = 'proxies'


async def get_aio_redis():
    redis = DBAioRedis()
    r = await redis.init_pool()
    return r


async def add(proxy, score=INITIAL_SCORE):
    """
    添加代理
    """
    r = await get_aio_redis()
    try:
        if not r.zscore(REDIS_KEY, proxy):
            return r.zadd(REDIS_KEY, score, proxy)
    finally:
        r.close()
        await r.wait_closed()


async def get():
    """
    随机获取有效代理
    """
    r = await get_aio_redis()
    try:
        result = r.zrangebyscore(REDIS_KEY, MAX_SCORE, MAX_SCORE)
        if len(result):
            return random.choice(result)
        else:
            result = r.zrevrange(REDIS_KEY, 0, -1)
            if len(result):
                return random.choice(result)
            else:
                raise PoolEmptyError("代理池暂无ip")
    finally:
        r.close()
        await r.wait_closed()


async def update(proxy):
    """
    代理值减一分，小于最小值则删除
    """
    r = await get_aio_redis()
    try:
        score = r.zscore(REDIS_KEY, proxy)
        if score and score > MIN_SCORE:
            print(' 代理 ', proxy, ' 当前分数 ', score, ' 减 1')
            return r.zincrby(REDIS_KEY, proxy, -1)
        else:
            print(' 代理 ', proxy, ' 当前分数 ', score, ' 移除 ')
            return r.zrem(REDIS_KEY, proxy)
    finally:
        r.close()
        await r.wait_closed()


async def exists(proxy):
    """
    判断是否存在
    """
    r = await get_aio_redis()
    try:
        return not r.zscore(REDIS_KEY, proxy) is None
    finally:
        r.close()
        await r.wait_closed()


async def max(proxy):
    """
    将代理设置为 MAX_SCORE
    """
    r = await get_aio_redis()
    try:
        return r.zadd(REDIS_KEY, MAX_SCORE, proxy)
    finally:
        r.close()
        await r.wait_closed()


async def count():
    """
    获取数量
    """
    r = await get_aio_redis()
    try:
        return r.zcard(REDIS_KEY)
    finally:
        r.close()
        await r.wait_closed()


async def all():
    """
    获取全部代理
    """
    r = await get_aio_redis()
    try:
        return r.zrangebyscore(REDIS_KEY, MIN_SCORE, MAX_SCORE)
    finally:
        r.close()
        await r.wait_closed()
