import backtrader as bt
import backtrader.feeds as btfeeds
import yfinance as yf

# Download historical data
data = yf.download('^GSPC', start='2010-01-01', end='2023-10-01', interval='1mo')
data['openinterest'] = 0

# Convert downloaded data to a Backtrader feed
data_feed = btfeeds.PandasData(dataname=data)


# Define the trading strategy
class TradingStrategy(bt.Strategy):
    params = (('sma1', 20), ('sma2', 50), ('rsi', 30), ('macd1', 12), ('macd2', 26), ('macdsig', 9))

    def __init__(self):
        self.sma1 = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.sma1)
        self.sma2 = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.sma2)
        self.rsi = bt.indicators.RelativeStrengthIndex(self.data.close, period=self.params.rsi)
        self.macd = bt.indicators.MACD(self.data.close, period_me1=self.params.macd1, period_me2=self.params.macd2, period_signal=self.params.macdsig)

    def notify_trade(self, trade):
        if trade.isclosed:
            print('Operation profit, gross %.2f, net %.2f' % (trade.pnl, trade.pnlcomm))

    def next(self):
        if not self.position:
            if self.sma1 > self.sma2 and self.rsi < 30 and self.macd.macd > self.macd.signal:
                self.buy()
        else:
            if self.sma1 < self.sma2 and self.rsi > 70 and self.macd.macd < self.macd.signal:
                self.sell()



# Initialize the Backtrader engine
cerebro = bt.Cerebro()

# Add the data feed and strategy to the engine
cerebro.adddata(data_feed)
cerebro.addstrategy(TradingStrategy)

# Add analyzers
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio')
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

# Run the backtest
cerebro.broker.setcash(100000.0)
results = cerebro.run()

# Print the results
print('Sharpe Ratio:', results[0].analyzers.sharpe_ratio.get_analysis())
print('Drawdown:', results[0].analyzers.drawdown.get_analysis())
print('Trades:', results[0].analyzers.trades.get_analysis())
