# -*- coding: utf-8 -*-
import requests
import random
import logging

from requests import RequestException

test_url = 'http://httpbin.org/get'  # 测试ip是否可用的 url
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/86.0.4240.193 Safari/537.36'}


def test_proxy(proxy):
    proxies = {
        'http': f'http://{proxy}',
        'https': f'https://{proxy}',
    }
    try:
        resp = requests.get(url=test_url, proxies=proxies, headers=headers, timeout=10)
        return resp.status_code
    except RequestException as e:
        logging.exception(e)
        return e.args


def get_proxies():
    with open('ip_in_file.txt', 'r') as f:
        ips = [line.strip() for line in f]
    # ips = list(filter(None, result))
    return ips


def ip_select():
    ips = get_proxies()
    while True:
        ip = random.choice(ips)
        result = test_proxy(ip)
        if result != 200:
            continue
    return result
