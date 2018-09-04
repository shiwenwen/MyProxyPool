# -*- coding:utf-8 -*-
# Author: ShiWenWen
import redis
from random import choice
import re

# ============= 分数配置 =================
# 最大分数
MAX_SCORE = 100
# 最小分数
MIN_SCORE = 50
# 初始分数
INIT_SCORE = 60

# ============= redis配置 =================
# 主机
REDIS_HOST = 'localhost'
# 端口
REDIS_PORT = 6379
# 密码
REDIS_PASSWORD = None
# 键
REDIS_KEY = 'proxies'


class RedisCli:
    def __init__(self, host=REDIS_HOST, port = REDIS_PORT, password = REDIS_PASSWORD):
        '''
        初始化
        :param host: redis地址
        :param port: redis端口
        :param password: redis密码
        '''
        self.db = redis.StrictRedis(host=host, port=port, password=password, decode_responses=True)

    def add(self, proxy, score=INIT_SCORE):
        '''
        添加代理，设置默认分数
        :param proxy: 代理
        :param score: 分数
        :return: 添加结果
        '''
        # 正则匹配代理格式是否正确
        if not re.match(r'\d+.\d+.\d+.\d+:\d+', proxy):
            print('代理 %s 无效 ==> 丢弃' % proxy)
            return
        # 判断代理池中是否已经存在
        if not self.db.zscore(REDIS_KEY, proxy):
            # 添加代理
            print('新增代理 %s ' % proxy)
            return self.db.zadd(REDIS_KEY, score, proxy)

    def random(self):
        '''
        随机获取有效代理
        :return: 随机代理
        '''
        # 尝试获取最高分数的代理集合
        result = self.db.zrangebyscore(REDIS_KEY,MAX_SCORE,MAX_SCORE)
        if len(result):
            # 如果有最高分数的代理，随机选择返回
            return choice(result)
        else:
            # 获取分数排名前一百的代理
            result = self.db.zrevrange(REDIS_KEY, 0, 100)
            if len(result):
                # 如果有，随机返回
                return choice(result)
            else:
                return None

    def decrease(self, proxy):
        '''
        将代理值减一分，分数小于最小值时，移除代理。
        :param proxy: 代理
        :return: 修改后的代理分数
        '''
        score = self.db.zscore(REDIS_KEY, proxy)
        if score and score > MIN_SCORE:
            # 如果分数大于最低分，将分数减一
            print('代理 %s 当前分数 %d ==> 减1 ==> %d' % (proxy, score, score - 1))
            return self.db.zincrby(REDIS_KEY, proxy, -1)
        else:
            # 否则移除代理
            print('代理 %s 当前分数 %d ==> 移除' % (proxy, score))
            return self.db.zrem(REDIS_KEY, proxy)

    def exists(self, proxy):
        '''
        代理是否存在
        :param proxy: 代理
        :return: 是否存在
        '''
        return self.db.zscore(REDIS_KEY, proxy) is not None

    def set_max(self, proxy):
        '''
        将代理设置为最大分数
        :param proxy: 代理
        :return: 设置结果
        '''
        print('代理 %s 可用 ==> 设置为 %d' % (proxy, MAX_SCORE))
        return self.db.zadd(REDIS_KEY, MAX_SCORE, proxy)

    def count(self):
        '''
        获取代理数量
        :return: 数量
        '''
        return self.db.zcard(REDIS_KEY)

    def all(self):
        '''
        获取全部代理
        :return: 全部代理
        '''
        return self.db.zrangebyscore(REDIS_KEY, MIN_SCORE, MAX_SCORE)


if __name__ == '__main__':
    # 进行一些测试
    redis_cli = RedisCli()
    proxy = '118.25.220.214:3128'
    redis_cli.add(proxy)
    redis_cli.set_max(proxy)
    redis_cli.decrease(proxy)
    print(redis_cli.exists(proxy))
    print(redis_cli.count())
    print(redis_cli.all())
    redis_cli.add('140.227.60.114:3128')
    redis_cli.add('213.128.7.72:53281')
    redis_cli.add('37.187.149.129:1080')
    redis_cli.set_max('140.227.60.114:3128')
    print(redis_cli.random())

