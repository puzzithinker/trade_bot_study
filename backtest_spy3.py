import concurrent.futures
import yfinance as yf
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
import numpy as np

# Fetch data
df = yf.download('SPY', start='2010-01-01', end='2023-10-10')

# Define the range of parameters to test
sma_slow_window_range = range(20, 61, 5)
sma_fast_window_range = range(5, 21, 5)
rsi_window_range = range(5, 31, 5)

# Initialize variables to record the best parameters
best_sharpe = -np.inf
best_sma_slow_window = None
best_sma_fast_window = None
best_rsi_window = None

# Define a function to backtest a single parameter combination
def backtest(sma_slow_window, sma_fast_window, rsi_window):
    df_copy = df.copy()  # Make a copy of the DataFrame

    # Calculate SMA and RSI
    sma_slow = SMAIndicator(df_copy['Close'], window=sma_slow_window).sma_indicator()
    sma_fast = SMAIndicator(df_copy['Close'], window=sma_fast_window).sma_indicator()
    rsi = RSIIndicator(df_copy['Close'], window=rsi_window).rsi()

    # Generate signals
    df_copy['buy_signal'] = (sma_fast > sma_slow) & (rsi < 30)
    df_copy['sell_signal'] = (sma_fast < sma_slow) & (rsi > 70)

    # Calculate returns
    df_copy['return'] = np.where(df_copy['buy_signal'], df_copy['Close'].pct_change().shift(-1), 0)

    # Calculate Sharpe ratio
    epsilon = 1e-8  # Small constant to avoid division by zero
    sharpe_ratio = df_copy['return'].mean() / (df_copy['return'].std() + epsilon) * np.sqrt(252)

    return sma_slow_window, sma_fast_window, rsi_window, sharpe_ratio

# Use a ThreadPoolExecutor to parallelize the backtests
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = []
    for sma_slow_window in sma_slow_window_range:
        for sma_fast_window in sma_fast_window_range:
            if sma_slow_window <= sma_fast_window:
                continue
            for rsi_window in rsi_window_range:
                futures.append(executor.submit(backtest, sma_slow_window, sma_fast_window, rsi_window))

    # As the futures complete, check if they have a better Sharpe ratio
    for future in concurrent.futures.as_completed(futures):
        sma_slow_window, sma_fast_window, rsi_window, sharpe_ratio = future.result()
        if sharpe_ratio > best_sharpe:
            best_sharpe = sharpe_ratio
            best_sma_slow_window = sma_slow_window
            best_sma_fast_window = sma_fast_window
            best_rsi_window = rsi_window

print(f'Best SMA slow window: {best_sma_slow_window}')
print(f'Best SMA fast window: {best_sma_fast_window}')
print(f'Best RSI window: {best_rsi_window}')
print(f'Best Sharpe ratio: {best_sharpe}')