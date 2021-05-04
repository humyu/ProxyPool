# -*- coding: utf-8 -*-
import random

from aioredis_base import DBAioRedis
from custom_error import PoolEmptyError

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
        score_str = await r.zscore(REDIS_KEY, proxy)
        if not score_str:
            await r.zadd(REDIS_KEY, score, proxy)
    finally:
        r.close()
        await r.wait_closed()


async def get():
    """
    随机获取有效代理
    """
    r = await get_aio_redis()
    try:
        ret_list = await r.zrangebyscore(REDIS_KEY, MAX_SCORE, MAX_SCORE)
        if len(ret_list):
            return random.choice(ret_list)
        else:
            result = await r.zrevrange(REDIS_KEY, 0, -1)
            if len(result):
                return random.choice(result)
            else:
                raise PoolEmptyError("代理池暂无ip")
    finally:
        r.close()
        await r.wait_closed()


async def decrease(proxy):
    """
    代理值减一分，小于最小值则删除
    """
    r = await get_aio_redis()
    try:
        score_str = await r.zscore(REDIS_KEY, proxy)
        if score_str and score_str > MIN_SCORE:
            # print(' 代理 ', proxy, ' 当前分数 ', score_str, ' 减 1')
            await r.zincrby(REDIS_KEY, -1, proxy)
        else:
            # print(' 代理 ', proxy, ' 当前分数 ', score_str, ' 移除 ')
            await r.zrem(REDIS_KEY, proxy)
    finally:
        r.close()
        await r.wait_closed()


async def exists(proxy):
    """
    判断是否存在
    """
    r = await get_aio_redis()
    try:
        score_str = await r.zscore(REDIS_KEY, proxy)
        return score_str if not score_str else None
    finally:
        r.close()
        await r.wait_closed()


async def max(proxy):
    """
    将代理设置为 MAX_SCORE
    """
    r = await get_aio_redis()
    try:
        await r.zadd(REDIS_KEY, MAX_SCORE, proxy)
    finally:
        r.close()
        await r.wait_closed()


async def count():
    """
    获取数量
    """
    r = await get_aio_redis()
    try:
        await r.zcard(REDIS_KEY)
    finally:
        r.close()
        await r.wait_closed()


async def all():
    """
    获取全部代理
    """
    r = await get_aio_redis()
    try:
        ret_list = await r.zrangebyscore(REDIS_KEY, MIN_SCORE, MAX_SCORE)
        return ret_list
    finally:
        r.close()
        await r.wait_closed()
