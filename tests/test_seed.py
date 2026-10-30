from seed_db import seed_database


# Test 1: Check sample data counts
def test_seed_data(db):
    seed_database(db)

    assert db.execute("SELECT COUNT(*) FROM suppliers").fetchone()[0] == 4
    assert db.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 12
    assert db.execute("SELECT COUNT(*) FROM sales").fetchone()[0] == 5
    assert db.execute("SELECT COUNT(*) FROM sale_items").fetchone()[0] == 12
    assert db.execute("SELECT COUNT(*) FROM stock_movements").fetchone()[0] == 0

    # Check product categories
    categories = db.execute(
        "SELECT COUNT(DISTINCT category) FROM products"
    ).fetchone()[0]

    assert categories >= 3


# Test 2: Running seed twice should not create duplicates
def test_seed_twice(db):
    seed_database(db)
    seed_database(db)

    assert db.execute("SELECT COUNT(*) FROM suppliers").fetchone()[0] == 4
    assert db.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 12
    assert db.execute("SELECT COUNT(*) FROM sales").fetchone()[0] == 5
    assert db.execute("SELECT COUNT(*) FROM sale_items").fetchone()[0] == 12


# Test 3: Check low-stock products
def test_low_stock_products(db):
    seed_database(db)

    low_stock = db.execute(
        """
        SELECT COUNT(*)
        FROM products
        WHERE quantity <= reorder_level
        """
    ).fetchone()[0]

    assert low_stock >= 2


# Test 4: Check products that were never sold
def test_never_sold_products(db):
    seed_database(db)

    never_sold = db.execute(
        """
        SELECT COUNT(*)
        FROM products
        WHERE id NOT IN (
            SELECT product_id FROM sale_items
        )
        """
    ).fetchone()[0]

    assert never_sold >= 2