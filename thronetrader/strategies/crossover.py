import logging

from thronetrader.helper import squire


def get_crossover_signals(symbol: str, logger: logging.Logger,
                          short_window: int = 20,
                          long_window: int = 50,
                          years: int = 1) -> str:
    """Get buy, sell and hold signals for a particular stock using breakout strategy.

    Args:
        symbol: Stock ticker.
        logger: Logger object.
        short_window: Short term moving average.
        long_window: Long term moving average.
        years: Number of years for the historical data.

    See Also:
        - | The number of years used to calculate moving averages impacts the frequency, responsiveness,
          | accuracy, and risk associated with the signals generated by the strategy.
        - A larger number of years will provide a longer historical perspective and result in smoother moving averages.
        - This tends to generate fewer buy and sell signals as the strategy focuses on longer-term trends.
        - Experiment and backtest to find the best fit for your approach.

    Returns:
        str:
        Analysis of buy/hold/sell.
    """
    try:
        stock_data = squire.get_historical_data(symbol=symbol, years=years, df=True)
    except ValueError as error:
        logger.error(error)
        return "undetermined"

    # Calculate short-term (e.g., 20-day) and long-term (e.g., 50-day) moving averages
    stock_data['SMA_short'] = stock_data['Close'].rolling(window=short_window).mean()
    stock_data['SMA_long'] = stock_data['Close'].rolling(window=long_window).mean()

    # Generate the buy, sell, and hold signals
    stock_data['buy'] = stock_data['SMA_short'] > stock_data['SMA_long']
    stock_data['sell'] = stock_data['SMA_short'] < stock_data['SMA_long']
    stock_data['hold'] = ~(stock_data['buy'] | stock_data['sell'])

    return squire.classify(stock_data, logger)
