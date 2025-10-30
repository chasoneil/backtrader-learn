from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import backtrader as bt

class TestStrategy(bt.Strategy):
    params = (
        ('maperiod', 15),
    )

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod)

        # 创建一个周期为25的指数移动平均线（EMA）指标实例，并将其添加到策略中。EMA用于反映价格变化的加权平均，更加强调最近的价格数据。
        bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
        # 创建一个周期为25的加权移动平均线（WMA）指标实例，并将其添加到策略中。subplot=True表示这个指标将在一个新的子图中绘制。WMA也是一种加权平均线，但是它对所有数据点加权，权重随着数据点距离当前时间的远近递减。
        bt.indicators.WeightedMovingAverage(self.datas[0], period=25, subplot=True)
        # 创建一个慢速随机指标（Stochastic Slow）实例，并将其添加到策略中。这个指标用于衡量市场是否处于超买或超卖状态，以及价格的变化动量。
        bt.indicators.StochasticSlow(self.datas[0])
        # 创建一个MACD直方图（MACDHisto）指标实例，并将其添加到策略中。MACD直方图用于显示MACD线和信号线之间的差异，当直方图为正时，表示市场处于买入状态；当直方图为负时，表示市场处于卖出状态
        bt.indicators.MACDHisto(self.datas[0])
        # 创建一个相对强弱指数（RSI）指标实例，并将其赋值给变量rsi。RSI用于衡量市场的超买和超卖条件，通常RSI大于70表示超买，小于30表示超卖。
        rsi = bt.indicators.RSI(self.datas[0])
        # 创建一个周期为10的RSI的平滑移动平均线（Smoothed Moving Average of RSI）实例，并将其添加到策略中。这个平滑的RSI可以用来过滤掉RSI的短期波动，提供更稳定的买卖信号。
        bt.indicators.SmoothedMovingAverage(rsi, period=10)
        # 创建一个平均真实波幅（ATR）指标实例，并将其添加到策略中。plot=False表示这个指标不会在图表中绘制出来。ATR用于衡量市场的波动性，计算方法是取过去周期内最高价、最低价和前一天收盘价之间的最大值，然后计算14周期的简单移动平均。
        bt.indicators.ATR(self.datas[0], plot=False)

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
            if self.dataclose[0] > self.sma[0]:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy()
        else:
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
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)
    cerebro.broker.setcommission(commission=0.0)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # 展示图表信息
    cerebro.plot()

if __name__ == '__main__':
    start()