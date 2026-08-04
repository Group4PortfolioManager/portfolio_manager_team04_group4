from datetime import datetime
from time import monotonic
import pandas as pd
import yfinance as yf


INFO_CACHE_TTL_SECONDS = 60
HISTORY_CACHE_TTL_SECONDS = 300

_info_cache = {}
_history_cache = {}


def _get_cached_value(cache, key, ttl_seconds):
    cached_entry = cache.get(key)

    if cached_entry is None:
        return None

    expires_at, value = cached_entry

    if expires_at <= monotonic():
        cache.pop(key, None)
        return None

    return value


def _set_cached_value(cache, key, ttl_seconds, value):
    cache[key] = (monotonic() + ttl_seconds, value)


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
    cache_key = (
        ticker.strip().upper(),
        start_date.isoformat(),
        end_date.isoformat(),
        interval,
    )

    cached_df = _get_cached_value(
        _history_cache,
        cache_key,
        HISTORY_CACHE_TTL_SECONDS,
    )

    if cached_df is not None:
        return cached_df.copy()

    stock = yf.Ticker(ticker)
    df = stock.history(start=start_date, end=end_date, interval=interval)
    df.index = pd.to_datetime(df.index).tz_localize(None)
    _set_cached_value(
        _history_cache,
        cache_key,
        HISTORY_CACHE_TTL_SECONDS,
        df.copy(),
    )
    return df


def get_info(ticker: str) -> dict:
    """Fetch basic company info for a ticker."""
    normalized_ticker = ticker.strip().upper()
    cached_info = _get_cached_value(
        _info_cache,
        normalized_ticker,
        INFO_CACHE_TTL_SECONDS,
    )

    if cached_info is not None:
        return dict(cached_info)

    stock = yf.Ticker(normalized_ticker)
    info = stock.info or {}
    _set_cached_value(
        _info_cache,
        normalized_ticker,
        INFO_CACHE_TTL_SECONDS,
        dict(info),
    )
    return info
