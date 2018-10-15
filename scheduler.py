# -*- coding:utf-8 -*-
# Author: ShiWenWen
from multiprocessing import Process
from api import app
from getter import Getter
from tester import Tester
import time

# 测试周期
TESTER_CYCLE = 20
# 获取周期
GETTER_CYCLE = 20

# 是否允许测试服务
TESTER_ENABLED = True
# 是否允许获取服务
GETTER_ENABLED = True
# 是否启动api服务
API_ENABLED = True


class Scheduler:
    def schedule_tester(self, cycle=TESTER_CYCLE):
        """
        定时测试代理
        :param cycle: 定时时间
        """
        tester = Tester()
        while True:
            print('测试器运行')
            tester.run()
            time.sleep(cycle)

    def schedule_getter(self, cycle=GETTER_CYCLE):
        """
        定时获取代理
        :param cycle:
        """
        getter = Getter()
        while True:
            print('开始定时获取代理')
            getter.run()
            time.sleep(cycle)

    def schedule_api(self):
        """
        开启api
        :return:
        """
        app.run()

    def run(self):
        print('代理池调度器开始运行')
        if GETTER_ENABLED:
            getter_process = Process(target=self.schedule_getter)
            getter_process.start()
        if TESTER_ENABLED:
            tester_process = Process(target=self.schedule_tester)
            tester_process.start()
        if API_ENABLED:
            api_process = Process(target=self.schedule_api)
            api_process.run()


if __name__ == '__main__':
    Scheduler().run()

