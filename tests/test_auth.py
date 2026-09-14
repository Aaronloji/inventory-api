def test_login_ok(client):
    res = client.post("/api/auth/login", json={"username": "admin", "password": "password123"})
    assert res.status_code == 200
    assert "access_token" in res.get_json()


def test_login_credenciales_malas(client):
    res = client.post("/api/auth/login", json={"username": "admin", "password": "mala"})
    assert res.status_code == 401


def test_endpoint_protegido_sin_token(client):
    assert client.get("/api/products").status_code == 401


def test_me_devuelve_el_usuario(client, auth):
    res = client.get("/api/auth/me", headers=auth("viewer"))
    assert res.status_code == 200
    assert res.get_json()["role"] == "viewer"


def test_solo_admin_registra_usuarios(client, auth):
    payload = {
        "username": "nuevo",
        "email": "nuevo@test.com",
        "password": "password123",
        "role": "viewer",
    }
    assert client.post("/api/auth/register", json=payload, headers=auth("manager")).status_code == 403
    assert client.post("/api/auth/register", json=payload, headers=auth("admin")).status_code == 201
