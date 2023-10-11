import yfinance as yf
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator, MACD, ADXIndicator
import matplotlib.pyplot as plt
from telegram import Bot

# Fetch data
df = yf.download('SPY', start='2010-01-01', end='2023-10-10')

# Define the optimal parameters
sma_window_slow = 55
sma_window_fast = 20
rsi_window = 5
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
df['sell_signal'] = ((df['sma_fast'] < df['sma_slow']) & (df['rsi'] > 70))

# Telegram bot settings
bot_token = "YOUR_TOKEN"
chat_id = "YOUR_CHAT_ID"

def send_telegram_message(signal_type, current_price, sma_fast, sma_slow, rsi):
    message = f"{signal_type} signal generated.\nCurrent price: {current_price}\nSMA Fast: {sma_fast}\nSMA Slow: {sma_slow}\nRSI: {rsi}"
    bot = Bot(token=bot_token)
    bot.send_message(chat_id=chat_id, text=message)

# Send Telegram message for buy and sell signals
if df['buy_signal'].iloc[-1]:
    send_telegram_message(
        "Buy",
        df['Close'].iloc[-1],
        df['sma_fast'].iloc[-1],
        df['sma_slow'].iloc[-1],
        df['rsi'].iloc[-1]
    )
elif df['sell_signal'].iloc[-1]:
    send_telegram_message(
        "Sell",
        df['Close'].iloc[-1],
        df['sma_fast'].iloc[-1],
        df['sma_slow'].iloc[-1],
        df['rsi'].iloc[-1]
    )

print(df)