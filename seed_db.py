from contextlib import closing

from inventory_db import connect, initialize_database


def seed_database(connection):
    # Supplier data
    suppliers = [
        ("ABC Tools", "abc@example.com"),
        ("BuildMart Supplies", "build@example.com"),
        ("Power Equipment Co", "power@example.com"),
        ("Hardware World", "hardware@example.com"),
    ]

    # Product data (prices are in cents)
    products = [
        ("HAM001", "Hammer", "Hand Tools", "ABC Tools", 1599, 20, 5),
        ("SCR001", "Screwdriver", "Hand Tools", "ABC Tools", 899, 15, 5),
        ("WRN001", "Wrench", "Hand Tools", "ABC Tools", 1299, 12, 4),
        ("DRL001", "Drill", "Power Tools", "Power Equipment Co", 4999, 3, 5),
        ("SAW001", "Circular Saw", "Power Tools", "Power Equipment Co", 7999, 8, 3),
        ("SND001", "Sander", "Power Tools", "Power Equipment Co", 4599, 6, 3),
        ("SCS001", "Screws", "Fasteners", "BuildMart Supplies", 499, 5, 5),
        ("NAL001", "Nails", "Fasteners", "BuildMart Supplies", 399, 30, 10),
        ("BLT001", "Bolts", "Fasteners", "BuildMart Supplies", 699, 25, 8),
        ("EXT001", "Extension Cord", "Electrical", "Hardware World", 1999, 10, 4),
        ("WIR001", "Electrical Wire", "Electrical", "Hardware World", 2499, 14, 5),
        ("OUT001", "Power Outlet", "Electrical", "Hardware World", 1099, 18, 6),
    ]

    # Sample sales
    sales = [
        ("sample-sale-1", "2026-10-20 10:00:00"),
        ("sample-sale-2", "2026-10-21 11:30:00"),
        ("sample-sale-3", "2026-10-22 14:15:00"),
        ("sample-sale-4", "2026-10-23 09:45:00"),
        ("sample-sale-5", "2026-10-24 16:20:00"),
    ]

    # Items included in each sale
    sale_items = [
        ("sample-sale-1", "HAM001", 2, 1599),
        ("sample-sale-1", "SCR001", 1, 899),
        ("sample-sale-1", "SCS001", 3, 499),
        ("sample-sale-2", "WRN001", 1, 1299),
        ("sample-sale-2", "DRL001", 1, 4999),
        ("sample-sale-3", "SAW001", 1, 7999),
        ("sample-sale-3", "NAL001", 5, 399),
        ("sample-sale-3", "BLT001", 2, 699),
        ("sample-sale-4", "HAM001", 1, 1599),
        ("sample-sale-4", "EXT001", 1, 1999),
        ("sample-sale-5", "SCR001", 2, 899),
        ("sample-sale-5", "SCS001", 4, 499),
    ]

    # Insert sample data in one transaction
    with connection:

        # Add suppliers
        connection.executemany(
            """
            INSERT OR IGNORE INTO suppliers (name, contact_email)
            VALUES (?, ?)
            """,
            suppliers,
        )

        # Get supplier IDs
        supplier_ids = {
            row["name"]: row["id"]
            for row in connection.execute(
                "SELECT id, name FROM suppliers"
            )
        }

        # Match products with their suppliers
        product_rows = [
            (
                sku,
                name,
                category,
                supplier_ids[supplier_name],
                price,
                quantity,
                reorder_level,
            )
            for (
                sku,
                name,
                category,
                supplier_name,
                price,
                quantity,
                reorder_level,
            ) in products
        ]

        # Adding products
        connection.executemany(
            """
            INSERT OR IGNORE INTO products
            (sku, name, category, supplier_id,
             unit_price, quantity, reorder_level)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            product_rows,
        )

        # Geting product IDs
        product_ids = {
            row["sku"]: row["id"]
            for row in connection.execute(
                "SELECT id, sku FROM products"
            )
        }

        # Adding sales
        connection.executemany(
            """
            INSERT OR IGNORE INTO sales (seed_key, sale_date)
            VALUES (?, ?)
            """,
            sales,
        )

        # Getting sale IDs
        sale_ids = {
            row["seed_key"]: row["id"]
            for row in connection.execute(
                """
                SELECT id, seed_key
                FROM sales
                WHERE seed_key IS NOT NULL
                """
            )
        }

        # Matching sale items with sales and products
        sale_item_rows = [
            (
                sale_ids[seed_key],
                product_ids[sku],
                quantity,
                price,
            )
            for seed_key, sku, quantity, price in sale_items
        ]

        # Add sale items
        connection.executemany(
            """
            INSERT OR IGNORE INTO sale_items
            (sale_id, product_id, quantity, unit_price)
            VALUES (?, ?, ?, ?)
            """,
            sale_item_rows,
        )


def print_counts(connection):
    # Check the number of records in each table
    tables = [
        "suppliers",
        "products",
        "sales",
        "sale_items",
        "stock_movements",
    ]

    print("Database seeded successfully.\n")

    for table in tables:
        count = connection.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]

        print(f"{table}: {count}")


def main():
    # Connect to the database and load sample data
    with closing(connect()) as connection:
        initialize_database(connection)
        seed_database(connection)
        print_counts(connection)


if __name__ == "__main__":
    main()