import yfinance as yf
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator, MACD, ADXIndicator

# Fetch data
df = yf.download('SPY', start='2010-01-01', end='2023-10-10')

# Define the optimal parameters
sma_window_slow = 30
sma_window_fast = 20
rsi_window = 10
macd_window_slow = 31
macd_window_fast = 14
adx_window = 16

# Calculate SMA, RSI, MACD, and ADX using the optimal parameters
sma_slow = SMAIndicator(df['Close'], window=sma_window_slow).sma_indicator()
sma_fast = SMAIndicator(df['Close'], window=sma_window_fast).sma_indicator()
rsi = RSIIndicator(df['Close'], window=rsi_window).rsi()
macd_indicator = MACD(df['Close'], window_slow=macd_window_slow, window_fast=macd_window_fast)
macd_line = macd_indicator.macd()
signal_line = macd_indicator.macd_signal()
adx = ADXIndicator(df['High'], df['Low'], df['Close'], window=adx_window).adx()

# Add the indicators to the DataFrame
df['sma_slow'] = sma_slow
df['sma_fast'] = sma_fast
df['rsi'] = rsi
df['macd_line'] = macd_line
df['signal_line'] = signal_line
df['adx'] = adx

# Generate buy and sell signals
df['buy_signal'] = ((df['sma_fast'] > df['sma_slow']) & (df['rsi'] < 30))

df['sell_signal'] = ((df['sma_fast'] < df['sma_slow'])  & (df['rsi'] > 70))

# Print the DataFrame
print(df)