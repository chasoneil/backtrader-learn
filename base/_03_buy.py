

# 接入买入操作 策略: 如果连续两天下跌, 则买入

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

    # 第一个策略，连续两天下跌即买入
    def next(self):
        self.log('Close, %.2f' % self.dataclose[0])

        # 如果连续两天下跌
        if self.dataclose[0] < self.dataclose[-1]:
            if self.dataclose[-1] < self.dataclose[-2]:
                # 输出买入的价格，其实就是当天的收盘价
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                """
                默认情况下，self.buy()会买入尽可能多的股票或资产，直到账户中的资金不足以购买更多为止。
                如果需要指定买入的数量，可以使用size参数，例如self.buy(size=100)表示买入100股。
                如果需要指定买入的资金量，可以使用size参数并设置为None，同时使用exectype=bt.Order.Market或exectype=bt.Order.Limit等参数来指定订单类型，并通过price参数指定价格，但资金量需要通过其他方式计算得出。
                """
                self.buy()

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
    cerebro.broker.setcash(100000.0)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

if __name__ == '__main__':
    start()