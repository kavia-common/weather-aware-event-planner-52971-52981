from flask import Flask
from flask_cors import CORS
from flask_smorest import Api

from .config import Config
from .db import db
from .routes.health import blp
from .routes.locations import blp as locations_blp
from .routes.events import blp as events_blp
from .routes.weather import blp as weather_blp
from .routes.recommendation import blp as recommendation_blp


# Initialize Flask app
app = Flask(__name__)
app.url_map.strict_slashes = False

# Load configuration
cfg = Config()
app.config["SECRET_KEY"] = cfg.SECRET_KEY
app.config["API_TITLE"] = cfg.API_TITLE
app.config["API_VERSION"] = cfg.API_VERSION
app.config["OPENAPI_VERSION"] = cfg.OPENAPI_VERSION
app.config["OPENAPI_URL_PREFIX"] = cfg.OPENAPI_URL_PREFIX
app.config["OPENAPI_SWAGGER_UI_PATH"] = cfg.OPENAPI_SWAGGER_UI_PATH
app.config["OPENAPI_SWAGGER_UI_URL"] = cfg.OPENAPI_SWAGGER_UI_URL

# Database config
app.config["SQLALCHEMY_DATABASE_URI"] = cfg.SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = cfg.SQLALCHEMY_TRACK_MODIFICATIONS

# CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize extensions
db.init_app(app)
api = Api(app)

# Register blueprints
api.register_blueprint(blp)
api.register_blueprint(locations_blp)
api.register_blueprint(events_blp)
api.register_blueprint(weather_blp)
api.register_blueprint(recommendation_blp)

# Create tables if not present (dev-friendly; for production use proper migrations)
with app.app_context():
    try:
        db.create_all()
    except Exception as exc:
        # Avoid hard failures in bootstrap; log to stdout
        print(f"[Bootstrap] DB initialization error: {exc}")
