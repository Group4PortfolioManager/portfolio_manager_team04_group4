from flask import Flask
import pandas as pd

from app.routes import api_routes


class FakeDbService:
	def __init__(self):
		self.snapshot_calls = []
		self.add_holding_calls = []
		self.remove_shares_calls = []
		self.deposit_calls = []
		self.withdraw_calls = []
		self.deleted_portfolios = []
		self.raise_on_assets = False
		self.raise_on_holdings = False
		self.summary_total_value = 1250.0

	def get_portfolio_by_id(self, portfolio_id):
		if portfolio_id == 404:
			return None
		return {
			"portfolio_id": portfolio_id,
			"portfolio_name": "Demo",
			"cash_balance": 500.0,
		}

	def get_portfolio_summary(self, portfolio_id):
		if portfolio_id == 500:
			return None
		return {
			"total_value": self.summary_total_value,
			"stocks_value": 600.0,
			"bonds_value": 100.0,
			"crypto_value": 50.0,
			"day_gain": 20.0,
			"day_gain_percent": 1.5,
			"total_return": 200.0,
			"cost_basis_total": 1050.0,
		}

	def upsert_portfolio_snapshot(self, portfolio_id, summary=None):
		self.snapshot_calls.append((portfolio_id, summary))
		portfolio_value = (
			summary["total_value"]
			if summary is not None
			else 0.0
		)
		return {
			"portfolio_id": portfolio_id,
			"portfolio_value": portfolio_value,
		}

	def get_portfolio_holdings(self, portfolio_id):
		if self.raise_on_holdings:
			raise RuntimeError("holdings-fail")
		if portfolio_id == 0:
			return None
		return [
			{
				"holding_id": 1,
				"ticker": "AAPL",
				"shares": 10,
				"current_price": 200.0,
				"market_value": 2000.0,
			}
		]

	def get_all_portfolios(self):
		return [
			{
				"portfolio_id": 1,
				"portfolio_name": "Demo",
			},
		]

	def get_holding_by_id(self, holding_id):
		if holding_id == 404:
			return None
		return {
			"holding_id": holding_id,
			"ticker": "AAPL",
		}

	def get_all_assets(self):
		if self.raise_on_assets:
			raise RuntimeError("assets-fail")
		return [
			{"asset_id": 1, "asset_type": "Stock"},
			{"asset_id": 2, "asset_type": "Bond"},
		]

	def get_asset_by_id(self, asset_id):
		if asset_id == 99:
			return None
		if asset_id == 4:
			return {"asset_id": 4, "asset_type": "Cash"}
		return {"asset_id": asset_id, "asset_type": "Stock"}

	def add_holding(self, holding):
		self.add_holding_calls.append(holding)
		return {
			"action": "created",
			"ticker": holding["ticker"],
			"shares": holding["shares"],
		}

	def remove_shares(self, portfolio_id, ticker, shares, sale_price):
		self.remove_shares_calls.append(
			(portfolio_id, ticker, shares, sale_price)
		)
		return {
			"action": "updated",
			"ticker": ticker,
			"shares_removed": float(shares),
			"sale_price": float(sale_price),
		}

	def deposit_cash(self, portfolio_id, amount):
		self.deposit_calls.append((portfolio_id, amount))
		return {
			"action": "deposit",
			"portfolio_id": portfolio_id,
			"amount": float(amount),
			"cash_balance": 800.0,
		}

	def withdraw_cash(self, portfolio_id, amount):
		self.withdraw_calls.append((portfolio_id, amount))
		if float(amount) > 500:
			raise ValueError("Insufficient cash balance for withdrawal.")
		return {
			"action": "withdraw",
			"portfolio_id": portfolio_id,
			"amount": float(amount),
			"cash_balance": 300.0,
		}

	def delete_portfolio_by_id(self, portfolio_id):
		if portfolio_id == 404:
			return False
		self.deleted_portfolios.append(portfolio_id)
		return True


