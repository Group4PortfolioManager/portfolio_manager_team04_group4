import importlib

from werkzeug.exceptions import NotFound

from app.config import Config


def _load_main_with_mocks(monkeypatch, portfolios):
	import app.database as database_module
	import scripts.init_db as init_db_module

	calls = {
		"start_database": 0,
		"get_portfolios": 0,
		"get_initial_data": 0,
		"portfolio_arg": None,
	}

	monkeypatch.setattr(
		init_db_module,
		"start_database",
		lambda: calls.__setitem__(
			"start_database",
			calls["start_database"] + 1,
		),
	)

	monkeypatch.setattr(
		database_module,
		"get_db_connection",
		lambda: object(),
	)

	def fake_get_portfolios(_db):
		calls["get_portfolios"] += 1
		return portfolios

	def fake_get_initial_data(_db, portfolio):
		calls["get_initial_data"] += 1
		calls["portfolio_arg"] = portfolio
		return [], []

	monkeypatch.setattr(
		database_module,
		"get_portfolios",
		fake_get_portfolios,
	)
	monkeypatch.setattr(
		database_module,
		"get_initial_data",
		fake_get_initial_data,
	)

	import app.main as main_module
	main_module = importlib.reload(main_module)

	return main_module, calls


def test_config_defaults():
	assert Config.DEBUG is True
	assert Config.TESTING is False
	assert Config.JSON_SORT_KEYS is False


def test_main_bootstrap_uses_first_portfolio(monkeypatch):
	main_module, calls = _load_main_with_mocks(
		monkeypatch,
		[
			{"portfolio_id": 7, "portfolio_name": "Demo"},
			{"portfolio_id": 8, "portfolio_name": "Alt"},
		],
	)

	assert calls["start_database"] >= 1
	assert calls["get_portfolios"] >= 1
	assert calls["get_initial_data"] >= 1
	assert calls["portfolio_arg"] == {
		"portfolio_id": 7,
		"portfolio_name": "Demo",
	}

	client = main_module.app.test_client()
	response = client.get("/")

	assert response.status_code == 200
	assert response.get_json() == {
		"message": "Welcome to the Portfolio Manager API"
	}


def test_main_bootstrap_passes_none_when_no_portfolios(monkeypatch):
	_, calls = _load_main_with_mocks(monkeypatch, [])

	assert calls["portfolio_arg"] is None


def test_main_error_handlers(monkeypatch):
	main_module, _ = _load_main_with_mocks(monkeypatch, [])

	http_payload, http_code = main_module.handle_http_error(
		NotFound("Missing")
	)
	unexpected_payload, unexpected_code = (
		main_module.handle_unexpected_error(
			RuntimeError("boom")
		)
	)

	assert http_code == 404
	assert http_payload == {"error": "Missing"}
	assert unexpected_code == 500
	assert unexpected_payload == {
		"error": "Internal server error: boom"
	}
