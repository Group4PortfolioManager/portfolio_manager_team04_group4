from flask import Blueprint
from app.services.portfolio_service import PortfolioService

api_bp = Blueprint('api_bp', __name__)
portfolio_service = PortfolioService()


@api_bp.route('/portfolios/<int:portfolio_id>', methods=['GET'])
def get_portfolio(portfolio_id):
    portfolio = portfolio_service.get_portfolio_by_id(portfolio_id)
    if portfolio is None:
        return {'error': 'Portfolio not found'}, 404
    return portfolio, 200


@api_bp.route('/portfolios/<int:portfolio_id>/holdings', methods=['GET'])
def get_portfolio_holdings(portfolio_id):
    holdings = portfolio_service.get_portfolio_holdings(portfolio_id)
    if not holdings:
        return {'error': 'No holdings found for this portfolio'}, 404
    return holdings, 200


@api_bp.route('/holdings/<int:holding_id>', methods=['GET'])
def get_holding(holding_id):
    holding = portfolio_service.get_holding_by_id(holding_id)
    if holding is None:
        return {'error': 'Holding not found'}, 404
    return holding, 200


@api_bp.route('/assets', methods=['GET'])
def get_assets():
    return portfolio_service.get_all_assets(), 200


@api_bp.route('/assets/<int:asset_id>', methods=['GET'])
def get_asset(asset_id):
    asset = portfolio_service.get_asset_by_id(asset_id)
    if asset is None:
        return {'error': 'Asset not found'}, 404
    return asset, 200


@api_bp.route('/stocks/<ticker>', methods=['GET'])
def get_stock(ticker):
    stock = portfolio_service.get_stock(ticker)
    if stock is None:
        return {'error': 'Stock not found'}, 404
    return stock, 200
