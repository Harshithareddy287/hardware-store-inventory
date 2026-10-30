# Hardware Store Inventory 

## 1. Project Overview

I am building a hardware store inventory system using Python and SQLite.

The application will help a small hardware store manage products, suppliers, stock, and sales. Users will be able to add products, search for items, update stock, record sales, and generate reports.

I'll build the project step by step using Git branches, pull requests, and pytest tests.

## 2. Database Design

I'll use SQLite with five tables:

| Table | Purpose |
|---|---|
| `suppliers` | Stores supplier information |
| `products` | Stores product details, prices, and stock quantities |
| `sales` | Stores sales records |
| `sale_items` | Stores the products and quantities in each sale |
| `stock_movements` | Tracks stock changes |

Each table will have an integer primary key.

Products will have a unique SKU, name, category, supplier, unit price, quantity, and reorder level.

I will be using foreign keys to connect the tables and constraints to prevent invalid data, such as duplicate SKUs, negative prices, and negative stock quantities.

Prices will be stored as integer cents. For example, $15.99 will be stored as `1599`.

I'll use `STRICT` tables because my SQLite version supports them.

The schema will use `IF NOT EXISTS` so running it again won't remove existing data.

I'll also add indexes for product and sales lookups.

## 3. Sample Data

I'll create `seed_db.py` to add sample records.

The sample database will contain:

- 4 suppliers
- 12 products
- 5 sales
- 12 sale items
- 0 stock movements initially

Products will belong to categories such as Hand Tools, Power Tools, Fasteners, and Electrical.

At least two products will have low stock, and at least two products will have no sales.

I'll use SQL placeholders and `executemany()` to insert the data.

The seed script will be safe to run multiple times without creating duplicate records. I'll use a unique `seed_key` for sample sales.

## 4. Main Features

### Product Management

Users will be able to add products, view product details, update prices, and delete products.

The application will check for duplicate SKUs, invalid prices, missing suppliers, and other incorrect inputs.

Products that have already been sold cannot be deleted because their sales history must be preserved.

### Product Search

Users can search products by name, SKU, or supplier.Also add filters for category, maximum price, available stock, and low stock.

Searches will use SQL placeholders to prevent SQL injection.

### Reports

Creating four reports:

1. Stock value by supplier
2. Low-stock products
3. Sales by product
4. Products that have never been sold

The reports will use SQL joins and calculations to get results from the database.

### Stock Management

Users will be able to restock products and make stock adjustments.

Every stock change will update the product quantity and create a record in `stock_movements`.

The application will not allow stock quantities to become negative.

### Sales

Users will be able to record sales containing multiple products.

When a sale is recorded, the application will:

1. Check the products and available stock.
2. Create a sales record.
3. Save the sale items and their prices.
4. Reduce product quantities.
5. Record the stock movements.

I will use SQLite transactions to make sure all these steps happen together.

If any part of the sale fails, the transaction will roll back, and the database will remain unchanged.

## 5. Python Files and Functions

I'll organize the project into separate files.

| File | Purpose |
|---|---|
| `schema.sql` | Creates database tables and indexes |
| `inventory_db.py` | Database connection and inventory functions |
| `seed_db.py` | Loads sample data |
| `main.py` | Command-line menu |
| `tests/` | Pytest tests |
| `Dockerfile` | Runs the application in Docker |

The main functions will include:

- `connect()` and `initialize_database()`
- `seed_database()`
- `add_product()`, `get_product()`, `change_price()`, `delete_product()`
- `search_products()`
- `stock_value_by_supplier()`, `low_stock_report()`
- `sales_by_product()`, `never_sold_report()`
- `restock_product()`, `adjust_stock()`, `record_sale()`
- `backup_database()`

Database functions will accept a connection so they can be tested using an in-memory database.

## 6. Testing Plan

I'll use pytest to test the main features of the inventory management system.

The tests will cover:

- Database tables and constraints
- Sample data and duplicate prevention
- Product management and search
- Inventory reports
- Stock updates and adjustments
- Sales transactions and rollback
- Database backup and restore

I'll test both successful operations and invalid inputs to make sure the application works correctly.

Each database test will use a fresh in-memory SQLite database so the tests don't affect the actual inventory data.

I'll use `pytest.mark.parametrize` when I need to test multiple inputs for the same function.

Before opening a pull request, I'll run:

```bash
python -m pytest -v
python -m ruff check .
```

I'll add tests as I develop each feature and make sure the project meets the assignment's testing requirements.

## 7. Git and GitHub Plan

I'll complete the project using six pull requests.

| PR | Branch | Work |
|---|---|---|
| 1 | `feature/database-and-seed` | Database schema, seed data, tests, and initial CI |
| 2 | `feature/products-and-search` | Product operations and search |
| 3 | `feature/reports` | Four inventory reports |
| 4 | `feature/stock-and-sales` | Stock updates and sales transactions |
| 5 | `feature/menu-and-container` | CLI menu, backup, Docker, and version 1.0.0 |
| 6 | `feature/low-stock-banner` | Low-stock banner and version 1.1.0 |

For each PR, I'll:

1. Create a feature branch.
2. Write tests and implement the feature.
3. Run pytest and Ruff.
4. Commit and push the changes.
5. Open a pull request with a short description.
6. Merge after CI passes and delete the branch.

GitHub Actions will automatically run the tests and Ruff checks.

I'll also add a Docker build job when I implement the container.

## 8. Docker and Releases

I'll create a Dockerfile using a pinned Python version.

The application will use the `INVENTORY_DB` environment variable to choose the database location.

I'll use a Docker volume so the database is saved even when a container is removed.

The project will have two releases:

**Version 1.0.0**
- Complete inventory system
- Product management
- Search and reports
- Stock updates and sales
- CLI menu and backup

**Version 1.1.0**
- Adds a low-stock message when the application starts

I'll create Git tags and Docker images for both versions.

I'll also test upgrading to version 1.1.0 and rolling back to version 1.0.0 using the same database volume.

## 9. Backup and Documentation

I'll use SQLite's backup feature to create database backups.

I'll verify backups using `PRAGMA integrity_check` and compare table counts.

The README will include:

- Project overview
- Setup instructions
- How to run the application
- Sample database details
- Testing commands
- Docker instructions
- Example report outputs
- Backup and restore steps
- Release and rollback instructions

I'll also include a short self-review explaining what worked well and what I could improve.

## 10. Final Goal

By the end of the project, I want to have a working inventory management system that can safely store products, manage stock, record sales, and generate useful reports.