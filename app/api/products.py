from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Category, Product, Role
from app.schemas import (
    PaginatedProductSchema,
    ProductQuerySchema,
    ProductSchema,
    ProductUpdateSchema,
)
from app.utils.decorators import roles_required

blp = Blueprint("products", __name__, url_prefix="/api/products", description="Productos e inventario")


@blp.route("")
class ProductList(MethodView):
    @jwt_required()
    @blp.arguments(ProductQuerySchema, location="query")
    @blp.response(200, PaginatedProductSchema)
    def get(self, args):
        """Lista productos con búsqueda, filtros y paginación."""
        query = Product.query

        if args.get("q"):
            term = f"%{args['q']}%"
            query = query.filter(Product.name.ilike(term) | Product.sku.ilike(term))
        if args.get("category_id"):
            query = query.filter(Product.category_id == args["category_id"])
        if args.get("low_stock"):
            query = query.filter(Product.stock <= Product.min_stock)

        page = query.order_by(Product.name).paginate(
            page=args["page"], per_page=args["per_page"], error_out=False
        )
        return {
            "items": page.items,
            "page": page.page,
            "per_page": page.per_page,
            "total": page.total,
            "pages": page.pages,
        }

    @roles_required(Role.ADMIN, Role.MANAGER)
    @blp.arguments(ProductSchema)
    @blp.response(201, ProductSchema)
    def post(self, data):
        """Crea un producto. El stock inicial siempre es 0: se carga con un movimiento."""
        if not db.session.get(Category, data["category_id"]):
            abort(422, message="La categoría no existe.")
        product = Product(**data)
        db.session.add(product)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(409, message="Ya existe un producto con ese SKU.")
        return product


@blp.route("/<int:product_id>")
class ProductDetail(MethodView):
    @jwt_required()
    @blp.response(200, ProductSchema)
    def get(self, product_id):
        """Obtiene un producto."""
        return db.get_or_404(Product, product_id)

    @roles_required(Role.ADMIN, Role.MANAGER)
    @blp.arguments(ProductUpdateSchema)
    @blp.response(200, ProductSchema)
    def patch(self, data, product_id):
        """Actualiza campos de un producto. El stock no se edita aquí."""
        product = db.get_or_404(Product, product_id)
        if "category_id" in data and not db.session.get(Category, data["category_id"]):
            abort(422, message="La categoría no existe.")
        for key, value in data.items():
            setattr(product, key, value)
        db.session.commit()
        return product

    @roles_required(Role.ADMIN)
    @blp.response(204)
    def delete(self, product_id):
        """Elimina un producto y su historial. Solo admin."""
        product = db.get_or_404(Product, product_id)
        db.session.delete(product)
        db.session.commit()
        return ""


@blp.route("/low-stock")
class LowStock(MethodView):
    @jwt_required()
    @blp.response(200, ProductSchema(many=True))
    def get(self):
        """Productos en o por debajo del stock mínimo."""
        return (
            Product.query.filter(Product.stock <= Product.min_stock)
            .order_by(Product.stock)
            .all()
        )
