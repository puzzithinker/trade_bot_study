import ccxt
import pandas as pd
import numpy as np
from sklearn.model_selection import ParameterGrid
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Replace talib with pandas for SMA
def SMA(array, timeperiod):
    return pd.Series(array).rolling(window=timeperiod).mean()

def BBANDS(array, timeperiod):
    middle = SMA(array, timeperiod)
    std = pd.Series(array).rolling(window=timeperiod).std()
    upper = middle + 2*std
    lower = middle - 2*std
    return upper, middle, lower

# Initialize exchange
exchange = ccxt.binance({
    'enableRateLimit': True,
})

# Define the parameter grid
param_grid = {'sma_short_period': range(10, 100, 10), 'sma_long_period': range(100, 200, 10), 'bollinger_period': range(10, 50, 10)}

# Create a list of all possible combinations of parameters
params_list = list(ParameterGrid(param_grid))

# List of assets to trade
assets = ['BTC/USDT', 'ETH/USDT', 'LINK/USDT','DOT/USDT','ATOM/USDT','ARB/USDT']

for asset in assets:
    # Initialize a DataFrame to store the results
    results = pd.DataFrame(columns=['sma_short_period', 'sma_long_period', 'bollinger_period', 'performance'])

    # Fetch OHLCV data
    data = pd.DataFrame(exchange.fetch_ohlcv(asset, '1d'), columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')

    # Loop over all possible combinations of parameters
    for params in params_list:
        df = data.copy()

        # Calculate the indicators with the current parameters
        df['sma_short'] = SMA(df['close'], timeperiod=params['sma_short_period'])
        df['sma_long'] = SMA(df['close'], timeperiod=params['sma_long_period'])
        df['upper_band'], df['middle_band'], df['lower_band'] = BBANDS(df['close'], timeperiod=params['bollinger_period'])

        # Define the conditions for a buy or sell signal
        df['buy_signal'] = np.where((df['close'] > df['sma_long']) & (df['sma_short'] > df['sma_long']) & (df['close'] < df['lower_band']), 1, 0)
        df['sell_signal'] = np.where((df['close'] < df['sma_long']) & (df['sma_short'] < df['sma_long']) & (df['close'] > df['upper_band']), -1, 0)

        # Calculate the performance of the strategy
        df['returns'] = df['close'].pct_change() * df['buy_signal'].shift()
        performance = df['returns'].cumsum().iloc[-1]

        # Check if performance is not NA
        if not pd.isna(performance):
            # Store the results
            new_row = pd.DataFrame([{**params, 'performance': performance}])
            results = pd.concat([results, new_row], ignore_index=True)

    # Find the set of parameters with the best performance
    best_params = results.loc[results['performance'].idxmax()]

    print(f'Best parameters for {asset}: {best_params}')