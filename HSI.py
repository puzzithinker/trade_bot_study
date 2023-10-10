import backtrader as bt
import yfinance as yf

# Define a simple moving average crossover strategy
class SmaCross(bt.Strategy):
    params = (('pfast', 50), ('pslow', 200),)

    def __init__(self):
        sma1 = bt.ind.SMA(period=self.p.pfast)
        sma2 = bt.ind.SMA(period=self.p.pslow)
        self.crossover = bt.ind.CrossOver(sma1, sma2)

    def next(self):
        if not self.position:  # not in the market
            if self.crossover > 0:  # fast crosses slow to the upside
                self.buy()  # enter long
        elif self.crossover < 0:  # in the market & cross to the downside
            self.close()  # close long position

# Fetch Hang Seng Index data
data = yf.download('^HSI', start='2010-01-01', end='2023-10-10')
data = bt.feeds.PandasData(dataname=data)

# Create a backtester
cerebro = bt.Cerebro()

# Add the data feed
cerebro.adddata(data)

# Add the strategy
cerebro.optstrategy(SmaCross, pfast=range(10, 100, 10), pslow=range(100, 200, 20))

# Set the starting cash
cerebro.broker.setcash(100000.0)

# Set the commission - 0.1% ... divide by 100 to remove the %
cerebro.broker.setcommission(commission=0.001)

# Add Sharpe Ratio
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio')

# Run the backtest
results = cerebro.run(maxcpus=1)

# Keep track of the best parameters and the highest Sharpe Ratio
best_params = None
highest_sharpe = None

# Evaluate the results
for res in results:
    sharpe = res[0].analyzers.sharpe_ratio.get_analysis()['sharperatio']
    if highest_sharpe is None or sharpe > highest_sharpe:
        highest_sharpe = sharpe
        best_params = (res[0].params.pfast, res[0].params.pslow)

print(f'Best Parameters: Fast SMA Period={best_params[0]}, Slow SMA Period={best_params[1]}')
print(f'Highest Sharpe Ratio: {highest_sharpe}')