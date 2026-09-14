from datetime import datetime, timezone

from app.extensions import db


class MovementType:
    IN = "in"
    OUT = "out"
    ADJUST = "adjust"

    ALL = (IN, OUT, ADJUST)


class StockMovement(db.Model):
    """Registro inmutable de cada cambio de stock (trazabilidad)."""

    __tablename__ = "stock_movements"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    stock_after = db.Column(db.Integer, nullable=False)
    note = db.Column(db.String(255))
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    product = db.relationship("Product", back_populates="movements")
    user = db.relationship("User", back_populates="movements")

    def __repr__(self) -> str:
        return f"<StockMovement {self.type} {self.quantity}>"
