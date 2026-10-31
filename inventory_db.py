import os
import sqlite3
from pathlib import Path


def connect(db_path=None):
    if db_path is None:
        db_path = os.environ.get(
            "INVENTORY_DB",
            Path(__file__).parent / "inventory.db"
        )

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database(connection):
    schema_path = Path(__file__).parent / "schema.sql"

    with open(schema_path, "r", encoding="utf-8") as file:
        schema = file.read()

    connection.executescript(schema)

# Adding a new product, checking details, and returns the product ID.

def add_product(connection, sku, name, category, supplier_id, price, quantity, reorder_level):
    if not sku.strip() or not name.strip() or not category.strip():
        raise ValueError("Product fields cannot be empty")

    if price < 0 or quantity < 0 or reorder_level < 0:
        raise ValueError("Price and quantities cannot be negative")

    if not connection.execute(
        "SELECT id FROM suppliers WHERE id = ?", (supplier_id,)).fetchone():
        raise ValueError("Supplier not found")

    with connection:
        cursor = connection.execute(
            """INSERT INTO products
            (sku, name, category, supplier_id, unit_price, quantity, reorder_level)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (sku, name, category, supplier_id, price, quantity, reorder_level))
    return cursor.lastrowid

# Find a product by its SKU and get its supplier name
def get_product_by_sku(connection, sku):

    # Join products and suppliers to get the product details
    product = connection.execute( """
        SELECT products.*, suppliers.name AS supplier_name
        FROM products
        JOIN suppliers ON products.supplier_id = suppliers.id
        WHERE products.sku = ?
        """,(sku,)).fetchone()

    # Return the product if found, otherwise return None
    return product

# Update the price of an existing product
def update_product_price(connection, sku, new_price):
    # Check if the new price is negative
    if new_price < 0:
        raise ValueError("Price cannot be negative")

    # Update the product price using its SKU
    with connection:
        cursor = connection.execute(
            "UPDATE products SET unit_price = ? WHERE sku = ?",
            (new_price, sku)
        )
    # Return True if updated, otherwise False
    return cursor.rowcount > 0


# Delete a product only if it has never been sold
def delete_product(connection, sku):

    # Find the product ID using its SKU
    product = connection.execute(
        "SELECT id FROM products WHERE sku = ?", (sku,)
    ).fetchone()

    if product is None:
        raise ValueError("Product not found")
    # Check if the product has any sales history
    sold = connection.execute(
        "SELECT 1 FROM sale_items WHERE product_id = ?", (product["id"],)
    ).fetchone()

    if sold:
        raise ValueError("Cannot delete a product with sales history")

    # Delete the product
    with connection:
        connection.execute(
            "DELETE FROM products WHERE id = ?", (product["id"],)
        )


# Search products using text and optional filters
def search_products(connection, text="", category=None, max_price=None,
                    in_stock=False, low_stock=False):

    query = """
        SELECT products.*, suppliers.name AS supplier_name
        FROM products
        JOIN suppliers ON products.supplier_id = suppliers.id
        WHERE 1=1
    """
    values = []

    # Searching by name, SKU, or supplier name
    if text:
        query += """ AND (
            products.name LIKE ? OR
            products.sku LIKE ? OR
            suppliers.name LIKE ?
        )"""
        values.extend([f"%{text}%"] * 3)

    # Filtering by category
    if category:
        query += " AND products.category = ?"
        values.append(category)

    # Filtering by maximum price
    if max_price is not None:
        query += " AND products.unit_price <= ?"
        values.append(max_price)

    # Showing products available in stock
    if in_stock:
        query += " AND products.quantity > 0"

    # Showing products at or below reorder level
    if low_stock:
        query += " AND products.quantity <= products.reorder_level"

    # Sort products alphabetically
    query += " ORDER BY products.name"

    return connection.execute(query, values).fetchall()