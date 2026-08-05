from flask import Flask

from app.routes import api_routes


class FakeDbService:
	def __init__(self):
		self.snapshot_calls = []

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
			"total_value": 1250.0,
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
		return {
			"portfolio_id": portfolio_id,
			"portfolio_value": summary["total_value"],
		}

	def get_portfolio_holdings(self, portfolio_id):
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

