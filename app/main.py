from flask import Flask
from flask_restful import Api
from app.config import Config
from app.routes.portfolio_routes import PortfolioResource

app = Flask(__name__)
app.config.from_object(Config)
api = Api(app)

api.add_resource(PortfolioResource, '/portfolios/<int:portfolio_id>')

if __name__ == '__main__':
    app.run(debug=True)