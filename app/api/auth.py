from flask.views import MethodView
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Role, User
from app.schemas import LoginSchema, TokenSchema, UserSchema
from app.utils.decorators import roles_required

blp = Blueprint("auth", __name__, url_prefix="/api/auth", description="Autenticación y sesión")


def _tokens_for(user: User) -> dict:
    claims = {"role": user.role, "username": user.username}
    identity = str(user.id)
    return {
        "access_token": create_access_token(identity=identity, additional_claims=claims),
        "refresh_token": create_refresh_token(identity=identity, additional_claims=claims),
    }


@blp.route("/login")
class Login(MethodView):
    @blp.arguments(LoginSchema)
    @blp.response(200, TokenSchema)
    def post(self, data):
        """Inicia sesión y devuelve access + refresh token."""
        user = User.query.filter_by(username=data["username"]).first()
        if not user or not user.check_password(data["password"]):
            abort(401, message="Credenciales inválidas.")
        if not user.is_active:
            abort(403, message="Usuario desactivado.")
        return _tokens_for(user)


@blp.route("/register")
class Register(MethodView):
    @roles_required(Role.ADMIN)
    @blp.arguments(UserSchema)
    @blp.response(201, UserSchema)
    def post(self, data):
        """Crea un usuario nuevo. Solo admin."""
        user = User(
            username=data["username"],
            email=data["email"],
            role=data.get("role", Role.VIEWER),
        )
        user.set_password(data["password"])
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(409, message="El usuario o el correo ya existen.")
        return user


@blp.route("/refresh")
class Refresh(MethodView):
    @jwt_required(refresh=True)
    @blp.response(200, TokenSchema)
    def post(self):
        """Genera un access token nuevo a partir del refresh token."""
        user = db.session.get(User, int(get_jwt_identity()))
        if not user or not user.is_active:
            abort(401, message="Sesión inválida.")
        return {
            "access_token": create_access_token(
                identity=str(user.id),
                additional_claims={"role": user.role, "username": user.username},
            )
        }


@blp.route("/me")
class Me(MethodView):
    @jwt_required()
    @blp.response(200, UserSchema)
    def get(self):
        """Devuelve el usuario autenticado."""
        user = db.session.get(User, int(get_jwt_identity()))
        if not user:
            abort(404, message="Usuario no encontrado.")
        return user
