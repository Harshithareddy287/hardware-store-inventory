import sqlite3

import pytest

from inventory_db import initialize_database


# Test 1: Check all five tables exist
def test_tables_created(db):
    tables = db.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'"
    ).fetchall()

    names = [row["name"] for row in tables]

    assert "suppliers" in names
    assert "products" in names
    assert "sales" in names
    assert "sale_items" in names
    assert "stock_movements" in names


# Test 2: Running schema again should not delete data
def test_schema_runs_twice(db):
    db.execute(
        "INSERT INTO suppliers (name) VALUES (?)",
        ("Test Supplier",),
    )

    initialize_database(db)

    count = db.execute(
        "SELECT COUNT(*) FROM suppliers"
    ).fetchone()[0]

    assert count == 1


# Test 3: Check foreign keys
def test_foreign_keys(db):
    assert db.execute("PRAGMA foreign_keys").fetchone()[0] == 1

    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            """
            INSERT INTO products
            (sku, name, category, supplier_id, unit_price, quantity, reorder_level)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            ("TEST001", "Hammer", "Tools", 999, 1000, 5, 2),
        )


# Test 4: Check negative price
def test_negative_price(db):
    db.execute("INSERT INTO suppliers (name) VALUES ('Test Supplier')")

    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            """
            INSERT INTO products
            (sku, name, category, supplier_id, unit_price, quantity, reorder_level)
            VALUES ('TEST001', 'Hammer', 'Tools', 1, -100, 5, 2)
            """
        )


# Test 5: Check negative quantity
def test_negative_quantity(db):
    db.execute("INSERT INTO suppliers (name) VALUES ('Test Supplier')")

    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            """
            INSERT INTO products
            (sku, name, category, supplier_id, unit_price, quantity, reorder_level)
            VALUES ('TEST001', 'Hammer', 'Tools', 1, 1000, -5, 2)
            """
        )


# Test 6: Check missing product name
def test_missing_name(db):
    db.execute("INSERT INTO suppliers (name) VALUES ('Test Supplier')")

    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            """
            INSERT INTO products
            (sku, name, category, supplier_id, unit_price, quantity, reorder_level)
            VALUES ('TEST001', NULL, 'Tools', 1, 1000, 5, 2)
            """
        )


# Test 7: Check duplicate SKU
def test_duplicate_sku(db):
    db.execute("INSERT INTO suppliers (name) VALUES ('Test Supplier')")

    sql = """
        INSERT INTO products
        (sku, name, category, supplier_id, unit_price, quantity, reorder_level)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    product = ("TEST001", "Hammer", "Tools", 1, 1000, 5, 2)

    db.execute(sql, product)

    with pytest.raises(sqlite3.IntegrityError):
        db.execute(sql, product)


# Test 8: Check STRICT data types
def test_strict_table(db):
    db.execute("INSERT INTO suppliers (name) VALUES ('Test Supplier')")

    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            """
            INSERT INTO products
            (sku, name, category, supplier_id, unit_price, quantity, reorder_level)
            VALUES ('TEST001', 'Hammer', 'Tools', 1, 'hello', 5, 2)
            """
        )


# Test 9: Check invalid stock movement reason
def test_invalid_movement_reason(db):
    db.execute("INSERT INTO suppliers (name) VALUES ('Test Supplier')")

    db.execute(
        """
        INSERT INTO products
        (sku, name, category, supplier_id, unit_price, quantity, reorder_level)
        VALUES ('TEST001', 'Hammer', 'Tools', 1, 1000, 5, 2)
        """
    )

    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            """
            INSERT INTO stock_movements
            (product_id, change, reason, created_at)
            VALUES (1, 5, 'invalid', '2026-10-28')
            """
        )