from flask.views import MethodView
from flask_smorest import Blueprint

from app.extensions import db
from app.models import Role, User
from app.schemas import UserSchema, UserUpdateSchema
from app.utils.decorators import roles_required

blp = Blueprint("users", __name__, url_prefix="/api/users", description="Gestión de usuarios")


@blp.route("")
class UserList(MethodView):
    @roles_required(Role.ADMIN)
    @blp.response(200, UserSchema(many=True))
    def get(self):
        """Lista los usuarios. Solo admin."""
        return User.query.order_by(User.username).all()


@blp.route("/<int:user_id>")
class UserDetail(MethodView):
    @roles_required(Role.ADMIN)
    @blp.arguments(UserUpdateSchema)
    @blp.response(200, UserSchema)
    def patch(self, data, user_id):
        """Cambia el rol o activa/desactiva un usuario. Solo admin."""
        user = db.get_or_404(User, user_id)
        for key, value in data.items():
            setattr(user, key, value)
        db.session.commit()
        return user
