# -*- coding:utf-8 -*-
# Author: ShiWenWen
from flask import Flask, g
from redisdb import RedisCli


__all__ = ['app']
app = Flask(__name__)


def get_conn():
    if not hasattr(g, 'redis'):
        g.redis = RedisCli()
    return g.redis


@app.route('/')
def index():
    return '<h1>Welcome to Proxy Pool System</h1>'


@app.route('/random')
def get_proxy():
    """
    获取随机可用代理
    :return: 随机代理
    """
    return get_conn().random()


@app.route('/count')
def get_counts():
    """
    获取代理池总量
    :return: 代理池总量
    """
    return str(get_conn().count())


if __name__ == '__main__':
    app.run()



