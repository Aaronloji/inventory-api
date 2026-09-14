from app.extensions import db


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))

    products = db.relationship("Product", back_populates="category")

    def __repr__(self) -> str:
        return f"<Category {self.name}>"
