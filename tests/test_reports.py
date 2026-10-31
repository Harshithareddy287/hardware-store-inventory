from inventory_db import (
    low_stock_report,
    never_sold_report,
    sales_by_product_report,
    stock_value_by_supplier,
)


# Checking total stock value for each supplier
def test_stock_value_by_supplier(db):
    db.execute("INSERT INTO suppliers (name) VALUES (?)", ("ABC Tools",))
    db.execute(
        """INSERT INTO products
        (sku, name, category, supplier_id, unit_price, quantity, reorder_level)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        ("HAM001", "Hammer", "Tools", 1, 1500, 10, 5)
    )
    results = stock_value_by_supplier(db)

    assert results[0]["supplier_name"] == "ABC Tools"
    assert results[0]["total_value"] == 15000


# Checking products at or below their reorder level
def test_low_stock_report(db):
    db.execute("INSERT INTO suppliers (name) VALUES (?)", ("ABC Tools",))
    db.execute(
        """INSERT INTO products
        (sku, name, category, supplier_id, unit_price, quantity, reorder_level)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        ("HAM001", "Hammer", "Tools", 1, 1500, 2, 5)
    )

    results = low_stock_report(db)

    assert len(results) == 1
    assert results[0]["sku"] == "HAM001"
    assert results[0]["units_short"] == 3


# Checking units sold and revenue for a product
def test_sales_by_product_report(db):
    db.execute("INSERT INTO suppliers (name) VALUES (?)", ("ABC Tools",))

    db.execute(
        """INSERT INTO products
        (sku, name, category, supplier_id, unit_price, quantity, reorder_level)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        ("HAM001", "Hammer", "Tools", 1, 1500, 10, 5)
    )

    db.execute(
        "INSERT INTO sales (sale_date) VALUES (?)",
        ("2026-10-30",)
    )

    db.execute(
        """INSERT INTO sale_items
        (sale_id, product_id, quantity, unit_price)
        VALUES (?, ?, ?, ?)""",
        (1, 1, 2, 1500)
    )

    results = sales_by_product_report(db)

    assert results[0]["sku"] == "HAM001"
    assert results[0]["units_sold"] == 2
    assert results[0]["revenue"] == 3000


# Checking products that have never been sold
def test_never_sold_report(db):
    db.execute("INSERT INTO suppliers (name) VALUES (?)", ("ABC Tools",))

    db.execute(
        """INSERT INTO products
        (sku, name, category, supplier_id, unit_price, quantity, reorder_level)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        ("HAM001", "Hammer", "Tools", 1, 1500, 10, 5)
    )

    results = never_sold_report(db)

    assert len(results) == 1
    assert results[0]["sku"] == "HAM001"