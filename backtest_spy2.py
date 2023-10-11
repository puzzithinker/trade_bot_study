import pandas as pd
import yfinance as yf
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator, MACD, ADXIndicator
from ta.volume import OnBalanceVolumeIndicator
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
import warnings
warnings.filterwarnings('ignore')


# Fetch data
df = yf.download('SPY', start='2010-01-01', end='2023-10-10')

# Define a range of possible SMA, RSI, MACD, and ADX windows
sma_windows_slow = range(30, 61, 10)
sma_windows_fast = range(10, 31, 10)
rsi_windows = range(10, 31, 10)
macd_windows_slow = range(26, 36, 5)
macd_windows_fast = range(12, 17, 2)
adx_windows = range(14, 24, 2)
n_sign = 9

# Calculate OBV
obv = OnBalanceVolumeIndicator(df['Close'], df['Volume']).on_balance_volume()
df['obv'] = obv

# Placeholder for the best SMA, RSI, MACD, ADX windows and the corresponding best Sharpe ratio
best_sma_window_slow = None
best_sma_window_fast = None
best_rsi_window = None
best_macd_window_slow = None
best_macd_window_fast = None
best_adx_window = None
best_sharpe_ratio = None

# Loop over all possible SMA, RSI, MACD, ADX windows
for sma_window_slow in sma_windows_slow:
    for sma_window_fast in sma_windows_fast:
        if sma_window_slow <= sma_window_fast:
            continue
        for rsi_window in rsi_windows:
            for macd_window_slow in macd_windows_slow:
                for macd_window_fast in macd_windows_fast:
                    if macd_window_slow <= macd_window_fast:
                        continue
                    for adx_window in adx_windows:
                        # Calculate SMA, RSI, MACD, ADX using the current window
                        sma_slow = SMAIndicator(df['Close'], window=sma_window_slow).sma_indicator()
                        sma_fast = SMAIndicator(df['Close'], window=sma_window_fast).sma_indicator()
                        rsi = RSIIndicator(df['Close'], window=rsi_window).rsi()
                        macd = MACD(df['Close'], window_slow=macd_window_slow, window_fast=macd_window_fast, window_sign=n_sign).macd()
                        # Calculate ADX using the current window
                        adx = ADXIndicator(df['High'], df['Low'], df['Close'], window=adx_window).adx()

                        df['sma_slow'] = sma_slow
                        df['sma_fast'] = sma_fast
                        df['rsi'] = rsi
                        df['macd'] = macd
                        df['adx'] = adx

                        X = df[['sma_slow', 'sma_fast', 'rsi', 'macd', 'adx', 'obv']].dropna()  # Drop NaN values
                        y = df['Close'].loc[X.index]  # Align y with X

                        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

                        model = XGBRegressor(objective='reg:squarederror')
                        model.fit(X_train, y_train)

                        # Calculate the Sharpe ratio
                        returns = y_test - model.predict(X_test)
                        sharpe_ratio = returns.mean() / returns.std()

                        # If this Sharpe ratio is better than the best one we've seen so far, update the best SMA window and the best Sharpe ratio
                        if best_sharpe_ratio is None or sharpe_ratio > best_sharpe_ratio:
                            best_sma_window_slow = sma_window_slow
                            best_sma_window_fast = sma_window_fast
                            best_rsi_window = rsi_window
                            best_macd_window_slow = macd_window_slow
                            best_macd_window_fast = macd_window_fast
                            best_adx_window = adx_window
                            best_sharpe_ratio = sharpe_ratio

print(f"Best SMA window slow: {best_sma_window_slow}")
print(f"Best SMA window fast: {best_sma_window_fast}")
print(f"Best RSI window: {best_rsi_window}")
print(f"Best MACD window slow: {best_macd_window_slow}")
print(f"Best MACD window fast: {best_macd_window_fast}")
print(f"Best ADX window: {best_adx_window}")
print(f"Best Sharpe ratio: {best_sharpe_ratio}")

