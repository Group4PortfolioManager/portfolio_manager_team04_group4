from datetime import datetime

from flask import Blueprint, request
from app.services.database_service import DataBaseService
from app.services.yahoo_service import get_historical_data, get_info

api_bp = Blueprint('api_bp', __name__)
database_service = DataBaseService()

@api_bp.route('/portfolios', methods=['GET'])
def get_portfolios():
    portfolios = database_service.get_all_portfolios()
    if portfolios is None:
        return {'error': 'Portfolios not found'}, 404
    return portfolios, 200


@api_bp.route('/portfolios/<int:portfolio_id>', methods=['GET'])
def get_portfolio(portfolio_id):
    portfolio = database_service.get_portfolio_by_id(portfolio_id)
    if portfolio is None:
        return {'error': 'Portfolio not found'}, 404

    summary = database_service.get_portfolio_summary(portfolio_id)
    if summary is None:
        return {'error': 'Portfolio summary not found'}, 404

    return {**portfolio, **summary}, 200


@api_bp.route('/portfolios/<int:portfolio_id>/holdings', methods=['GET'])
def get_portfolio_holdings(portfolio_id):
    holdings = database_service.get_portfolio_holdings(portfolio_id)
    if not holdings:
        return [], 200
    return holdings, 200


@api_bp.route('/holdings/<int:holding_id>', methods=['GET'])
def get_holding(holding_id):
    holding = database_service.get_holding_by_id(holding_id)
    if holding is None:
        return {'error': 'Holding not found'}, 404
    return holding, 200


@api_bp.route('/assets', methods=['GET'])
def get_assets():
    return database_service.get_all_assets(), 200


@api_bp.route('/assets/<int:asset_id>', methods=['GET'])
def get_asset(asset_id):
    asset = database_service.get_asset_by_id(asset_id)
    if asset is None:
        return {'error': 'Asset not found'}, 404
    return asset, 200


@api_bp.route('/stocks/<ticker>', methods=['GET'])
def get_stock(ticker):
    info = get_info(ticker)
    if not info:
        return {'error': 'Stock not found'}, 404
    return {
        'ticker': ticker.upper(),
        'name': info.get('shortName') or info.get('longName') or ticker.upper(),
        'price': info.get('currentPrice'),
        'currency': info.get('currency')
    }, 200


@api_bp.route('/stocks/<ticker>/history', methods=['GET'])
def get_stock_history(ticker):
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    interval = request.args.get('interval', '1d')

    if not start_date or not end_date:
        return {'error': 'start_date and end_date are required'}, 400

    try:
        df = get_historical_data(
            ticker,
            datetime.strptime(start_date, '%Y-%m-%d'),
            datetime.strptime(end_date, '%Y-%m-%d'),
            interval=interval,
        )
    except ValueError:
        return {'error': 'Dates must be in YYYY-MM-DD format'}, 400

    if df.empty:
        return {'error': 'No historical data found'}, 404

    return {
        'ticker': ticker.upper(),
        'interval': interval,
        'data': df.reset_index().to_dict(orient='records')
    }, 200


@api_bp.route('/portfolios/<int:portfolio_id>/buy', methods=['POST'])
def buy_holding(portfolio_id):
    data = request.get_json(silent=True) or {}
    asset_id = data.get('asset_id')
    ticker = data.get('ticker')
    company_name = data.get('company_name')
    shares = data.get('shares')
    price = data.get('price')
    purchase_date = data.get('purchase_date')

    if not ticker or shares is None or price is None or purchase_date is None:
        return {'error': 'ticker, shares, price, and purchase date are required'}, 400

    holding = {
            'portfolio_id':portfolio_id,
            'asset_id':asset_id,
            'ticker':ticker,
            'company_name':company_name,
            'shares':shares,
            'cost_basis':price,
            'purchase_date':purchase_date
        }
    
    trade = database_service.add_holding(holding)
    return trade, 200


@api_bp.route('/portfolios/<int:portfolio_id>/sell', methods=['POST'])
def sell_holding(portfolio_id):
    data = request.get_json(silent=True) or {}
    ticker = data.get('ticker')
    shares = data.get('shares')
    

    if not ticker or shares is None:
        return {'error': 'ticker and shares are required'}, 400

    trade = database_service.remove_shares(portfolio_id, ticker, shares)
    if isinstance(trade, dict) and trade.get('error'):
        return trade, 400
    return trade, 200