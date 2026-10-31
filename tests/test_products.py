import sqlite3

import pytest

from inventory_db import (
    add_product,
    delete_product,
    get_product_by_sku,
    update_product_price,
)


# Check that a valid product is added successfully
def test_add_product(db):
    db.execute(
        "INSERT INTO suppliers (name) VALUES (?)",
        ("ABC Tools",)
    )

    product_id = add_product(
        db, "HAM002", "Claw Hammer", "Hand Tools",
        1, 1599, 20, 5
    )

    product = get_product_by_sku(db, "HAM002")

    assert product["id"] == product_id
    assert product["name"] == "Claw Hammer"
    assert product["supplier_name"] == "ABC Tools"


# Check that duplicate SKUs are not allowed
def test_duplicate_sku(db):
    db.execute(
        "INSERT INTO suppliers (name) VALUES (?)",
        ("ABC Tools",)
    )

    add_product(db, "HAM001", "Hammer", "Tools", 1, 1500, 10, 5)

    with pytest.raises(sqlite3.IntegrityError):
        add_product(db, "HAM001", "Another Hammer", "Tools", 1, 2000, 5, 2)


# Check that the supplier must exist
def test_unknown_supplier(db):
    with pytest.raises(ValueError, match="Supplier not found"):
        add_product(db, "HAM001", "Hammer", "Tools", 999, 1500, 10, 5)


# Check that negative prices and quantities are rejected
@pytest.mark.parametrize("price, quantity", [
    (-100, 10),
    (1500, -5),
])
def test_negative_product_values(db, price, quantity):
    db.execute(
        "INSERT INTO suppliers (name) VALUES (?)",
        ("ABC Tools",)
    )

    with pytest.raises(ValueError):
        add_product(
            db, "HAM001", "Hammer", "Tools",
            1, price, quantity, 5
        )


# Check that a product price can be updated
def test_update_product_price(db):
    db.execute(
        "INSERT INTO suppliers (name) VALUES (?)",
        ("ABC Tools",)
    )

    add_product(db, "HAM001", "Hammer", "Tools", 1, 1500, 10, 5)

    result = update_product_price(db, "HAM001", 2000)

    product = get_product_by_sku(db, "HAM001")

    assert result is True
    assert product["unit_price"] == 2000


# Check that updating a missing product returns False
def test_update_missing_product(db):
    assert update_product_price(db, "UNKNOWN", 2000) is False


# Check that a product without sales history can be deleted
def test_delete_unsold_product(db):
    db.execute(
        "INSERT INTO suppliers (name) VALUES (?)",
        ("ABC Tools",)
    )

    add_product(db, "HAM001", "Hammer", "Tools", 1, 1500, 10, 5)

    delete_product(db, "HAM001")

    assert get_product_by_sku(db, "HAM001") is None


# Check that a product with sales history cannot be deleted
def test_delete_sold_product(db):
    db.execute(
        "INSERT INTO suppliers (name) VALUES (?)",
        ("ABC Tools",))

    product_id = add_product(
        db, "HAM001", "Hammer", "Tools", 1, 1500, 10, 5)

    db.execute(
        "INSERT INTO sales (sale_date) VALUES (?)",
        ("2026-10-30",))

    sale_id = db.execute(
        "SELECT id FROM sales"
    ).fetchone()["id"]

    db.execute(
        """INSERT INTO sale_items
           (sale_id, product_id, quantity, unit_price)
           VALUES (?, ?, ?, ?)""",
        (sale_id, product_id, 1, 1500)
    )

    with pytest.raises(ValueError, match="sales history"):
        delete_product(db, "HAM001")

    assert get_product_by_sku(db, "HAM001") is not None