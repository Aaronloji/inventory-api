def test_entrada_suma_stock(client, auth):
    res = client.post(
        "/api/movements",
        json={"product_id": 1, "type": "in", "quantity": 5, "note": "Compra"},
        headers=auth("manager"),
    )
    assert res.status_code == 201
    assert res.get_json()["stock_after"] == 15


def test_salida_resta_stock(client, auth):
    res = client.post(
        "/api/movements",
        json={"product_id": 1, "type": "out", "quantity": 4},
        headers=auth("manager"),
    )
    assert res.get_json()["stock_after"] == 6


def test_salida_mayor_al_stock_falla(client, auth):
    res = client.post(
        "/api/movements",
        json={"product_id": 1, "type": "out", "quantity": 999},
        headers=auth("manager"),
    )
    assert res.status_code == 409


def test_ajuste_fija_el_stock(client, auth):
    res = client.post(
        "/api/movements",
        json={"product_id": 1, "type": "adjust", "quantity": 2},
        headers=auth("admin"),
    )
    assert res.get_json()["stock_after"] == 2


def test_low_stock_detecta_bajo_minimo(client, auth):
    client.post(
        "/api/movements",
        json={"product_id": 1, "type": "adjust", "quantity": 1},
        headers=auth("admin"),
    )
    res = client.get("/api/products/low-stock", headers=auth("viewer"))
    assert len(res.get_json()) == 1


def test_viewer_no_registra_movimientos(client, auth):
    res = client.post(
        "/api/movements",
        json={"product_id": 1, "type": "in", "quantity": 1},
        headers=auth("viewer"),
    )
    assert res.status_code == 403


def test_stats(client, auth):
    res = client.get("/api/stats", headers=auth("viewer"))
    assert res.status_code == 200
    assert res.get_json()["total_products"] == 1