def _performance_history_stub(portfolio_id, window_type="months", window_size=12):
	if portfolio_id == 404:
		return None
	if window_size == 3:
		raise ValueError("window issue")
	if window_size == 13:
		raise RuntimeError("perf-fail")
	return [
		{"date": "2026-08-01", "label": "Aug", "value": 100.0},
	]


def _build_client():
	app = Flask(__name__)
	app.register_blueprint(api_routes.api_bp)
	return app.test_client()


def test_get_portfolio_merges_summary_and_reuses_it_for_snapshot(monkeypatch):
	fake_db = FakeDbService()
	monkeypatch.setattr(api_routes, "database_service", fake_db)

	client = _build_client()
	response = client.get("/portfolios/1")

	assert response.status_code == 200
	payload = response.get_json()
	assert payload["portfolio_id"] == 1
	assert payload["total_value"] == 1250.0
	assert fake_db.snapshot_calls == [
		(
			1,
			{
				"total_value": 1250.0,
				"stocks_value": 600.0,
				"bonds_value": 100.0,
				"crypto_value": 50.0,
				"day_gain": 20.0,
				"day_gain_percent": 1.5,
				"total_return": 200.0,
				"cost_basis_total": 1050.0,
			},
		)
	]


def test_get_portfolios_returns_list(monkeypatch):
	fake_db = FakeDbService()
	monkeypatch.setattr(api_routes, "database_service", fake_db)

	client = _build_client()
	response = client.get("/portfolios")

	assert response.status_code == 200
	payload = response.get_json()
	assert payload == [{"portfolio_id": 1, "portfolio_name": "Demo"}]


def test_delete_portfolio_rejects_non_zero_value(monkeypatch):
	fake_db = FakeDbService()
	fake_db.summary_total_value = 100.0
	monkeypatch.setattr(api_routes, "database_service", fake_db)

	client = _build_client()
	response = client.delete("/portfolios/1")

	assert response.status_code == 400
	assert "only when its total value is $0" in response.get_json()["error"]
	assert fake_db.deleted_portfolios == []


def test_delete_portfolio_succeeds_when_zero_value(monkeypatch):
	fake_db = FakeDbService()
	fake_db.summary_total_value = 0.0
	monkeypatch.setattr(api_routes, "database_service", fake_db)

	client = _build_client()
	response = client.delete("/portfolios/1")

	assert response.status_code == 200
	assert response.get_json()["message"] == "Portfolio deleted successfully"
	assert fake_db.deleted_portfolios == [1]


def test_delete_portfolio_returns_404_for_missing_portfolio(monkeypatch):
	fake_db = FakeDbService()
	monkeypatch.setattr(api_routes, "database_service", fake_db)

	client = _build_client()
	response = client.delete("/portfolios/404")

	assert response.status_code == 404
	assert response.get_json()["error"] == "Portfolio not found"


def test_get_portfolio_returns_404_for_missing_portfolio(monkeypatch):
	fake_db = FakeDbService()
	monkeypatch.setattr(api_routes, "database_service", fake_db)

	client = _build_client()
	response = client.get("/portfolios/404")

	assert response.status_code == 404
	assert response.get_json()["error"] == "Portfolio not found"


def test_get_portfolio_holdings_returns_enriched_holdings(monkeypatch):
	fake_db = FakeDbService()
	monkeypatch.setattr(api_routes, "database_service", fake_db)

	client = _build_client()
	response = client.get("/portfolios/1/holdings")

	assert response.status_code == 200
	payload = response.get_json()
	assert len(payload) == 1
	assert payload[0]["ticker"] == "AAPL"
	assert payload[0]["current_price"] == 200.0


def test_get_portfolio_holdings_handles_service_error(monkeypatch):
	fake_db = FakeDbService()
	fake_db.raise_on_holdings = True
	monkeypatch.setattr(api_routes, "database_service", fake_db)

	client = _build_client()
	response = client.get("/portfolios/1/holdings")

	assert response.status_code == 500
	assert response.get_json()["error"] == "Unable to load holdings"


