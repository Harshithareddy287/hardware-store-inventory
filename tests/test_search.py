import pytest

from inventory_db import search_products


# Createing sample products for testing
@pytest.fixture
def search_db(db):
    db.execute(
        "INSERT INTO suppliers (name) VALUES (?)",
        ("ABC Tools",))

    db.executemany(
        """INSERT INTO products
        (sku, name, category, supplier_id, unit_price, quantity, reorder_level)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        [
            ("HAM001", "Hammer", "Tools", 1, 1500, 10, 5),
            ("DRL001", "Drill", "Power Tools", 1, 5000, 2, 5),
            ("SAW001", "Saw", "Tools", 1, 2000, 0, 3),
        ]
    )

    return db

# Check searching by name, SKU, and supplier ignoring case
@pytest.mark.parametrize("text, expected", [
    ("hammer", 1),
    ("drl001", 1),
    ("abc tools", 3),
])
def test_search_text(search_db, text, expected):
    results = search_products(search_db, text=text)

    assert len(results) == expected


# Checking category filter
def test_category_filter(search_db):
    results = search_products(search_db, category="Tools")

    assert len(results) == 2


# Checking maximum price filter
def test_max_price_filter(search_db):
    results = search_products(search_db, max_price=2000)

    assert len(results) == 2


# Checking in-stock filter
def test_in_stock_filter(search_db):
    results = search_products(search_db, in_stock=True)

    assert len(results) == 2


# Checking low-stock filter
def test_low_stock_filter(search_db):
    results = search_products(search_db, low_stock=True)

    assert len(results) == 2


# Checking combining filters and sorting by name
def test_combined_filters(search_db):
    results = search_products(
        search_db,
        category="Tools",
        max_price=2000,
        in_stock=True
    )

    assert len(results) == 1
    assert results[0]["name"] == "Hammer"

    # Check alphabetical sorting
    all_results = search_products(search_db)
    assert [product["name"] for product in all_results] == [
        "Drill", "Hammer", "Saw"
    ]


# Checking SQL injection does not damage the database
def test_sql_injection(search_db):
    results = search_products(
        search_db,
        text="'; DROP TABLE products; --"
    )

    assert results == []

    count = search_db.execute(
        "SELECT COUNT(*) FROM products"
    ).fetchone()[0]

    assert count == 3