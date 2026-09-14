from datetime import datetime, timedelta, timezone
from decimal import Decimal

from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_smorest import Blueprint, abort
from sqlalchemy import func

from app.extensions import db
from app.models import Category, MovementType, Product, Role, StockMovement
from app.schemas import (
    MovementQuerySchema,
    MovementSchema,
    PaginatedMovementSchema,
    StatsSchema,
)
from app.utils.decorators import roles_required

blp = Blueprint(
    "movements", __name__, url_prefix="/api", description="Movimientos de stock y reportes"
)


@blp.route("/movements")
class MovementList(MethodView):
    @jwt_required()
    @blp.arguments(MovementQuerySchema, location="query")
    @blp.response(200, PaginatedMovementSchema)
    def get(self, args):
        """Historial de movimientos, del más reciente al más antiguo."""
        query = StockMovement.query
        if args.get("product_id"):
            query = query.filter(StockMovement.product_id == args["product_id"])
        if args.get("type"):
            query = query.filter(StockMovement.type == args["type"])

        page = query.order_by(StockMovement.created_at.desc()).paginate(
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
    @blp.arguments(MovementSchema)
    @blp.response(201, MovementSchema)
    def post(self, data):
        """Registra un movimiento y actualiza el stock del producto.

        - `in`: suma al stock
        - `out`: resta del stock (falla si no alcanza)
        - `adjust`: fija el stock en el valor indicado
        """
        product = db.session.get(Product, data["product_id"])
        if not product:
            abort(422, message="El producto no existe.")

        qty = data["quantity"]
        if data["type"] == MovementType.IN:
            product.stock += qty
        elif data["type"] == MovementType.OUT:
            if product.stock < qty:
                abort(409, message=f"Stock insuficiente: disponible {product.stock}.")
            product.stock -= qty
        else:  # adjust
            product.stock = qty

        movement = StockMovement(
            product_id=product.id,
            user_id=int(get_jwt_identity()),
            type=data["type"],
            quantity=qty,
            note=data.get("note"),
            stock_after=product.stock,
        )
        db.session.add(movement)
        db.session.commit()
        return movement


@blp.route("/stats")
class Stats(MethodView):
    @jwt_required()
    @blp.response(200, StatsSchema)
    def get(self):
        """Métricas de resumen para el dashboard."""
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        value = db.session.query(
            func.coalesce(func.sum(Product.unit_price * Product.stock), 0)
        ).scalar()
        return {
            "total_products": db.session.query(func.count(Product.id)).scalar(),
            "total_categories": db.session.query(func.count(Category.id)).scalar(),
            "low_stock_count": Product.query.filter(
                Product.stock <= Product.min_stock
            ).count(),
            "inventory_value": Decimal(value),
            "movements_last_7_days": StockMovement.query.filter(
                StockMovement.created_at >= week_ago
            ).count(),
        }