def test_get_holding_returns_404_when_missing(monkeypatch):
	fake_db = FakeDbService()
	monkeypatch.setattr(api_routes, "database_service", fake_db)

	client = _build_client()
	response = client.get("/holdings/404")

	assert response.status_code == 404
	assert response.get_json()["error"] == "Holding not found"


def test_get_assets_returns_500_on_service_failure(monkeypatch):
	fake_db = FakeDbService()
	fake_db.raise_on_assets = True
	monkeypatch.setattr(api_routes, "database_service", fake_db)

	client = _build_client()
	response = client.get("/assets")

	assert response.status_code == 500
	assert response.get_json()["error"] == "Unable to load assets"


def test_get_asset_returns_404_when_missing(monkeypatch):
	fake_db = FakeDbService()
	monkeypatch.setattr(api_routes, "database_service", fake_db)

	client = _build_client()
	response = client.get("/assets/99")

	assert response.status_code == 404
	assert response.get_json()["error"] == "Asset not found"


def test_get_portfolio_performance_validation_errors(monkeypatch):
	monkeypatch.setattr(api_routes, "get_portfolio_performance_history", _performance_history_stub)
	client = _build_client()

	bad_type = client.get("/portfolios/1/performance?window_type=years&window_size=12")
	assert bad_type.status_code == 400
	assert "window_type must be" in bad_type.get_json()["error"]

	bad_size = client.get("/portfolios/1/performance?window_type=days&window_size=1")
	assert bad_size.status_code == 400
	assert bad_size.get_json()["error"] == "window_size must be at least 2"


def test_get_portfolio_performance_handles_not_found_and_exceptions(monkeypatch):
	monkeypatch.setattr(api_routes, "get_portfolio_performance_history", _performance_history_stub)
	client = _build_client()

	not_found = client.get("/portfolios/404/performance?window_type=months&window_size=12")
	assert not_found.status_code == 404
	assert not_found.get_json()["error"] == "Portfolio not found"

	value_error = client.get("/portfolios/1/performance?window_type=months&window_size=3")
	assert value_error.status_code == 400
	assert value_error.get_json()["error"] == "window issue"

	server_error = client.get("/portfolios/1/performance?window_type=months&window_size=13")
	assert server_error.status_code == 500
	assert server_error.get_json()["error"] == "Unable to load portfolio performance"


def test_get_stock_returns_price_payload(monkeypatch):
	monkeypatch.setattr(
		api_routes,
		"get_info",
		lambda _ticker: {
			"shortName": "Apple Inc.",
			"currency": "USD",
			"regularMarketPrice": 205.5,
		},
	)

	client = _build_client()
	response = client.get("/stocks/aapl")

	assert response.status_code == 200
	payload = response.get_json()
	assert payload == {
		"ticker": "AAPL",
		"name": "Apple Inc.",
		"price": 205.5,
		"currency": "USD",
	}


def test_get_stock_returns_404_when_yahoo_has_no_info(monkeypatch):
	monkeypatch.setattr(api_routes, "get_info", lambda _ticker: {})

	client = _build_client()
	response = client.get("/stocks/aapl")

	assert response.status_code == 404
	assert response.get_json()["error"] == "Stock not found"


def test_get_stock_returns_404_when_price_is_missing(monkeypatch):
	monkeypatch.setattr(
		api_routes,
		"get_info",
		lambda _ticker: {"shortName": "Apple Inc."},
	)

	client = _build_client()
	response = client.get("/stocks/aapl")

	assert response.status_code == 404
	assert "Current price was not found" in response.get_json()["error"]


