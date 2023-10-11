import ccxt
import pandas as pd
import datetime
import talib
import matplotlib.pyplot as plt
import logging
import schedule
import time
import numpy as np

# Initialize the logger
logging.basicConfig(filename='paper_trading.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

# Initialize the exchange (using Binance as an example)
exchange = ccxt.binance({
    'apiKey': 'YOUR_API_KEY',
    'secret': 'YOUR_SECRET_KEY',
})

# Define the metrics for each cryptocurrency pair
metrics = {
    'BTC/USDT': {'sma_short_period': 10, 'sma_long_period': 170, 'bollinger_period': 40},
    'ETH/USDT': {'sma_short_period': 10, 'sma_long_period': 190, 'bollinger_period': 40},
    'ADA/USDT': {'sma_short_period': 10, 'sma_long_period': 140, 'bollinger_period': 20},
}

# Function to fetch cryptocurrency data
def fetch_data(pair, timeframe='1d', limit=500):
    data = exchange.fetch_ohlcv(pair, timeframe, limit=limit)
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df

# Function to calculate SMA
def calculate_SMA(data, period):
    return talib.SMA(data, timeperiod=period)

# Function to calculate Bollinger Bands
def calculate_bollinger_bands(data, period):
    upper, middle, lower = talib.BBANDS(data, timeperiod=period)
    return upper, middle, lower

# Main function to implement the trading strategy
def paper_trade():
    for pair, metric in metrics.items():
        data = fetch_data(pair)
        data['sma_short'] = calculate_SMA(data['close'], metric['sma_short_period'])
        data['sma_long'] = calculate_SMA(data['close'], metric['sma_long_period'])
        data['bollinger_up'], data['bollinger_middle'], data['bollinger_down'] = calculate_bollinger_bands(data['close'], metric['bollinger_period'])

        # Check for BUY signal
        if data['sma_short'][-1] > data['sma_long'][-1] and data['close'][-1] < data['bollinger_down'][-1]:
            logging.info(f"BUY signal for {pair} at price {data['close'][-1]}")
            plt.figure(figsize=(12,5))
            plt.title(f"Buy signal for {pair}")
            plt.plot(data['close'], label='Close Price', color='blue')
            plt.plot(data['sma_short'], label='Short-term SMA', color='red')
            plt.plot(data['sma_long'], label='Long-term SMA', color='green')
            plt.plot(data['bollinger_up'], label='Upper Bollinger Band', color='cyan')
            plt.plot(data['bollinger_down'], label='Lower Bollinger Band', color='cyan')
            plt.legend(loc='upper left')
            plt.show()

        # Check for SELL signal
        elif data['sma_short'][-1] < data['sma_long'][-1] and data['close'][-1] > data['bollinger_up'][-1]:
            logging.info(f"SELL signal for {pair} at price {data['close'][-1]}")
            plt.figure(figsize=(12,5))
            plt.title(f"Sell signal for {pair}")
            plt.plot(data['close'], label='Close Price', color='blue')
            plt.plot(data['sma_short'], label='Short-term SMA', color='red')
            plt.plot(data['sma_long'], label='Long-term SMA', color='green')
            plt.plot(data['bollinger_up'], label='Upper Bollinger Band', color='cyan')
            plt.plot(data['bollinger_down'], label='Lower Bollinger Band', color='cyan')
            plt.legend(loc='upper left')
            plt.show()

# Schedule the paper trade program to run every day
schedule.every().day.at("00:00").do(paper_trade)

while True:
    schedule.run_pending()
    time.sleep(1)