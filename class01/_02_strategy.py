
# 添加策略

import datetime
import os.path
import sys

import backtrader as bt

def start():
    cerebro = bt.Cerebro()

    # 配置策略
    cerebro.addstrategy(MyStrategy)

    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, 'data/data01.txt')

    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        fromdate=datetime.datetime(2000, 1, 1),
        todate=datetime.datetime(2000, 12, 31),
        reverse=False
    )

    cerebro.adddata(data)
    cerebro.broker.setcash(100000.0)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

# 策略类 继承自 strategy
class MyStrategy(bt.Strategy):

    # 自定义的输出日志的方法
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    # 初始化
    # 将数据源中的收盘价赋值给dataclose
    def __init__(self):
        self.dataclose = self.datas[0].close

    # 策略启动 每个bar开始调用一次
    # 记录收盘价
    def next(self):
        self.log('Close, %.2f' % self.dataclose[0])


if __name__ == '__main__':
    start()

