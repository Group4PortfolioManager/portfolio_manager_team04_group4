from flask import Flask
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
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
CORS(
    app,
     resources={
         r"/*": {
             "origins": [
                 "http://localhost:5173",
                 "http://127.0.0.1:5173",
              ]
        }
    },
)

@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = ("strict-origin-when-cross-origin")
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "object-src 'none'"
    )
    
    return response



@app.route('/')
def index():
    return {'message': 'Welcome to the Portfolio Manager API'}


@app.errorhandler(HTTPException)
def handle_http_error(exc):
    return {'error': exc.description}, exc.code


@app.errorhandler(Exception)
def handle_unexpected_error(exc):
    return {'error': f'Internal server error: {exc}'}, 500

app.register_blueprint(api_bp)

if __name__ == '__main__':
    app.run(debug=True)