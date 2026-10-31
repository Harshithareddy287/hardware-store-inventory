import pytest

from inventory_db import adjust_stock, record_sale, restock_product


def test_restock_product(db):
    # Add a supplier and product
    db.execute("INSERT INTO suppliers (name) VALUES ('ABC Tools')")
    db.execute("""
        INSERT INTO products
        (sku, name, category, supplier_id, unit_price, quantity, reorder_level)
        VALUES ('HAM001', 'Hammer', 'Tools', 1, 1500, 10, 5)""")
    db.commit()

    # Restock 5 units
    restock_product(db, "HAM001", 5)

    # Check updated quantity
    product = db.execute(
        "SELECT quantity FROM products WHERE sku = ?", ("HAM001",)).fetchone()
    assert product["quantity"] == 15

    # Check stock movement
    movement = db.execute(
        "SELECT change, reason FROM stock_movements").fetchone()
    assert movement["change"] == 5
    assert movement["reason"] == "restock"

# Test that stock decreases and the change is recorded
def test_adjust_stock(db):
    db.execute("INSERT INTO suppliers (name) VALUES ('ABC Tools')")
    db.execute("""
        INSERT INTO products
        (sku, name, category, supplier_id, unit_price, quantity, reorder_level)
        VALUES ('HAM001', 'Hammer', 'Tools', 1, 1500, 10, 5)
    """)
    db.commit()

    adjust_stock(db, "HAM001", -3)

    product = db.execute(
        "SELECT quantity FROM products WHERE sku = 'HAM001'"
    ).fetchone()

    movement = db.execute(
        "SELECT change, reason FROM stock_movements"
    ).fetchone()

    assert product["quantity"] == 7
    assert movement["change"] == -3
    assert movement["reason"] == "adjustment"


# Test that stock cannot become negative
def test_adjust_stock_negative(db):
    db.execute("INSERT INTO suppliers (name) VALUES ('ABC Tools')")
    db.execute("""
        INSERT INTO products
        (sku, name, category, supplier_id, unit_price, quantity, reorder_level)
        VALUES ('HAM001', 'Hammer', 'Tools', 1, 1500, 10, 5)
    """)
    db.commit()

    with pytest.raises(ValueError):
        adjust_stock(db, "HAM001", -15)

    product = db.execute(
        "SELECT quantity FROM products WHERE sku = 'HAM001'"
    ).fetchone()

    assert product["quantity"] == 10

# Add sample products for testing sales
def add_sample_products(db):
    db.execute("INSERT INTO suppliers (name) VALUES ('ABC Tools')")
    db.execute("""
        INSERT INTO products
        (sku, name, category, supplier_id, unit_price, quantity, reorder_level)
        VALUES
        ('HAM001', 'Hammer', 'Tools', 1, 1500, 10, 5),
        ('DRL001', 'Drill', 'Tools', 1, 5000, 3, 2)
    """)
    db.commit()


# Test that a sale saves details and updates stock
def test_record_sale(db):
    add_sample_products(db)

    sale_id = record_sale(db, [("HAM001", 2)], "2026-10-31")

    product = db.execute(
        "SELECT quantity FROM products WHERE sku = 'HAM001'"
    ).fetchone()

    item = db.execute(
        "SELECT quantity, unit_price FROM sale_items WHERE sale_id = ?",
        (sale_id,)
    ).fetchone()

    movement = db.execute(
        "SELECT change, reason FROM stock_movements"
    ).fetchone()

    assert product["quantity"] == 8
    assert item["quantity"] == 2
    assert item["unit_price"] == 1500
    assert movement["change"] == -2
    assert movement["reason"] == "sale"


# Test that insufficient stock cancels the entire sale
def test_sale_rollback(db):
    add_sample_products(db)

    with pytest.raises(ValueError):
        record_sale(db, [("HAM001", 2), ("DRL001", 10)])

    product = db.execute(
        "SELECT quantity FROM products WHERE sku = 'HAM001'"
    ).fetchone()

    assert product["quantity"] == 10

    # Check that no sale records were saved
    for table in ("sales", "sale_items", "stock_movements"):
        count = db.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]
        assert count == 0


# Test that unknown and duplicate products are rejected
@pytest.mark.parametrize("items", [
    [("HAM001", 2), ("XYZ001", 1)],
    [("HAM001", 2), ("HAM001", 1)],
])
def test_sale_invalid_products(db, items):
    add_sample_products(db)

    with pytest.raises(ValueError):
        record_sale(db, items)

    assert db.execute(
        "SELECT COUNT(*) FROM sales"
    ).fetchone()[0] == 0