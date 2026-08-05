from datetime import datetime

import pandas as pd

from app.services import yahoo_service


class FakeTicker:
    call_count = 0

    def __init__(self, ticker):
        self.ticker = ticker
        FakeTicker.call_count += 1

    @property
    def info(self):
        return {
            "regularMarketPrice": 101.0,
            "ticker": self.ticker,
        }

    def history(self, start, end, interval="1d"):
        index = pd.DatetimeIndex(
            ["2026-08-01", "2026-08-02"],
            tz="UTC",
        )
        return pd.DataFrame(
            {
                "Open": [100, 101],
                "Close": [101, 102],
            },
            index=index,
        )


def setup_function():
    yahoo_service._info_cache.clear()
    yahoo_service._history_cache.clear()
    FakeTicker.call_count = 0


def test_get_info_uses_ticker_cache(monkeypatch):
    monkeypatch.setattr(
        yahoo_service.yf,
        "Ticker",
        FakeTicker,
    )

    first = yahoo_service.get_info("aapl")
    second = yahoo_service.get_info("AAPL")

    assert first["regularMarketPrice"] == 101.0
    assert second["regularMarketPrice"] == 101.0
    assert FakeTicker.call_count == 1


def test_get_historical_data_uses_cache_and_returns_copy(monkeypatch):
    monkeypatch.setattr(
        yahoo_service.yf,
        "Ticker",
        FakeTicker,
    )

    start = datetime(2026, 8, 1)
    end = datetime(2026, 8, 3)

    first = yahoo_service.get_historical_data(
        "MSFT",
        start,
        end,
    )
    second = yahoo_service.get_historical_data(
        "MSFT",
        start,
        end,
    )

    assert FakeTicker.call_count == 1
    assert list(first["Close"]) == [101, 102]
    assert list(second["Close"]) == [101, 102]

    second.loc[second.index[0], "Close"] = 999

    third = yahoo_service.get_historical_data(
        "MSFT",
        start,
        end,
    )
    assert list(third["Close"]) == [101, 102]
