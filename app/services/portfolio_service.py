class PortfolioService:
    def get_all_portfolios(self):
        return [
            {'id': 1, 'name': 'Demo Portfolio', 'value': 10000.0}
        ]

    def get_portfolio_by_id(self, portfolio_id):
        if portfolio_id == 1:
            return {'id': 1, 'name': 'Demo Portfolio', 'value': 10000.0}
        return None

    def get_portfolio_holdings(self, portfolio_id):
        if portfolio_id == 1:
            return [
                {'id': 1, 'portfolio_id': 1, 'ticker': 'AAPL', 'quantity': 10, 'avg_cost': 150.0},
                {'id': 2, 'portfolio_id': 1, 'ticker': 'MSFT', 'quantity': 5, 'avg_cost': 300.0}
            ]
        return []

    def get_holding_by_id(self, holding_id):
        if holding_id == 1:
            return {'id': 1, 'portfolio_id': 1, 'ticker': 'AAPL', 'quantity': 10, 'avg_cost': 150.0}
        if holding_id == 2:
            return {'id': 2, 'portfolio_id': 1, 'ticker': 'MSFT', 'quantity': 5, 'avg_cost': 300.0}
        return None

    def get_all_assets(self):
        return [
            {'id': 1, 'ticker': 'AAPL', 'name': 'Apple Inc.'},
            {'id': 2, 'ticker': 'MSFT', 'name': 'Microsoft Corp.'}
        ]

    def get_asset_by_id(self, asset_id):
        if asset_id == 1:
            return {'id': 1, 'ticker': 'AAPL', 'name': 'Apple Inc.'}
        if asset_id == 2:
            return {'id': 2, 'ticker': 'MSFT', 'name': 'Microsoft Corp.'}
        return None

    def get_stock(self, ticker):
        if ticker.upper() == 'AAPL':
            return {'ticker': 'AAPL', 'name': 'Apple Inc.', 'price': 190.25}
        if ticker.upper() == 'MSFT':
            return {'ticker': 'MSFT', 'name': 'Microsoft Corp.', 'price': 420.10}
        return None
