import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from .models.database import init_db

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config["DATABASE_PATH"] = os.getenv("DATABASE_PATH", "./atlas.db")

    CORS(app, origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")])

    # Initialise database
    with app.app_context():
        init_db(app.config["DATABASE_PATH"])

    # Register blueprints
    from .routes.requests import requests_bp
    from .routes.technicians import technicians_bp
    from .routes.dashboard import dashboard_bp

    app.register_blueprint(requests_bp, url_prefix="/api")
    app.register_blueprint(technicians_bp, url_prefix="/api")
    app.register_blueprint(dashboard_bp, url_prefix="/api")

    return app
