from flask import Flask, jsonify, redirect
from flask_cors import CORS

from app.config import Config
from app.extensions import db, jwt, migrate, rest_api


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    rest_api.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    from app.api.auth import blp as auth_blp
    from app.api.categories import blp as categories_blp
    from app.api.movements import blp as movements_blp
    from app.api.products import blp as products_blp
    from app.api.users import blp as users_blp

    rest_api.register_blueprint(auth_blp)
    rest_api.register_blueprint(categories_blp)
    rest_api.register_blueprint(products_blp)
    rest_api.register_blueprint(movements_blp)
    rest_api.register_blueprint(users_blp)

    @app.get("/")
    def index():
        """La raiz lleva a la documentacion interactiva."""
        return redirect("/docs")

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    @jwt.expired_token_loader
    def expired_token(_header, _payload):
        return jsonify(message="El token expiro."), 401

    @jwt.unauthorized_loader
    def missing_token(reason):
        return jsonify(message="Falta el token de acceso.", detail=reason), 401

    return app
