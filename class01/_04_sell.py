
# 接入卖出操作

# 例子：入场持有 5 根 bar 后（在第 6 根 bar 上）退出，无论是盈利还是亏损。
# 翻译过来就是如果有持有的，持有时间超过5根bar，一般是五个交易日，第六天卖掉
# 规定在未入场时可以买入订单，如果持仓或者有进行中的订单都不能再买入

# 订单状态通过 order.status 获取
# 使用 notify_order() 这个方法监控订单的状态

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime
import os.path
import sys
import backtrader as bt

class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None           # 初始化订单

    # 每次订单状态发生变化，调用该方法
    def notify_order(self, order):
        """
        order.status 获取订单状态，状态一共有：
        Accepted（已接受）、Submitted（已提交）、Completed（已成交）、Margin（保证金不足）、Rejected（已拒绝）
        """
        # 订单处于这两种状态说明还在处理中，未完成
        if order.status in [order.Submitted, order.Accepted]:
            return

        # 对于已成交的订单，要区分是购买还是卖出
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

            # self.bar_executed 订单完成时的长度
            # len(self) 当前到了哪根bar
            # 不管是买还是卖，一定做了操作，并且成交，记录下位置
            self.bar_executed = len(self)

        # 这个情况下订单根本没完成，属于无效订单
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def next(self):
        self.log('Close, %.2f' % self.dataclose[0])

        if self.order:
            return

        # 没有持仓，准备入场，入场的逻辑还是连续两个交易日下跌就入
        if not self.position:
            if self.dataclose[0] < self.dataclose[-1]:
                if self.dataclose[-1] < self.dataclose[-2]:
                    self.log('BUY CREATE, %.2f' % self.dataclose[0])
                    self.order = self.buy()
        # 如果有持仓，看看是不是满足退场的条件
        else:
            if len(self) >= (self.bar_executed + 5):
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.sell()

def start():
    # 初始化引擎
    cerebro = bt.Cerebro()
    # 加载策略
    cerebro.addstrategy(TestStrategy)

    # 加载数据源
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, 'data/data01.txt')
    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        fromdate=datetime.datetime(2000, 1, 1),
        todate=datetime.datetime(2000, 12, 31),
        reverse=False)
    cerebro.adddata(data)
    #设置初始资金
    cerebro.broker.setcash(100000.0)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

if __name__ == '__main__':
    start()