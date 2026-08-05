from datetime import date
from decimal import Decimal

import pytest

from app import database as app_database
from app.services import database_service


class FakeCursor:
	def __init__(
		self,
		*,
		fetchone_values=None,
		fetchall_values=None,
		rowcount=1,
		lastrowid=99,
	):
		self.fetchone_values = list(fetchone_values or [])
		self.fetchall_values = list(fetchall_values or [])
		self.rowcount = rowcount
		self.lastrowid = lastrowid
		self.executed = []
		self.closed = False

	def execute(self, query, params=None):
		self.executed.append((query, params))

	def fetchone(self):
		if self.fetchone_values:
			return self.fetchone_values.pop(0)
		return None

	def fetchall(self):
		if self.fetchall_values:
			return self.fetchall_values.pop(0)
		return []

	def close(self):
		self.closed = True


class FakeDb:
	def __init__(self, cursors):
		self.cursors = list(cursors)
		self.cursor_calls = []
		self.commit_called = False
		self.rollback_called = False
		self.closed = False

	def cursor(self, **kwargs):
		self.cursor_calls.append(kwargs)
		if not self.cursors:
			raise AssertionError("No fake cursor left")
		return self.cursors.pop(0)

	def commit(self):
		self.commit_called = True

	def rollback(self):
		self.rollback_called = True

	def close(self):
		self.closed = True


def test_get_db_connection_uses_env_variables(monkeypatch):
	captured = {}

	def fake_connect(**kwargs):
		captured.update(kwargs)
		return "db-conn"

	monkeypatch.setenv("db_host", "localhost")
	monkeypatch.setenv("db_user", "root")
	monkeypatch.setenv("db_password", "pw")
	monkeypatch.setenv("db_name", "portfolio")
	monkeypatch.setattr(
		app_database.mysql.connector,
		"connect",
		fake_connect,
	)

	result = app_database.get_db_connection()

	assert result == "db-conn"
	assert captured == {
		"host": "localhost",
		"user": "root",
		"password": "pw",
		"database": "portfolio",
	}


def test_get_portfolios_fetches_all_and_closes_cursor():
	portfolio_rows = [{"portfolio_id": 1}]
	cursor = FakeCursor(fetchall_values=[portfolio_rows])
	db = FakeDb([cursor])

	result = app_database.get_portfolios(db)

	assert result == portfolio_rows
	assert cursor.closed is True
	assert "SELECT * FROM portfolio;" in cursor.executed[0][0]


def test_get_initial_data_creates_portfolio_when_missing():
	assets_cursor = FakeCursor(fetchall_values=[[{"asset_id": 11}]])
	holdings_cursor = FakeCursor(fetchall_values=[[{"holding_id": 22}]])
	portfolio_cursor = FakeCursor(
		fetchall_values=[[{"portfolio_id": 1, "portfolio_name": "New Portfolio"}]]
	)
	db = FakeDb([assets_cursor, holdings_cursor, portfolio_cursor])

	assets, holdings = app_database.get_initial_data(db, None)

	assert db.commit_called is True
	assert assets == [{"asset_id": 11}]
	assert holdings == [{"holding_id": 22}]
	assert portfolio_cursor.closed is True
	assert assets_cursor.closed is True
	assert holdings_cursor.closed is True


def test_get_initial_data_uses_existing_portfolio_without_insert():
	assets_cursor = FakeCursor(fetchall_values=[[{"asset_id": 11}]])
	holdings_cursor = FakeCursor(fetchall_values=[[{"holding_id": 22}]])
	db = FakeDb([assets_cursor, holdings_cursor])

	assets, holdings = app_database.get_initial_data(
		db,
		{"portfolio_id": 42},
	)

	assert db.commit_called is False
	assert assets == [{"asset_id": 11}]
	assert holdings == [{"holding_id": 22}]


def test_add_holding_rejects_invalid_numeric_payload():
	service = database_service.DataBaseService()

	with pytest.raises(ValueError) as error:
		service.add_holding(
			{
				"portfolio_id": 1,
				"asset_id": 1,
				"ticker": "AAPL",
				"company_name": "Apple",
				"shares": "not-a-number",
				"cost_basis": 10,
				"purchase_date": "2026-08-05",
			}
		)

	assert "shares and cost_basis must be valid numbers." == str(
		error.value
	)


def test_remove_shares_rejects_invalid_numbers_before_db_access():
	service = database_service.DataBaseService()

	with pytest.raises(ValueError) as error:
		service.remove_shares(1, "AAPL", "bad", 1)

	assert "must be valid numbers" in str(error.value)


def test_remove_shares_rejects_non_positive_shares_before_db_access():
	service = database_service.DataBaseService()

	with pytest.raises(ValueError) as error:
		service.remove_shares(1, "AAPL", 0, 1)

	assert str(error.value) == (
		"Shares to remove must be greater than zero."
	)


def test_remove_shares_rejects_negative_sale_price_before_db_access():
	service = database_service.DataBaseService()

	with pytest.raises(ValueError) as error:
		service.remove_shares(1, "AAPL", 1, -1)

	assert str(error.value) == "Sale price cannot be negative."


