import yfinance as yf
import ta
import pandas as pd
import matplotlib.pyplot as plt

# Download historical data
data = yf.download('^GSPC', start='2010-01-01', end='2023-10-01', interval='1d')

# Calculate the indicators

# Moving Average
data['SMA_20'] = ta.trend.sma_indicator(data['Close'], window=20)
data['SMA_50'] = ta.trend.sma_indicator(data['Close'], window=50)

# RSI
data['RSI'] = ta.momentum.rsi(data['Close'], window=14)

# MACD
macd = ta.trend.MACD(data['Close'])
data['MACD_diff'] = macd.macd_diff()

# Define the buy/sell signals
data['Buy_Signal'] = (data['SMA_20'] > data['SMA_50']) & (data['RSI'] < 30) & (data['MACD_diff'] > 0)
data['Sell_Signal'] = (data['SMA_20'] < data['SMA_50']) & (data['RSI'] > 70) & (data['MACD_diff'] < 0)

# Plotting the data
plt.figure(figsize=(12,5))
plt.plot(data['Close'], label='S&P 500 Close Prices', color='blue')
plt.plot(data['SMA_20'], label='20-Month SMA', color='red')
plt.plot(data['SMA_50'], label='50-Month SMA', color='green')
plt.scatter(data[data['Buy_Signal']].index, data[data['Buy_Signal']]['Close'], color='green', marker='^', alpha=1)
plt.scatter(data[data['Sell_Signal']].index, data[data['Sell_Signal']]['Close'], color='red', marker='v', alpha=1)
plt.title('S&P 500 - Buy and Sell Signals')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend(loc='upper left')
plt.grid()
plt.show()