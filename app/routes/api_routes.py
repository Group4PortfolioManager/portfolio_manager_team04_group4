from flask import Blueprint, request

from app.services.database_service import DataBaseService


api_bp = Blueprint("api_bp", __name__)
database_service = DataBaseService()


@api_bp.route("/portfolios", methods=["GET"])
def get_portfolios():
    try:
        portfolios = (
            database_service.get_all_portfolios()
        )

        if portfolios is None:
            return {
                "error": "Portfolios not found"
            }, 404

        return portfolios, 200

    except Exception:
        return {
            "error": "Unable to load portfolios"
        }, 500


@api_bp.route(
    "/portfolios/<int:portfolio_id>",
    methods=["GET"],
)
def get_portfolio(portfolio_id):
    try:
        portfolio = (
            database_service.get_portfolio_by_id(
                portfolio_id
            )
        )

        if portfolio is None:
            return {
                "error": "Portfolio not found"
            }, 404

        summary = (
            database_service.get_portfolio_summary(
                portfolio_id
            )
        )

        if summary is None:
            return {
                "error": "Portfolio summary not found"
            }, 404

        return {
            **portfolio,
            **summary,
        }, 200

    except Exception:
        return {
            "error": "Unable to load portfolio"
        }, 500


@api_bp.route(
    "/portfolios/<int:portfolio_id>/holdings",
    methods=["GET"],
)
def get_portfolio_holdings(portfolio_id):
    try:
        holdings = (
            database_service.get_portfolio_holdings(
                portfolio_id
            )
        )

        return holdings or [], 200

    except Exception:
        return {
            "error": "Unable to load holdings"
        }, 500


@api_bp.route(
    "/holdings/<int:holding_id>",
    methods=["GET"],
)
def get_holding(holding_id):
    try:
        holding = (
            database_service.get_holding_by_id(
                holding_id
            )
        )

        if holding is None:
            return {
                "error": "Holding not found"
            }, 404

        return holding, 200

    except Exception:
        return {
            "error": "Unable to load holding"
        }, 500


@api_bp.route("/assets", methods=["GET"])
def get_assets():
    try:
        assets = database_service.get_all_assets()
        return assets, 200

    except Exception:
        return {
            "error": "Unable to load assets"
        }, 500


@api_bp.route(
    "/assets/<int:asset_id>",
    methods=["GET"],
)
def get_asset(asset_id):
    try:
        asset = database_service.get_asset_by_id(
            asset_id
        )

        if asset is None:
            return {
                "error": "Asset not found"
            }, 404

        return asset, 200

    except Exception:
        return {
            "error": "Unable to load asset"
        }, 500


@api_bp.route(
    "/portfolios/<int:portfolio_id>/buy",
    methods=["POST"],
)
def buy_holding(portfolio_id):
    data = request.get_json(silent=True) or {}

    asset_id = data.get("asset_id")
    ticker = data.get("ticker")
    company_name = data.get("company_name")
    shares = data.get("shares")
    cost_basis = data.get("cost_basis")
    purchase_date = data.get("purchase_date")

    if (
        asset_id is None
        or not ticker
        or not company_name
        or shares is None
        or cost_basis is None
        or purchase_date is None
    ):
        return {
            "error": (
                "asset_id, ticker, company_name, shares, "
                "cost_basis, and purchase_date are required"
            )
        }, 400

    holding = {
        "portfolio_id": portfolio_id,
        "asset_id": asset_id,
        "ticker": ticker,
        "company_name": company_name,
        "shares": shares,
        "cost_basis": cost_basis,
        "purchase_date": purchase_date,
    }

    try:
        trade = database_service.add_holding(
            holding
        )

        status_code = (
            201
            if trade.get("action") == "created"
            else 200
        )

        return trade, status_code

    except ValueError as error:
        return {
            "error": str(error)
        }, 400

    except Exception:
        return {
            "error": "Unable to buy holding"
        }, 500


@api_bp.route(
    "/portfolios/<int:portfolio_id>/sell",
    methods=["POST"],
)
def sell_holding(portfolio_id):
    data = request.get_json(silent=True) or {}

    ticker = data.get("ticker")
    shares = data.get("shares")
    sale_price = data.get("sale_price")

    if (
        not ticker
        or shares is None
        or sale_price is None
    ):
        return {
            "error": (
                "ticker, shares, and sale_price "
                "are required"
            )
        }, 400

    try:
        trade = database_service.remove_shares(
            portfolio_id,
            ticker,
            shares,
            sale_price,
        )

        return trade, 200

    except ValueError as error:
        return {
            "error": str(error)
        }, 400

    except Exception:
        return {
            "error": "Unable to sell holding"
        }, 500