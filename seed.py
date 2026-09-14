"""Crea el esquema y carga datos de ejemplo.

    python seed.py
"""

from app import create_app
from app.extensions import db
from app.models import Category, MovementType, Product, Role, StockMovement, User

USERS = [
    ("admin", "admin@demo.com", "admin1234", Role.ADMIN),
    ("bodega", "bodega@demo.com", "bodega1234", Role.MANAGER),
    ("consulta", "consulta@demo.com", "consulta1234", Role.VIEWER),
]

CATEGORIES = [
    ("Herramientas", "Herramienta manual y eléctrica"),
    ("Repuestos", "Repuestos de línea de producción"),
    ("Consumibles", "Material de consumo rápido"),
]

PRODUCTS = [
    ("HER-001", "Taladro percutor 1/2", 1, "89000.00", 3, 12),
    ("HER-002", "Juego de llaves mixtas", 1, "34500.00", 2, 2),
    ("REP-101", "Rodamiento 6204-2RS", 2, "7800.00", 20, 45),
    ("REP-102", "Banda transportadora 2m", 2, "125000.00", 1, 1),
    ("CON-201", "Guantes de nitrilo (caja)", 3, "9500.00", 15, 60),
    ("CON-202", "Cinta aislante", 3, "1200.00", 30, 18),
]


def run() -> None:
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        users = {}
        for username, email, password, role in USERS:
            user = User(username=username, email=email, role=role)
            user.set_password(password)
            db.session.add(user)
            users[username] = user

        for name, description in CATEGORIES:
            db.session.add(Category(name=name, description=description))
        db.session.commit()

        for sku, name, category_id, price, min_stock, initial in PRODUCTS:
            product = Product(
                sku=sku,
                name=name,
                category_id=category_id,
                unit_price=price,
                min_stock=min_stock,
                stock=initial,
            )
            db.session.add(product)
            db.session.flush()
            db.session.add(
                StockMovement(
                    product_id=product.id,
                    user_id=users["admin"].id,
                    type=MovementType.IN,
                    quantity=initial,
                    stock_after=initial,
                    note="Carga inicial",
                )
            )
        db.session.commit()

        print("Datos de ejemplo cargados.")
        for username, _, password, role in USERS:
            print(f"  {role:8} {username} / {password}")


if __name__ == "__main__":
    run()
