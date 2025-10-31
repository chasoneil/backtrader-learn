
# 运行一个 backtrader 实例

import backtrader as bt

# 创建一个最简单的backtrader
def start():
    # 初始化引擎
    cerebro = bt.Cerebro()

    cerebro.broker.setcash(100000.0)    # 设置初始化资金

    # 初始化持仓组合资金
    print('start: %.2f' % cerebro.broker.getvalue())
    # 运行策略
    cerebro.run()
    # 输出投资后的资金
    print('after: %.2f' % cerebro.broker.getvalue())

if __name__ == '__main__':
    start()


