# trade_bot_study

Here's how the program works:

It imports the necessary libraries, including concurrent.futures for parallel processing, yfinance for fetching historical stock data, ta for technical analysis indicators, and numpy for numerical operations.

The program fetches historical data for the Hang Seng Index (^HSI) from Yahoo Finance using the yf.download function. The data is fetched from January 1, 2010, to October 10, 2023.

It defines three ranges of parameters to test: sma_slow_window_range, sma_fast_window_range, and rsi_window_range. These ranges represent the different values to be tested for the slow SMA window, fast SMA window, and RSI window, respectively.

The program initializes variables to record the best parameters found and the corresponding best Sharpe ratio. The Sharpe ratio is a measure of risk-adjusted performance commonly used in finance.

It defines a function called backtest that takes the three parameters (sma_slow_window, sma_fast_window, rsi_window) and performs the backtest for a single combination of parameters.

Inside the backtest function, a copy of the original DataFrame is made to avoid modifying the original data. The slow and fast SMAs are calculated using the SMAIndicator from the ta library, and the RSI is calculated using the RSIIndicator. These indicators are used to generate buy and sell signals based on certain conditions.

The returns are calculated by taking the percentage change of the closing price and shifting it by one day. If the buy signal condition is met, the return is set to the calculated percentage change; otherwise, it is set to zero.

The Sharpe ratio is calculated as the mean of the returns divided by the standard deviation, multiplied by the square root of 252 (assuming 252 trading days in a year). A small constant (epsilon) is added to the denominator to avoid division by zero.

The main part of the program uses a ThreadPoolExecutor to parallelize the backtests. It iterates over the parameter ranges and submits each combination of parameters as a separate task to the executor.

As the tasks complete, the program checks if the resulting Sharpe ratio is better than the best one found so far. If it is, the best parameters and Sharpe ratio are updated accordingly.

Finally, the program prints the best parameters (sma_slow_window, sma_fast_window, rsi_window) and the corresponding best Sharpe ratio.
