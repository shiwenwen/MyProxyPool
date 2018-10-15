# -*- coding:utf-8 -*-
# Author: ShiWenWen
from redisdb import RedisCli
import aiohttp
from aiohttp import ClientError, ClientConnectionError, ServerTimeoutError
import asyncio
import time
from asyncio import TimeoutError

# 测试认为有效的状态码
VALID_STATUS_CODES = [200]
# 测试网站
TEST_URL = 'http://www.baidu.com'

# 每次批量测试的数量
BATCH_TEST_SIZE = 100


class Tester:
    def __init__(self):
        self.redis = RedisCli()

    async def test_single_proxy(self, proxy):
        '''
        测试单个代理
        :param proxy: 代理
        :return: 测试结果
        '''
        conn = aiohttp.TCPConnector(verify_ssl=False)
        async with aiohttp.ClientSession(connector=conn) as session:
            try:
                if isinstance(proxy, bytes):
                    proxy = proxy.decode('utf-8')
                real_proxy = 'http://' + proxy
                print('正在测试代理', real_proxy)
                async with session.get(TEST_URL, proxy=real_proxy, timeout=15) as response:
                    if response.status in VALID_STATUS_CODES:
                        # 如果代理可用，分数置为最高
                        self.redis.max(proxy)
                        print('代理%s可用' % proxy)
                        return True
                    else:
                        # 如果代理不可用，分数减一
                        self.redis.decrease(proxy)
                        print('请求响应码不合理，代理不可用', proxy)
                        return False
            except (ClientError, ClientConnectionError, ServerTimeoutError, AttributeError, TimeoutError):
                self.redis.decrease(proxy)
                print('代理请求失败,不可用', proxy)
                return False

    def run(self):
        try:
            proxies = self.redis.all()
            loop = asyncio.get_event_loop()
            # 批量测试
            for i in range(0, len(proxies), BATCH_TEST_SIZE):
                test_proxies = proxies[i: i + BATCH_TEST_SIZE]
                tasks = [self.test_single_proxy(proxy) for proxy in test_proxies]
                loop.run_until_complete(asyncio.wait(tasks))
                # 睡眠五秒钟
                time.sleep(5)
        except Exception as e:
            print('测试错误', e)


if __name__ == '__main__':
    # 测试代码
    Tester().run()


