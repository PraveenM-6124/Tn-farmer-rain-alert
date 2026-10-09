"""Tests for agricultural marketplace produce listings and buyer enquiries."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.core.security import encrypt_phone, hash_phone
from backend.app.models.farmer import Farmer
from backend.app.models.product import Product


def test_list_products_empty(client: TestClient) -> None:
    """Verify listing products returns 200 array."""
    res = client.get("/api/v1/products")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_marketplace_page_renders(client: TestClient) -> None:
    """Verify /marketplace HTML page loads with produce catalog."""
    res = client.get("/marketplace")
    assert res.status_code == 200
    assert "🛒" in res.text or "Produce" in res.text or "Marketplace" in res.text


def test_create_and_enquire_product(client: TestClient, db_session: Session) -> None:
    """Verify produce creation and buyer enquiry workflow."""
    phone = "+919876599999"
    farmer = Farmer(
        name="Test Farmer",
        phone_hash=hash_phone(phone),
        phone_encrypted=encrypt_phone(phone),
        language="ta",
        district="Ranipet",
        is_active=True,
    )
    db_session.add(farmer)
    db_session.flush()

    product = Product(
        farmer_id=farmer.id,
        name_en="Organic Ponni Rice",
        name_ta="பொன்னி அரிசி",
        category="grains",
        quantity=50.0,
        unit="quintal",
        price_inr=2500.0,
        district="Ranipet",
        is_active=True,
    )
    db_session.add(product)
    db_session.commit()

    # Query products
    res = client.get("/api/v1/products?category=grains")
    assert res.status_code == 200
    prods = res.json()
    assert len(prods) >= 1
    assert prods[0]["name_en"] == "Organic Ponni Rice"

    # Enquire product
    enquiry_res = client.post(
        f"/api/v1/products/{product.id}/enquire",
        json={
            "buyer_name": "Kannan Buyer",
            "buyer_phone": "+919840123456",
            "message": "Looking to buy 20 bags for Chennai depot.",
        },
    )
    assert enquiry_res.status_code == 200
    assert enquiry_res.json()["success"] is True
