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
        cursor.execute("SELECT * FROM holdings WHERE holding_id = %s;", (holding_id,)) # Loads Holdings Related to Specific Portfolio
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
        cursor.execute("SELECT * FROM asset WHERE asset_id = %s;", (asset_id,)) # Loads Holdings Related to Specific Portfolio
        asset = cursor.fetchall()
        cursor.close()
        return asset