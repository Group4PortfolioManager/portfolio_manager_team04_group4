"""Unit tests for portfolio performance history calculations.

These tests validate snapshot-based performance behavior:
- missing portfolio handling
- fallback to summary when no snapshots exist
- step-wise value changes from seed + in-range snapshots
"""

from datetime import date
from datetime import datetime

from app.services import analytics_service


class FakeDbService:
    """Simple in-memory test double for DataBaseService."""

    def __init__(
        self,
        *,
        portfolio=None,
        summary=None,
        seed_snapshot=None,
        snapshots=None,
    ):
        self._portfolio = portfolio
        self._summary = summary
        self._seed_snapshot = seed_snapshot
        self._snapshots = snapshots or []
        self.upsert_calls = []

    def get_portfolio_by_id(self, portfolio_id):
        """Return the configured portfolio payload."""
        return self._portfolio

    def upsert_portfolio_snapshot(self, portfolio_id):
        """Track upsert calls and emulate successful writes."""
        self.upsert_calls.append(portfolio_id)
        return {
            "portfolio_id": portfolio_id,
            "snapshot_date": "2026-08-04",
            "portfolio_value": 0.0,
        }

    def get_latest_portfolio_snapshot_before(self, portfolio_id, before_date):
        """Return the configured seed snapshot before the range start."""
        return self._seed_snapshot

    def get_portfolio_snapshots(self, portfolio_id, start_date=None, end_date=None):
        """Return configured in-range snapshots."""
        return list(self._snapshots)

    def get_portfolio_summary(self, portfolio_id):
        """Return configured live summary fallback."""
        return self._summary


def _inject_db_service(monkeypatch, fake_service):
    """Replace DataBaseService constructor with a fixed fake instance."""
    monkeypatch.setattr(
        analytics_service,
        "DataBaseService",
        lambda: fake_service,
    )


def test_get_portfolio_performance_history_returns_none_for_missing_portfolio(monkeypatch):
    """Returns None when portfolio does not exist."""
    fake_service = FakeDbService(portfolio=None)
    _inject_db_service(monkeypatch, fake_service)

    result = analytics_service.get_portfolio_performance_history(1)

    assert result is None
    assert fake_service.upsert_calls == []


def test_get_portfolio_performance_history_uses_summary_when_no_snapshots(monkeypatch):
    """Uses current summary value for all points when no snapshot rows exist."""
    points = [
        date(2026, 8, 1),
        date(2026, 8, 2),
        date(2026, 8, 3),
    ]
    fake_service = FakeDbService(
        portfolio={"portfolio_id": 1, "cash_balance": 100.0},
        summary={"total_value": 250.5},
        snapshots=[],
    )

    _inject_db_service(monkeypatch, fake_service)
    monkeypatch.setattr(analytics_service, "_build_points", lambda **_: points)

    result = analytics_service.get_portfolio_performance_history(
        1,
        window_type="days",
        window_size=3,
    )

    assert [row["value"] for row in result] == [250.5, 250.5, 250.5]
    assert fake_service.upsert_calls == [1]


def test_get_portfolio_performance_history_applies_step_changes_without_future_backfill(monkeypatch):
    """Keeps earlier dates at seed value until a later snapshot date is reached."""
    points = [
        date(2026, 8, 1),
        date(2026, 8, 2),
        date(2026, 8, 3),
        date(2026, 8, 4),
    ]
    fake_service = FakeDbService(
        portfolio={"portfolio_id": 1, "cash_balance": 10.0},
        seed_snapshot={
            "snapshot_date": date(2026, 7, 31),
            "portfolio_value": 90.0,
        },
        snapshots=[
            {
                "snapshot_date": "2026-08-03",
                "portfolio_value": 120.0,
            }
        ],
    )

    _inject_db_service(monkeypatch, fake_service)
    monkeypatch.setattr(analytics_service, "_build_points", lambda **_: points)

    result = analytics_service.get_portfolio_performance_history(
        1,
        window_type="days",
        window_size=4,
    )

    assert [row["value"] for row in result] == [90.0, 90.0, 120.0, 120.0]
    assert fake_service.upsert_calls == [1]


def test_get_portfolio_performance_history_uses_cash_balance_until_first_snapshot(monkeypatch):
    """When no seed snapshot exists, values begin from portfolio cash balance."""
    points = [
        date(2026, 8, 1),
        date(2026, 8, 2),
        date(2026, 8, 3),
    ]
    fake_service = FakeDbService(
        portfolio={"portfolio_id": 1, "cash_balance": 75.0},
        snapshots=[
            {
                "snapshot_date": "2026-08-03",
                "portfolio_value": 130.0,
            }
        ],
    )

    _inject_db_service(monkeypatch, fake_service)
    monkeypatch.setattr(analytics_service, "_build_points", lambda **_: points)

    result = analytics_service.get_portfolio_performance_history(
        1,
        window_type="days",
        window_size=3,
    )

    assert [row["value"] for row in result] == [75.0, 75.0, 130.0]


def test_get_portfolio_performance_history_ignores_invalid_snapshot_dates(monkeypatch):
    """Invalid snapshot date strings are skipped without breaking history output."""
    points = [
        date(2026, 8, 1),
        date(2026, 8, 2),
        date(2026, 8, 3),
    ]
    fake_service = FakeDbService(
        portfolio={"portfolio_id": 1, "cash_balance": 50.0},
        snapshots=[
            {
                "snapshot_date": "not-a-date",
                "portfolio_value": 999.0,
            },
            {
                "snapshot_date": "2026-08-02",
                "portfolio_value": 80.0,
            },
        ],
    )

    _inject_db_service(monkeypatch, fake_service)
    monkeypatch.setattr(analytics_service, "_build_points", lambda **_: points)

    result = analytics_service.get_portfolio_performance_history(
        1,
        window_type="days",
        window_size=3,
    )

    assert [row["value"] for row in result] == [50.0, 80.0, 80.0]


def test_coerce_snapshot_date_handles_datetime_and_invalid_strings():
    """Helper coerces datetime objects and rejects malformed date strings."""
    coerced_datetime = analytics_service._coerce_snapshot_date(
        datetime(2026, 8, 5, 12, 0, 0)
    )
    coerced_invalid = analytics_service._coerce_snapshot_date("2026/08/05")

    assert coerced_datetime == date(2026, 8, 5)
    assert coerced_invalid is None


def test_format_label_uses_day_and_month_modes():
    """Label helper returns day labels for day mode and month labels otherwise."""
    point = date(2026, 8, 5)

    assert analytics_service._format_label(point, window_type="days") == "05 Aug"
    assert analytics_service._format_label(point, window_type="months") == "Aug"
