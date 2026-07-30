from app.database import get_db_connection

class DataBaseService:
    def __init__(self):
        self._db = None

    @property
    def db(self):
        if self._db is None:
            self._db = get_db_connection()
        return self._db

    def get_all_portfolios(self):
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM portfolio;") # Load Portfolios
        portfolios = cursor.fetchall()
        cursor.close()
        return portfolios

    def get_portfolio_by_id(self, portfolio_id):
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM portfolio WHERE portfolio_id = %s;", (portfolio_id,)) # Load Portfolios
        portfolio = cursor.fetchall()
        cursor.close()
        return portfolio

    def get_portfolio_holdings(self, portfolio_id):
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM holdings WHERE portfolio_id = %s;", (portfolio_id,)) # Loads Holdings Related to Specific Portfolio
        holdings = cursor.fetchall()
        cursor.close()
        return holdings

    def get_holding_by_id(self, holding_id):
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM holdings WHERE holding_id = %s;", (holding_id,))
        holding = cursor.fetchall()
        cursor.close()
        return holding
    
    def get_holding_by_ticker(self, ticker):
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM holdings WHERE ticker = %s;", (ticker,))
        holding = cursor.fetchall()
        cursor.close()
        return holding

    def get_all_assets(self):
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM asset;") # Loads Assets
        assets = cursor.fetchall()
        cursor.close()
        return assets

    def get_asset_by_id(self, asset_id):
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM asset WHERE asset_id = %s;", (asset_id,))
        asset = cursor.fetchall()
        cursor.close()
        return asset
    
    def add_portfolio(self, portfolio):
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("INSERT INTO portfolio (portfolio_name, cash_balance, created_at) VALUES (%s, %s, NOW());", (portfolio['portfolio_name'], portfolio['cash_balance'],))
        self.db.commit()
        cursor.close()
    
    def add_holding(self, holding):
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("INSERT INTO holdings (portfolio_id, asset_id, ticker, company_name, shares, current_price, market_value, cost_basis, profit_loss) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);", (holding['portfolio_id'], holding['asset_id'], holding['ticker'], holding['company_name'], holding['shares'], holding['current_price'], holding['market_value'], holding['cost_basis'], holding['profit_loss'],))
        self.db.commit()
        cursor.close()
    
    def add_asset(self, asset_type):
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("INSERT INTO asset (asset_type) VALUES (%s);", (asset_type,))
        self.db.commit()
        cursor.close()
    
    def update_portfolio(self, portfolio):
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("UPDATE portfolio SET portfolio_name = %s, cash_balance = %s, created_at = %s WHERE portfolio_id = %s", (portfolio['portfolio_name'], portfolio['cash_balance'], portfolio['created_at'], portfolio['portfolio_id'],))
        self.db.commit()
        cursor.close()
            
    def update_holding(self, holding):
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("UPDATE holdings SET portfolio_id = %s, asset_id = %s, ticker = %s, company_name = %s, shares = %s, current_price = %s, market_value = %s, cost_basis = %s, profit_loss = %s WHERE holding_id = %s", (holding['portfolio_id'], holding['asset_id'], holding['ticker'], holding['company_name'], holding['shares'], holding['current_price'], holding['market_value'], holding['cost_basis'], holding['profit_loss'], holding['holding_id'],))
        self.db.commit()
        cursor.close()
    
    def delete_portfolio_by_id(self, portfolio_id):
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("DELETE FROM portfolio WHERE portfolio_id = %s;", (portfolio_id,))
        self.db.commit()
        cursor.close()
    
    def delete_holding_by_id(self, holding_id):
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("DELETE FROM holdings WHERE holding_id = %s;", (holding_id,))
        self.db.commit()
        cursor.close()
    
    def delete_asset_by_id(self, asset_id):
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("DELETE FROM asset WHERE asset_id = %s;", (asset_id,))
        self.db.commit()
        cursor.close()