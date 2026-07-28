from flask import Flask
from app.config import Config
from app.routes.api_routes import api_bp
from scripts.init_db import start_database
from app.database import get_db_connection, get_portfolios, get_initial_data

start_database()
db = get_db_connection()
portfolios = get_portfolios(db)
portfolio = None
if len(portfolios) < 2:
    portfolio = None if len(portfolios) == 0 else portfolios[0]
#TODO: #If more than 1, ask user to select portfolio
else:
    portfolio = portfolios[0]
assets, holdings = get_initial_data(db, portfolio)

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/')
def index():
    return {'message': 'Welcome to the Portfolio Manager API'}

app.register_blueprint(api_bp)

if __name__ == '__main__':
    app.run(debug=True)