def test_buy_holding_returns_201_and_saves_trade(monkeypatch):
	fake_db = FakeDbService()
	monkeypatch.setattr(api_routes, "database_service", fake_db)
	monkeypatch.setattr(
		api_routes,
		"get_info",
		lambda _ticker: {
			"shortName": "Apple Inc.",
			"regularMarketPrice": 190.0,
		},
	)

	client = _build_client()
	response = client.post(
		"/portfolios/1/buy",
		json={
			"asset_id": 1,
			"ticker": "aapl",
			"shares": 2,
		},
	)

	assert response.status_code == 201
	assert fake_db.add_holding_calls[0]["ticker"] == "AAPL"
	assert fake_db.snapshot_calls[-1][0] == 1


def test_buy_holding_rejects_cash_asset(monkeypatch):
	fake_db = FakeDbService()
	monkeypatch.setattr(api_routes, "database_service", fake_db)

	client = _build_client()
	response = client.post(
		"/portfolios/1/buy",
		json={
			"asset_id": 4,
			"ticker": "cash",
			"shares": 1,
		},
	)

	assert response.status_code == 400
	assert response.get_json()["error"] == "Cash cannot be added as a holding"


def test_buy_holding_rejects_invalid_asset_id(monkeypatch):
	fake_db = FakeDbService()
	monkeypatch.setattr(api_routes, "database_service", fake_db)

	client = _build_client()
	response = client.post(
		"/portfolios/1/buy",
		json={
			"asset_id": 99,
			"ticker": "AAPL",
			"shares": 1,
		},
	)

	assert response.status_code == 400
	assert response.get_json()["error"] == "Invalid asset_id"


def test_sell_holding_requires_ticker_and_shares(monkeypatch):
	fake_db = FakeDbService()
	monkeypatch.setattr(api_routes, "database_service", fake_db)

	client = _build_client()
	response = client.post("/portfolios/1/sell", json={"ticker": "AAPL"})

	assert response.status_code == 400
	assert response.get_json()["error"] == "ticker and shares are required"


def test_sell_holding_returns_200_and_updates_snapshot(monkeypatch):
	fake_db = FakeDbService()
	monkeypatch.setattr(api_routes, "database_service", fake_db)
	monkeypatch.setattr(
		api_routes,
		"get_info",
		lambda _ticker: {"regularMarketPrice": 210.0},
	)

	client = _build_client()
	response = client.post(
		"/portfolios/1/sell",
		json={"ticker": "aapl", "shares": 1.5},
	)

	assert response.status_code == 200
	assert fake_db.remove_shares_calls == [(1, "AAPL", 1.5, 210.0)]
	assert fake_db.snapshot_calls[-1][0] == 1


def test_sell_holding_returns_400_when_sale_price_missing(monkeypatch):
	fake_db = FakeDbService()
	monkeypatch.setattr(api_routes, "database_service", fake_db)
	monkeypatch.setattr(api_routes, "get_info", lambda _ticker: {})

	client = _build_client()
	response = client.post(
		"/portfolios/1/sell",
		json={"ticker": "aapl", "shares": 1},
	)

	assert response.status_code == 400
	assert "Unable to retrieve a current price" in response.get_json()["error"]


def test_get_stock_history_requires_dates(monkeypatch):
	client = _build_client()
	response = client.get("/stocks/AAPL/history")

	assert response.status_code == 400
	assert response.get_json()["error"] == "start_date and end_date are required"


def test_get_stock_history_returns_rows(monkeypatch):
	def fake_history(_ticker, _start, _end, interval="1d"):
		index = pd.DatetimeIndex(["2026-08-01", "2026-08-02"])
		return pd.DataFrame(
			{
				"Open": [100.0, 101.0],
				"Close": [102.0, 103.0],
			},
			index=index,
		)

	monkeypatch.setattr(api_routes, "get_historical_data", fake_history)

	client = _build_client()
	response = client.get(
		"/stocks/AAPL/history?start_date=2026-08-01&end_date=2026-08-03&interval=1d"
	)

	assert response.status_code == 200
	payload = response.get_json()
	assert payload["ticker"] == "AAPL"
	assert payload["interval"] == "1d"
	assert len(payload["data"]) == 2


