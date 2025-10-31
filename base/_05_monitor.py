import datetime
import os.path
import sys

import backtrader as bt

class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    # 策略初始化
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.buyprice = None        # 买入价格
        self.buycomm = None         # 佣金

    def notify_order(self, order):
        # 未完成的订单不管他
        if order.status in [order.Submitted, order.Accepted]:
            return

        # 完成的订单监控状态
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    '买入执行，价格：%.2f，成本：%.2f，佣金 %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log('卖出执行，价格：%.2f，成本：%.2f，佣金 %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单取消/保证金不足/拒绝')

        self.order = None

    # 每成交一笔记录，执行一次
    def notify_trade(self, trade):
        # 当交易没被关闭的时候
        if not trade.isclosed:
            return
        # 交易已经结束
        self.log('利润记录，毛利润 %.2f，净利润 %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        self.log('收盘价，%.2f' % self.dataclose[0])
        # 如果不是空证明当前正在有订单交易，不再下单
        if self.order:
            return

        # 如果没有持仓，创建买入订单
        if not self.position:
            if self.dataclose[0] < self.dataclose[-1]:
                if self.dataclose[-1] < self.dataclose[-2]:
                    self.log('创建买入订单，%.2f' % self.dataclose[0])
                    self.order = self.buy()
        # 如果有持仓，看看到没到卖出的条件
        else:
            if len(self) >= (self.bar_executed + 5):
                self.log('创建卖出订单，%.2f' % self.dataclose[0])
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
    cerebro.broker.setcash(100000.0)
    # 设置佣金是 0.1%
    cerebro.broker.setcommission(commission=0.001)

    print('初始投资组合价值：%.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('最终投资组合价值：%.2f' % cerebro.broker.getvalue())

if __name__ == '__main__':
    start()