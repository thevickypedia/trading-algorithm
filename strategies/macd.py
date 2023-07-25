import pprint
from typing import Dict

import pandas as pd
import webull
from helper import squire

wb = webull.paper_webull()


def get_macd_signals(symbol: str,
                     bar_count: int = 100,
                     simple: bool = False) -> Dict[str, str]:
    """Get buy, sell, and hold signals using the Moving Average Convergence Divergence (MACD) strategy.

    Args:
        symbol: Stock ticker.
        bar_count: Number of bars from webull.
        simple: Simply returns whether it's a buy, sell or hold.

    See Also:
        - A larger `bar_count` gives longer historical data for analysis.
        - A smaller count focuses on recent data for short-term signals.
        - Experiment and backtest to find the best fit for your approach.
        - | Short-term EMA (12-day EMA): A smaller span value for the short-term EMA means that it reacts more quickly
          | to recent price changes. This can lead to more frequent and sensitive crossovers between the MACD line and
          | the Signal line, resulting in more buy and sell signals. However, it might also generate more false signals
          | in volatile markets.
        - | Long-term EMA (26-day EMA): A larger span value for the long-term EMA makes it smoother and less reactive
          | to short-term price fluctuations. This helps in identifying the long-term trends in the stock's price
          | movement. However, a larger span might result in delayed signals and could miss some short-term trends.
        _ | Crossover Sensitivity: When the short-term EMA crosses above the long-term EMA, it generates a bullish
          | signal (buy), and when it crosses below the long-term EMA, it generates a bearish signal (sell).
          | The span value influences how quickly these crossovers occur. A smaller span makes crossovers more
          | sensitive, potentially leading to more frequent signals.

    Returns:
        Dict[str, str]:
        A dictionary of each day's buy, sell, and hold signals.
    """
    # Fetch historical stock data using the 'get_bars' method from the 'webull' package
    bars = wb.get_bars(stock=symbol, interval='d', count=bar_count)

    # Create a DataFrame from the fetched data
    stock_data = pd.DataFrame(bars)

    # Calculate the short-term (e.g., 12-day) and long-term (e.g., 26-day) Exponential Moving Averages (EMAs)
    stock_data['EMA_short'] = stock_data['close'].ewm(span=12, adjust=False).mean()
    stock_data['EMA_long'] = stock_data['close'].ewm(span=26, adjust=False).mean()

    # Calculate the MACD line and the Signal line (9-day EMA of the MACD line)
    stock_data['MACD'] = stock_data['EMA_short'] - stock_data['EMA_long']
    stock_data['Signal'] = stock_data['MACD'].ewm(span=9, adjust=False).mean()

    # Generate the buy, sell, and hold signals based on MACD crossovers
    stock_data['buy'] = stock_data['MACD'] > stock_data['Signal']
    stock_data['sell'] = stock_data['MACD'] < stock_data['Signal']
    stock_data['hold'] = ~(stock_data['buy'] | stock_data['sell'])

    return squire.classify(stock_data, simple)