def test_deposit_cash_requires_amount(monkeypatch):
	fake_db = FakeDbService()
	monkeypatch.setattr(api_routes, "database_service", fake_db)

	client = _build_client()
	response = client.post("/portfolios/1/cash/deposit", json={})

	assert response.status_code == 400
	assert response.get_json()["error"] == "amount is required"


def test_deposit_cash_success_updates_snapshot(monkeypatch):
	fake_db = FakeDbService()
	monkeypatch.setattr(api_routes, "database_service", fake_db)

	client = _build_client()
	response = client.post(
		"/portfolios/1/cash/deposit",
		json={"amount": 50},
	)

	assert response.status_code == 200
	assert fake_db.deposit_calls == [(1, 50)]
	assert fake_db.snapshot_calls[-1][0] == 1


def test_withdraw_cash_value_error_returns_400(monkeypatch):
	fake_db = FakeDbService()
	monkeypatch.setattr(api_routes, "database_service", fake_db)

	client = _build_client()
	response = client.post(
		"/portfolios/1/cash/withdraw",
		json={"amount": 600},
	)

	assert response.status_code == 400
	assert response.get_json()["error"] == "Insufficient cash balance for withdrawal."


def test_get_stock_returns_500_when_provider_raises(monkeypatch):
	monkeypatch.setattr(
		api_routes,
		"get_info",
		lambda _ticker: (_ for _ in ()).throw(RuntimeError("yahoo down")),
	)

	client = _build_client()
	response = client.get("/stocks/aapl")

	assert response.status_code == 500
	assert response.get_json()["error"] == "Unable to load stock data"


def test_get_stock_history_rejects_invalid_date_format(monkeypatch):
	client = _build_client()
	response = client.get(
		"/stocks/AAPL/history?start_date=2026/08/01&end_date=2026-08-03&interval=1d"
	)

	assert response.status_code == 400
	assert response.get_json()["error"] == "Dates must be in YYYY-MM-DD format"


def test_get_stock_history_returns_404_for_empty_data(monkeypatch):
	def fake_history(_ticker, _start, _end, interval="1d"):
		return pd.DataFrame()

	monkeypatch.setattr(api_routes, "get_historical_data", fake_history)

	client = _build_client()
	response = client.get(
		"/stocks/AAPL/history?start_date=2026-08-01&end_date=2026-08-03&interval=1d"
	)

	assert response.status_code == 404
	assert response.get_json()["error"] == "No historical data found"


def test_get_stock_history_returns_500_when_provider_fails(monkeypatch):
	def fake_history(_ticker, _start, _end, interval="1d"):
		raise RuntimeError("history provider unavailable")

	monkeypatch.setattr(api_routes, "get_historical_data", fake_history)

	client = _build_client()
	response = client.get(
		"/stocks/AAPL/history?start_date=2026-08-01&end_date=2026-08-03&interval=1d"
	)

	assert response.status_code == 500
	assert response.get_json()["error"] == "Unable to load historical data"


def test_withdraw_cash_requires_amount(monkeypatch):
	fake_db = FakeDbService()
	monkeypatch.setattr(api_routes, "database_service", fake_db)

	client = _build_client()
	response = client.post("/portfolios/1/cash/withdraw", json={})

	assert response.status_code == 400
	assert response.get_json()["error"] == "amount is required"


def test_withdraw_cash_success_updates_snapshot(monkeypatch):
	fake_db = FakeDbService()
	monkeypatch.setattr(api_routes, "database_service", fake_db)

	client = _build_client()
	response = client.post(
		"/portfolios/1/cash/withdraw",
		json={"amount": 100},
	)

	assert response.status_code == 200
	assert fake_db.withdraw_calls == [(1, 100)]
	assert fake_db.snapshot_calls[-1][0] == 1

