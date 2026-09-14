from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Category, Role
from app.schemas import CategorySchema
from app.utils.decorators import roles_required

blp = Blueprint(
    "categories", __name__, url_prefix="/api/categories", description="Categorías de producto"
)


@blp.route("")
class CategoryList(MethodView):
    @jwt_required()
    @blp.response(200, CategorySchema(many=True))
    def get(self):
        """Lista todas las categorías."""
        return Category.query.order_by(Category.name).all()

    @roles_required(Role.ADMIN, Role.MANAGER)
    @blp.arguments(CategorySchema)
    @blp.response(201, CategorySchema)
    def post(self, data):
        """Crea una categoría."""
        category = Category(**data)
        db.session.add(category)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(409, message="Ya existe una categoría con ese nombre.")
        return category


@blp.route("/<int:category_id>")
class CategoryDetail(MethodView):
    @jwt_required()
    @blp.response(200, CategorySchema)
    def get(self, category_id):
        """Obtiene una categoría."""
        return db.get_or_404(Category, category_id)

    @roles_required(Role.ADMIN, Role.MANAGER)
    @blp.arguments(CategorySchema)
    @blp.response(200, CategorySchema)
    def put(self, data, category_id):
        """Actualiza una categoría."""
        category = db.get_or_404(Category, category_id)
        for key, value in data.items():
            setattr(category, key, value)
        db.session.commit()
        return category

    @roles_required(Role.ADMIN)
    @blp.response(204)
    def delete(self, category_id):
        """Elimina una categoría sin productos asociados. Solo admin."""
        category = db.get_or_404(Category, category_id)
        if category.products:
            abort(409, message="La categoría tiene productos asociados.")
        db.session.delete(category)
        db.session.commit()
        return ""
