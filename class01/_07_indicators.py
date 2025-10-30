# 本篇研究技术指标 indicators 的用法
# 主要研究 SimpleMovingAverage SMA 指标 这个均线可以反映一段时间的价格均值
# 计算方法都在indicators.py文件中

import datetime
import os.path
import sys
import backtrader as bt

class TestStrategy(bt.Strategy):
    params = (
        ('maperiod', 15),       # 配置SMA的周期是15天
    )

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.buyprice = None
        self.buycomm = None
        # 配置SMA指标  但是只是这一句就能动态计算均线SMA的值吗? todo
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.maperiod)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        self.log('Close, %.2f' % self.dataclose[0])

        if self.order:
            return

        if not self.position:
            # 如果当天收盘价大于SMA均线，买入
            if self.dataclose[0] > self.sma[0]:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy()
        else:
            # 如果当天收盘价小于SMA均线，卖出
            if self.dataclose[0] < self.sma[0]:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.sell()

def start():
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TestStrategy)

    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, 'data/data01.txt')

    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        fromdate=datetime.datetime(2000, 1, 1),
        todate=datetime.datetime(2000, 12, 31),
        reverse=False)

    cerebro.adddata(data)
    cerebro.broker.setcash(1000.0)

    """
    这行代码的作用是为策略添加一个仓位管理器。仓位管理器决定了每次交易中买入或卖出的股票数量。
    bt.sizers.FixedSize 是一个内置的仓位管理器，它会在每次交易中买入或卖出固定数量的股票。
    stake=10 表示每次交易买入或卖出10股股票。这意味着无论市场的波动如何，每次开仓时都会买入或卖出10股。 
    """
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)
    cerebro.broker.setcommission(commission=0.0)        # 本策略不考虑佣金

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

if __name__ == '__main__':
    start()