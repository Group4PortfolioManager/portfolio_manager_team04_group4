class DataBaseService:
    def get_all_portfolios(self):
        return [
            {'portfolio_id': 1, 'portfolio_name': 'Demo Portfolio', 'created_at': '2023-01-01'}
        ]

    def get_portfolio_by_id(self, portfolio_id):
        if portfolio_id == 1:
            return {'portfolio_id': 1, 'portfolio_name': 'Demo Portfolio', 'created_at': '2023-01-01'}
        return None

    def get_portfolio_holdings(self, portfolio_id):
        if portfolio_id == 1:
            return [
                {'holding_id': 1, 'portfolio_id': 1,'asset_id': 1, 'ticker': 'AAPL', 'company_name': 'Apple Inc.', 'shares': 10, 'current_price': 150.0, 'market_value': 1500.0, 'cost_basis': 1200.0, 'profit_loss': 300.0},
                {'holding_id': 2, 'portfolio_id': 1, 'asset_id': 2, 'ticker': 'MSFT', 'company_name': 'Microsoft Corp.', 'shares': 5, 'current_price': 300.0, 'market_value': 1500.0, 'cost_basis': 1500.0, 'profit_loss': 0.0}
            ]
        return []

    def get_holding_by_id(self, holding_id):
        if holding_id == 1:
            return {'holding_id': 1, 'portfolio_id': 1,'asset_id': 1, 'ticker': 'AAPL', 'company_name': 'Apple Inc.', 'shares': 10, 'current_price': 150.0, 'market_value': 1500.0, 'cost_basis': 1200.0, 'profit_loss': 300.0}
        if holding_id == 2:
            return {'holding_id': 2, 'portfolio_id': 1, 'asset_id': 2, 'ticker': 'MSFT', 'company_name': 'Microsoft Corp.', 'shares': 5, 'current_price': 300.0, 'market_value': 1500.0, 'cost_basis': 1500.0, 'profit_loss': 0.0}
        return None

    def get_all_assets(self):
        return [
            {'asset_id': 1, 'asset_type': 'stock'},
            {'asset_id': 2, 'asset_type': 'stock'}
        ]
    
    def get_asset_by_id(self, asset_id):
        if asset_id == 1:
            return {'asset_id': 1, 'asset_type': 'stock'}
        if asset_id == 2:
            return {'asset_id': 2, 'asset_type': 'stock'}
        return None

    def buy_holding(self, portfolio_id, ticker, shares, price):
        return {
            'portfolio_id': portfolio_id,
            'ticker': ticker.upper(),
            'shares': shares,
            'price': price,
            'action': 'buy'
        }

    def sell_holding(self, portfolio_id, ticker, shares, price):
        return {
            'portfolio_id': portfolio_id,
            'ticker': ticker.upper(),
            'shares': shares,
            'price': price,
            'action': 'sell'
        }