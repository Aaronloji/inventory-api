import pytest

from app import create_app
from app.config import TestConfig
from app.extensions import db as _db
from app.models import Category, Product, Role, User


@pytest.fixture()
def app():
    app = create_app(TestConfig)
    with app.app_context():
        _db.create_all()
        _seed()
        yield app
        _db.session.remove()
        _db.drop_all()


def _seed():
    for username, role in [
        ("admin", Role.ADMIN),
        ("manager", Role.MANAGER),
        ("viewer", Role.VIEWER),
    ]:
        user = User(username=username, email=f"{username}@test.com", role=role)
        user.set_password("password123")
        _db.session.add(user)

    _db.session.add(Category(name="General", description="Categoría base"))
    _db.session.commit()

    _db.session.add(
        Product(sku="SKU-1", name="Producto base", category_id=1, unit_price=1000, min_stock=5, stock=10)
    )
    _db.session.commit()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def auth(client):
    def _login(username="admin"):
        res = client.post(
            "/api/auth/login", json={"username": username, "password": "password123"}
        )
        token = res.get_json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _login
