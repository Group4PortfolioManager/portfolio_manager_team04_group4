from flask import Flask
from app.config import Config
from app.routes.api_routes import api_bp

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/')
def index():
    return {'message': 'Welcome to the Portfolio Manager API'}

app.register_blueprint(api_bp)


if __name__ == '__main__':
    app.run(debug=True)