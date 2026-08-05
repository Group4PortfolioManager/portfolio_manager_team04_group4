from datetime import date
from decimal import Decimal

from app.services import database_service


class FakeCursor:
	def __init__(self):
		self.executed = []
		self.closed = False

	def execute(self, query, params=None):
		self.executed.append((query, params))

	def close(self):
		self.closed = True


class FakeDb:
	def __init__(self):
		self.cursor_obj = FakeCursor()
		self.commit_called = False
		self.rollback_called = False
		self.closed = False

	def cursor(self, **_kwargs):
		return self.cursor_obj

	def commit(self):
		self.commit_called = True

	def rollback(self):
		self.rollback_called = True

	def close(self):
		self.closed = True


def test_get_market_quote_uses_price_fallback_fields(monkeypatch):
	service = database_service.DataBaseService()
	monkeypatch.setattr(
		database_service,
		"get_info",
		lambda _ticker: {
			"regularMarketPrice": 99.5,
			"regularMarketPreviousClose": 97.0,
		},
	)

	current_price, previous_close = service._get_market_quote("AAPL")

	assert current_price == Decimal("99.5")
	assert previous_close == Decimal("97.0")


def test_enrich_holding_with_market_data_calculates_values(monkeypatch):
	service = database_service.DataBaseService()
	monkeypatch.setattr(
		service,
		"_get_market_quote",
		lambda _ticker: (Decimal("20"), Decimal("19")),
	)

	result = service._enrich_holding_with_market_data(
		{
			"ticker": "AAPL",
			"shares": "3",
			"cost_basis": "10",
		}
	)

	assert result["current_price"] == 20.0
	assert result["previous_close"] == 19.0
	assert result["market_value"] == 60.0
	assert result["profit_loss"] == 30.0
	assert result["profit_loss_percent"] == 100.0


def test_upsert_portfolio_snapshot_uses_given_summary_without_recomputing(monkeypatch):
	fake_db = FakeDb()
	service = database_service.DataBaseService()

	monkeypatch.setattr(
		database_service,
		"get_db_connection",
		lambda: fake_db,
	)
	monkeypatch.setattr(
		service,
		"_ensure_portfolio_history_table",
		lambda _db: None,
	)

	def fail_if_called(_portfolio_id):
		raise AssertionError("Should not recompute summary")

	monkeypatch.setattr(
		service,
		"get_portfolio_summary",
		fail_if_called,
	)

	summary = {
		"cash_balance": 200.0,
		"total_value": 1200.0,
	}

	result = service.upsert_portfolio_snapshot(
		1,
		snapshot_date=date(2026, 8, 5),
		summary=summary,
	)

	assert fake_db.commit_called is True
	assert fake_db.cursor_obj.closed is True
	assert fake_db.closed is True
	assert result == {
		"portfolio_id": 1,
		"snapshot_date": "2026-08-05",
		"cash_balance": 200.0,
		"portfolio_value": 1200.0,
	}


def test_get_market_quote_defaults_to_zero_on_lookup_failure(monkeypatch):
	service = database_service.DataBaseService()

	def raise_lookup_error(_ticker):
		raise RuntimeError("boom")

	monkeypatch.setattr(
		database_service,
		"get_info",
		raise_lookup_error,
	)

	current_price, previous_close = service._get_market_quote("AAPL")

	assert current_price == Decimal("0")
	assert previous_close == Decimal("0")


def test_add_holding_rejects_missing_required_fields():
	service = database_service.DataBaseService()

	try:
		service.add_holding({"portfolio_id": 1})
		raise AssertionError("Expected ValueError")
	except ValueError as error:
		message = str(error)
		assert "Missing required fields" in message
		assert "asset_id" in message


def test_add_holding_rejects_non_positive_shares():
	service = database_service.DataBaseService()

	payload = {
		"portfolio_id": 1,
		"asset_id": 1,
		"ticker": "AAPL",
		"company_name": "Apple",
		"shares": 0,
		"cost_basis": 10,
		"purchase_date": "2026-08-05",
	}

	try:
		service.add_holding(payload)
		raise AssertionError("Expected ValueError")
	except ValueError as error:
		assert str(error) == "shares must be greater than zero."


def test_add_holding_rejects_negative_cost_basis():
	service = database_service.DataBaseService()

	payload = {
		"portfolio_id": 1,
		"asset_id": 1,
		"ticker": "AAPL",
		"company_name": "Apple",
		"shares": 2,
		"cost_basis": -1,
		"purchase_date": "2026-08-05",
	}

	try:
		service.add_holding(payload)
		raise AssertionError("Expected ValueError")
	except ValueError as error:
		assert str(error) == "cost_basis cannot be negative."


def test_withdraw_cash_rejects_invalid_amount_before_db_work():
	service = database_service.DataBaseService()

	try:
		service.withdraw_cash(1, "not-a-number")
		raise AssertionError("Expected ValueError")
	except ValueError as error:
		assert "Withdrawal amount must be a valid number." == str(error)


def test_deposit_cash_rejects_invalid_amount_before_db_work():
	service = database_service.DataBaseService()

	try:
		service.deposit_cash(1, "not-a-number")
		raise AssertionError("Expected ValueError")
	except ValueError as error:
		assert "Deposit amount must be a valid number." == str(error)