def test_deposit_cash_rejects_zero_or_negative_amount():
	service = database_service.DataBaseService()

	with pytest.raises(ValueError) as error:
		service.deposit_cash(1, 0)

	assert str(error.value) == (
		"Deposit amount must be greater than zero."
	)


def test_withdraw_cash_rejects_zero_or_negative_amount():
	service = database_service.DataBaseService()

	with pytest.raises(ValueError) as error:
		service.withdraw_cash(1, 0)

	assert str(error.value) == (
		"Withdrawal amount must be greater than zero."
	)


def test_get_asset_by_type_returns_existing_id(monkeypatch):
	service = database_service.DataBaseService()
	cursor = FakeCursor(fetchone_values=[{"asset_id": 7}])
	db = FakeDb([cursor])

	monkeypatch.setattr(
		database_service,
		"get_db_connection",
		lambda: db,
	)

	asset_id = service.get_asset_by_type("Stock")

	assert asset_id == 7
	assert db.commit_called is False
	assert db.closed is True


def test_get_asset_by_type_inserts_new_asset_when_missing(monkeypatch):
	service = database_service.DataBaseService()
	cursor = FakeCursor(fetchone_values=[None], lastrowid=12)
	db = FakeDb([cursor])

	monkeypatch.setattr(
		database_service,
		"get_db_connection",
		lambda: db,
	)

	asset_id = service.get_asset_by_type("ETF")

	assert asset_id == 12
	assert db.commit_called is True
	assert db.closed is True


def test_get_portfolio_summary_returns_none_when_portfolio_missing(monkeypatch):
	service = database_service.DataBaseService()
	cursor = FakeCursor(fetchone_values=[None])
	db = FakeDb([cursor])

	monkeypatch.setattr(
		database_service,
		"get_db_connection",
		lambda: db,
	)

	result = service.get_portfolio_summary(1)

	assert result is None
	assert cursor.closed is True
	assert db.closed is True


def test_get_portfolio_summary_aggregates_values(monkeypatch):
	service = database_service.DataBaseService()
	holdings = [
		{
			"ticker": "AAPL",
			"shares": 2,
			"cost_basis": 90,
			"asset_type": "Stock",
		},
		{
			"ticker": "BND",
			"shares": 3,
			"cost_basis": 40,
			"asset_type": "Bond",
		},
		{
			"ticker": "BTC",
			"shares": 5,
			"cost_basis": 12,
			"asset_type": "Crypto",
		},
	]
	cursor = FakeCursor(
		fetchone_values=[{"cash_balance": 100}],
		fetchall_values=[holdings],
	)
	db = FakeDb([cursor])

	quote_map = {
		"AAPL": (Decimal("120"), Decimal("100")),
		"BND": (Decimal("50"), Decimal("49")),
		"BTC": (Decimal("10"), Decimal("8")),
	}

	monkeypatch.setattr(
		database_service,
		"get_db_connection",
		lambda: db,
	)
	monkeypatch.setattr(
		service,
		"_get_market_quote",
		lambda ticker: quote_map[ticker],
	)

	summary = service.get_portfolio_summary(1)

	assert summary["cash_balance"] == 100.0
	assert summary["stocks_value"] == 240.0
	assert summary["bonds_value"] == 150.0
	assert summary["crypto_value"] == 50.0
	assert summary["total_value"] == 540.0
	assert summary["total_return"] == 80.0
	assert summary["cost_basis_total"] == 360.0
	assert summary["total_return_percent"] == pytest.approx(22.2222, rel=1e-4)
	assert summary["day_gain"] == 53.0
	assert summary["day_gain_percent"] == pytest.approx(13.6951, rel=1e-4)


def test_get_portfolio_snapshots_builds_query_filters(monkeypatch):
	service = database_service.DataBaseService()
	cursor = FakeCursor(fetchall_values=[[{"snapshot_date": "2026-08-01"}]])
	db = FakeDb([cursor])

	monkeypatch.setattr(
		database_service,
		"get_db_connection",
		lambda: db,
	)
	monkeypatch.setattr(
		service,
		"_ensure_portfolio_history_table",
		lambda _db: None,
	)

	result = service.get_portfolio_snapshots(
		1,
		start_date=date(2026, 8, 1),
		end_date=date(2026, 8, 31),
	)

	query, params = cursor.executed[0]
	assert "AND snapshot_date >= %s" in query
	assert "AND snapshot_date <= %s" in query
	assert "ORDER BY snapshot_date" in query
	assert params == (1, date(2026, 8, 1), date(2026, 8, 31))
	assert result == [{"snapshot_date": "2026-08-01"}]


def test_get_latest_portfolio_snapshot_before_returns_row(monkeypatch):
	service = database_service.DataBaseService()
	cursor = FakeCursor(
		fetchone_values=[
			{
				"snapshot_date": "2026-07-31",
				"cash_balance": 10,
				"portfolio_value": 99,
			}
		]
	)
	db = FakeDb([cursor])

	monkeypatch.setattr(
		database_service,
		"get_db_connection",
		lambda: db,
	)
	monkeypatch.setattr(
		service,
		"_ensure_portfolio_history_table",
		lambda _db: None,
	)

	result = service.get_latest_portfolio_snapshot_before(
		1,
		date(2026, 8, 1),
	)

	assert result["snapshot_date"] == "2026-07-31"
	assert cursor.closed is True
	assert db.closed is True
