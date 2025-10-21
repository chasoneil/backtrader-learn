
# 配置数据源

import datetime
import os.path
import sys

import backtrader as bt

# 数据源的使用方法，这里使用的是CSV格式的数据
def start():
    cerebro = bt.Cerebro()

    # 获取数据文件目录
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, 'data/data01.txt')

    data = bt.feeds.YahooFinanceCSVData(
        dataname = datapath,
        fromdate = datetime.datetime(2000, 1, 1),
        todate = datetime.datetime(2000, 12, 31),
        # 控制数据是否逆序加载(最新的数据先加载)
        reverse = False
    )

    cerebro.adddata(data)
    cerebro.broker.setcash(100000.0)

    print('Start strategy: %.2f' % cerebro.broker.getvalue())

    cerebro.run()

    print('Finish strategy: %.2f' % cerebro.broker.getvalue())



if __name__ == '__main__':
    start()