import backtrader as bt
import backtrader.feeds as btfeeds
import yfinance as yf

data = yf.download('^GSPC', start='2010-01-01', end='2023-10-01', interval='1mo')

data_feed = btfeeds.PandasData(dataname=data)

class MovingAverageStrategy(bt.Strategy):
    params = (('short_period', 3), ('long_period', 6))

    def __init__(self):
        self.sma_short = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.short_period)
        self.sma_long = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.long_period)

    def next(self):
        if self.sma_short > self.sma_long and not self.position:
            self.buy()  # Enter long position
        elif self.sma_short < self.sma_long and self.position:
            self.sell()  # Exit long position

def run_backtest():
	cerebro = bt.Cerebro()
	cerebro.adddata(data_feed)
	cerebro.addstrategy(MovingAverageStrategy)
	cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='annual_return')
	cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trade_analyzer')
	cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
	cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='timereturn')
	cerebro.addanalyzer(bt.analyzers.VWR, _name='vwr')
	cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')
	cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
	cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
	cerebro.broker.setcash(100000.0)
	results = cerebro.run()
	sharpe_ratio = results[0].analyzers.sharpe.get_analysis()['sharperatio']
	print('Sharpe Ratio:', sharpe_ratio)
	print('Annual Return:', results[0].analyzers.annual_return.get_analysis())
	print('Trade Analysis:', results[0].analyzers.trade_analyzer.get_analysis())
	print('Drawdown:', results[0].analyzers.drawdown.get_analysis())
	print('Time Return:', results[0].analyzers.timereturn.get_analysis())
	print('VWR:', results[0].analyzers.vwr.get_analysis())
	print('SQN:', results[0].analyzers.sqn.get_analysis())

run_backtest()