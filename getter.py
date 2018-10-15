# -*- coding:utf-8 -*-
# Author: ShiWenWen
from pyquery import PyQuery as pq
import requests
from redisdb import RedisCli

# 基础请求头
BASE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7'
}

# 代理池最大数量
POOL_UPPER_THRESHOLD = 10000


class Crawler:
    def get_proxies(self, crawl_name):
        '''
        通过代理爬取名获取代理 如crawl_dailli66
        :param crawl_name: 爬取代理的方法名
        :return: 代理
        '''
        proxies = []
        for proxy in eval('self.%s()' % crawl_name):
            # 获取代理成
            proxies.append(proxy)
        return proxies

    def get_page(self, url, options={}):
        """
        获取网页
        :param url:
        :param options:
        :return:
        """
        headers = dict(BASE_HEADERS, **options)
        print('正在抓取', url)
        try:
            response = requests.get(url, headers=headers)
            print('抓取成功', url, response.status_code)
            if response.status_code == 200:
                return response.text
        except Exception as e:
            print('抓取失败', e, url)
        return None

    def get_all_crawl_func(self):
        '''
        获取所有爬取代理源的方法
        :return:
        '''
        funcs = []
        for attr in dir(self):
            if attr.startswith('crawl_'):
                funcs.append(attr)
        return funcs

    def crawl_dailli66(self, page_count=4):
        '''
        爬取66免费代理网
        :param page_count: 爬取的页数
        :return: 代理
        '''
        start_url = 'http://www.66ip.cn/{}.html'
        urls = [start_url.format(page) for page in range(1, page_count + 1)]
        for url in urls:
            print('爬取', url)
            html = self.get_page(url)
            if html:
                doc = pq(html)
                trs = doc('.containerbox table tr:gt(0)').items()
                for tr in trs:
                    ip = tr.find('td:nth-child(1)').text()
                    port = tr.find('td:nth-child(2)').text()
                    yield ':'.join([ip, port])

    # ...爬取其他网站的


class Getter:
    def __init__(self):
        # 初始化代理池和代理源爬取
        self.redis = RedisCli()
        self.crawler = Crawler()

    def is_over_thershold(self):
        '''
        判断是否达到代理池最大限制
        :return: 是否达到代理池最大限制
        '''
        return self.redis.count() >= POOL_UPPER_THRESHOLD

    def run(self):
        '''
        获取代理源 存入代理池
        :return:
        '''
        if not self.is_over_thershold():
            for crawl_fun in self.crawler.get_all_crawl_func():
                proxies = self.crawler.get_proxies(crawl_fun)
                for proxy in proxies:
                    self.redis.add(proxy)


if __name__ == '__main__':
    # 执行测试
    # print(Crawler().get_proxies('crawl_dailli66'))
    Getter().run()


