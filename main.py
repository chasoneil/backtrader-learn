# backtrader 学习框架

import backtrader as bt

def print_hi(name):
    print(f'Hi, {name}')  # 按 Ctrl+F8 切换断点。


# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
    print_hi('PyCharm')

# 构建策略

class MyStrategy(bt.Strategy):

    # 全局参数设置
    params = ()

    # 初始化
    def __init__(self):
        self.order = None

    # 这个会针对每个数据进行策略计算
    # 例如使用昨天的收盘价和今天的开盘价

    def next(self):
        pass