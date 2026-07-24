from datetime import datetime
import pandas as pd
import yfinance as yf


def get_historical_data(ticker: str, start_date: datetime, end_date: datetime, interval: str = "1d") -> pd.DataFrame:
    """Fetch historical stock data from Yahoo Finance for a given ticker.

    Args:
        ticker: Stock ticker symbol (e.g. 'GOOG', 'AAPL').
        start_date: Start of the historical period.
        end_date: End of the historical period.
        interval: Data interval (e.g. '1d', '1wk', '1mo').

    Returns:
        DataFrame indexed by date with columns: Open, High, Low, Close,
        Volume, Dividends, Stock Splits.
    """
    stock = yf.Ticker(ticker)
    df = stock.history(start=start_date, end=end_date, interval=interval)
    df.index = pd.to_datetime(df.index).tz_localize(None)
    return df


def get_info(ticker: str) -> dict:
    """Fetch basic company info for a ticker."""
    stock = yf.Ticker(ticker)
    return stock.info or {}
