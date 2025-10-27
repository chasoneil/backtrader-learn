import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import backtrader as bt


def start():
    #instantiated Cerebro engine
    cerebro = bt.Cerebro()

    #get absolute path value of running script (can be another script which call the function)
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))

    #save data file under same folder with this script and get the path value of data file
    datapath = os.path.join(modpath, 'data/data01.txt')

    #use feeds.YahhoFinanceCSVData method to read YF CSV data format file per given path, start date, end date and data order
    #as default, raw csv data download from yfinance is in date descending order, the model file already adjusted the date order to ascending order, thus set reverse = False
    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        fromdate=datetime.datetime(2000, 1, 1),
        todate=datetime.datetime(2000, 12, 31),
        reverse=False)

    cerebro.adddata(data)

    #set start cash value instead of using the default broker instance created by Cerebro engine
    cerebro.broker.setcash(100000.0)

    #print initial value
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    #run back test over data
    cerebro.run()

    #print result outcome
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.plot()

if __name__ == '__main__':
    start()