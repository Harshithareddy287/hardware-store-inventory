import os
import sqlite3

from inventory_db import (
    add_product,
    connect,
    get_product_by_sku,
    initialize_database,
    low_stock_report,
    never_sold_report,
    record_sale,
    restock_product,
    sales_by_product_report,
    search_products,
    stock_value_by_supplier,
)


# Show menu options
def show_menu():
    print("\n===== HARDWARE STORE INVENTORY =====")
    print("1. Search products")
    print("2. Look up product by SKU")
    print("3. Add product")
    print("4. Restock product")
    print("5. Record sale")
    print("6. View reports")
    print("7. Backup database")
    print("0. Exit")

# Search products by name, SKU, or supplier
def search_menu(connection):
    text = input("Enter product name, SKU, or supplier: ")

    products = search_products(connection, text=text)

    if not products:
        print("No products found")
    else:
        for product in products:
            print(product["sku"], "-", product["name"])


# Look up a product using its SKU
def lookup_menu(connection):
    sku = input("Enter product SKU: ")

    product = get_product_by_sku(connection, sku)

    if product is None:
        print("Product not found")
    else:
        print("SKU:", product["sku"])
        print("Name:", product["name"])
        print("Price:", f"${product['unit_price'] / 100:.2f}")
        print("Quantity:", product["quantity"])
        print("Supplier:", product["supplier_name"])

# Add a new product
def add_product_menu(connection):
    sku = input("Enter SKU: ")
    name = input("Enter product name: ")
    category = input("Enter category: ")
    supplier_id = int(input("Enter supplier ID: "))
    price = round(float(input("Enter price in dollars: ")) * 100)
    quantity = int(input("Enter quantity: "))
    reorder_level = int(input("Enter reorder level: "))

    add_product(
        connection,
        sku,
        name,
        category,
        supplier_id,
        price,
        quantity,
        reorder_level,
    )

    print("Product added successfully!")


# Restock an existing product
def restock_menu(connection):
    sku = input("Enter product SKU: ")
    quantity = int(input("Enter quantity to add: "))

    restock_product(connection, sku, quantity)

    print("Product restocked successfully!")



# Record a sale
def record_sale_menu(connection):
    items = []

    try:
        count = int(input("How many different products? "))

        for _ in range(count):
            sku = input("Enter product SKU: ").strip()
            quantity = int(input("Enter quantity: "))
            items.append((sku, quantity))

        sale_id = record_sale(connection, items)

        print("Sale recorded successfully!")
        print("Sale ID:", sale_id)

    except ValueError as error:
        print("Error:", error)

# Display inventory reports
def reports_menu(connection):
    print("\n===== REPORTS =====")
    print("1. Stock value by supplier")
    print("2. Low stock products")
    print("3. Sales by product")
    print("4. Never sold products")

    choice = input("Enter your choice: ")

    if choice == "1":
        for row in stock_value_by_supplier(connection):
            print(dict(row))

    elif choice == "2":
        for row in low_stock_report(connection):
            print(dict(row))

    elif choice == "3":
        for row in sales_by_product_report(connection):
            print(dict(row))

    elif choice == "4":
        for row in never_sold_report(connection):
            print(dict(row))

    else:
        print("Invalid report option")

# Backup the inventory database
def backup_menu(connection):
    filename = input("Enter backup filename: ")

    if not filename:
        print("Filename cannot be empty.")
        return

    database_path = os.environ.get("INVENTORY_DB", "inventory.db")
    backup_path = os.path.join(os.path.dirname(database_path), filename)

    if os.path.abspath(backup_path) == os.path.abspath(database_path):
        print("Cannot overwrite the main database.")
        return

    with sqlite3.connect(backup_path) as backup:
        connection.backup(backup)
        result = backup.execute("PRAGMA integrity_check").fetchone()[0]

    print("Backup integrity check:", result)

#Menu options
def main():
    connection = connect()
    initialize_database(connection)

    while True:
        show_menu()
        choice = input("Enter your choice: ")

        if choice == "0":
            print("Goodbye!")
            break

        try:
            if choice == "1":
                search_menu(connection)
            elif choice == "2":
                lookup_menu(connection)
            elif choice == "3":
                add_product_menu(connection)
            elif choice == "4":
                restock_menu(connection)
            elif choice == "5":
                record_sale_menu(connection)
            elif choice == "6":
                reports_menu(connection)
            elif choice == "7":
                backup_menu(connection)
            else:
                print("Invalid option")

        except (ValueError, TypeError) as error:
            print("Error:", error)

    connection.close()


if __name__ == "__main__":
    main()