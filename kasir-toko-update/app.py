from flask import Flask
from config import Config
from rute.web import web_bp
from rute.api import api_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
