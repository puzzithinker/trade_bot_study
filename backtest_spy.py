import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.base import BaseEstimator
from sklearn.model_selection import ParameterGrid

class CombinedStrategy(BaseEstimator):
    def __init__(self, short_window=40, long_window=100, bollinger_period=20, num_std=2, rsi_period=14, rsi_upper=70, rsi_lower=30):
        self.short_window = short_window
        self.long_window = long_window
        self.bollinger_period = bollinger_period
        self.num_std = num_std
        self.rsi_period = rsi_period
        self.rsi_upper = rsi_upper
        self.rsi_lower = rsi_lower

    def fit(self, X, y=None):
        return self

    def calculate_RSI(self, data, window): 
        diff = data.diff(1)
        up_chg = 0 * diff
        down_chg = 0 * diff
        
        up_chg[diff > 0] = diff[ diff>0 ]
        down_chg[diff < 0] = diff[ diff < 0 ]
        
        up_chg_avg   = up_chg.rolling(window).mean()
        down_chg_avg = down_chg.abs().rolling(window).mean()
        
        rs = abs(up_chg_avg/down_chg_avg)
        rsi = 100 - 100/(1+rs)
        return rsi

    def predict(self, X):
        close_prices = X['Close'].values

        short_ma = np.array([np.mean(close_prices[i - self.short_window + 1: i + 1]) 
                             if i >= self.short_window else np.mean(close_prices[:i + 1]) 
                             for i in range(close_prices.shape[0])])

        long_ma = np.array([np.mean(close_prices[i - self.long_window + 1: i + 1]) 
                            if i >= self.long_window else np.mean(close_prices[:i + 1]) 
                            for i in range(close_prices.shape[0])])

        rolling_mean = short_ma
        rolling_std = np.array([np.std(close_prices[i - self.bollinger_period + 1: i + 1]) 
                                if i >= self.bollinger_period else np.std(close_prices[:i + 1]) 
                                for i in range(close_prices.shape[0])])

        upper_band = rolling_mean + self.num_std * rolling_std
        lower_band = rolling_mean - self.num_std * rolling_std
        rsi = self.calculate_RSI(X['Close'], self.rsi_period)

        ma_signals = np.where(short_ma > long_ma, 1.0, -1.0)
        bollinger_signals = np.where(close_prices > upper_band, -1.0, np.where(close_prices < lower_band, 1.0, 0.0))
        rsi_signals = np.where(rsi > self.rsi_upper, -1.0, np.where(rsi < self.rsi_lower, 1.0, 0.0))

        signals = np.sign(ma_signals + bollinger_signals + rsi_signals)
        positions = np.diff(signals)

        returns = np.diff(close_prices) / close_prices[:-1] * positions
        cumulative_returns = np.cumprod(1 + returns)

        return cumulative_returns[-1]

df = yf.download('SPY', start='2010-01-01', end='2023-10-10')
X = df[['Close']]

param_grid = {'short_window': range(20, 60), 'long_window': range(80, 120), 
              'bollinger_period': range(10, 30), 'num_std': np.arange(1, 3, 0.1), 
              'rsi_period': range(10, 20), 'rsi_upper': np.arange(60, 80, 5), 'rsi_lower': np.arange(20, 40, 5)}

param_list = list(ParameterGrid(param_grid))

best_score = float('-inf')
best_params = None

for params in param_list:
    strategy = CombinedStrategy(**params)
    strategy.fit(X)
    score = strategy.predict(X)
    if score > best_score:
        best_score = score
        best_params = params

print(best_params)