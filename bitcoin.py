import pandas as pd
import numpy as np
import time
import ccxt


mavg_short_period = 14
mavg_long_period = 28
timeframe = '1h'
exchange = ccxt.binance()
symbol = 'BTC/USDT'
timeframe = '1h'
since = '2023-10-01'

# Initial portfolio
portfolio = {
    'USDT': 10000,
    'BTC': 0,
    'buy_price': 0,
}

def fetch_data(exchange, symbol, timeframe, since):
    milli_since = int(pd.Timestamp(since).timestamp() * 1000)
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, milli_since)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df


def calculate_mavg(df):
    df['mavg_short'] = df['close'].rolling(mavg_short_period).mean()
    df['mavg_long'] = df['close'].rolling(mavg_long_period).mean()
    return df

def check_signal(df):
    df = calculate_mavg(df)
    latest_data = df.iloc[-1]
    if latest_data['mavg_short'] > latest_data['mavg_long']:
        return 'buy'
    elif latest_data['mavg_short'] < latest_data['mavg_long']:
        return 'sell'
    else:
        return 'wait'

def execute_trade(signal, price):
    global portfolio
    if signal == 'buy' and portfolio['USDT'] > 0:
        portfolio['BTC'] = portfolio['USDT'] / price
        portfolio['buy_price'] = price
        portfolio['USDT'] = 0
    elif signal == 'sell' and portfolio['BTC'] > 0:
        portfolio['USDT'] = portfolio['BTC'] * price
        portfolio['BTC'] = 0

def timeframe_to_ms(timeframe):
    multiplier = int(timeframe[:-1])
    if timeframe.endswith('m'):
        return multiplier * 60 * 1000
    elif timeframe.endswith('h'):
        return multiplier * 60 * 60 * 1000
    elif timeframe.endswith('d'):
        return multiplier * 24 * 60 * 60 * 1000
    else:
        raise ValueError('Invalid timeframe')

while True:
    df = fetch_data(exchange, symbol, timeframe, since)
    signal = check_signal(df)
    latest_price = df['close'].iloc[-1]
    execute_trade(signal, latest_price)
    print(latest_price)
    print(signal)
    print(portfolio)
    time.sleep(timeframe_to_ms(timeframe) / 1000)