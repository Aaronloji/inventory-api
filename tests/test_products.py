NUEVO = {
    "sku": "SKU-2",
    "name": "Producto nuevo",
    "unit_price": "2500.00",
    "min_stock": 3,
    "category_id": 1,
}


def test_listar_productos_pagina(client, auth):
    res = client.get("/api/products", headers=auth("viewer"))
    assert res.status_code == 200
    data = res.get_json()
    assert data["total"] == 1
    assert data["items"][0]["sku"] == "SKU-1"


def test_viewer_no_puede_crear(client, auth):
    assert client.post("/api/products", json=NUEVO, headers=auth("viewer")).status_code == 403


def test_manager_crea_producto_con_stock_cero(client, auth):
    res = client.post("/api/products", json=NUEVO, headers=auth("manager"))
    assert res.status_code == 201
    assert res.get_json()["stock"] == 0


def test_sku_duplicado_da_409(client, auth):
    duplicado = {**NUEVO, "sku": "SKU-1"}
    assert client.post("/api/products", json=duplicado, headers=auth("admin")).status_code == 409


def test_busqueda_por_nombre(client, auth):
    res = client.get("/api/products?q=base", headers=auth("viewer"))
    assert res.get_json()["total"] == 1
    res = client.get("/api/products?q=inexistente", headers=auth("viewer"))
    assert res.get_json()["total"] == 0


def test_solo_admin_elimina(client, auth):
    assert client.delete("/api/products/1", headers=auth("manager")).status_code == 403
    assert client.delete("/api/products/1", headers=auth("admin")).status_code == 204
