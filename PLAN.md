# Hardware Store Inventory Management System — Plan

## 1. Project Overview

I am building a command-line inventory management system for a small hardware store using Python and SQLite.

Right now,store uses spreadsheets to track products, stock quantities, prices, and sales. This can lead to incorrect stock counts, outdated prices, and difficulty tracking sales history. My application will make it easier to manage products, update stock, record sales, and generate reports.

One important part of this project is making sure that a failed sale doesn't leave the database with incorrect information.

## 2. Database Design

I'll create the database using `schema.sql`.

The database will have five tables:

| Table | Columns and constraints | Purpose |
|---|---|---|
| `suppliers` | `id` (INTEGER primary key), `name` (required, unique, nonblank), `contact_email` (optional TEXT) | Stores supplier information. |
| `products` | `id` (INTEGER primary key), `sku` (unique, required, nonblank), `name` and `category` (required, nonblank), `supplier_id` (required foreign key), `unit_price` (INTEGER >= 0), `quantity` (INTEGER >= 0), `reorder_level` (INTEGER >= 0) | Stores product details and current stock. |
| `sales` | `id` (INTEGER primary key), `sale_date` (required TEXT) | Records when a sale happened. |
| `sale_items` | `id` (INTEGER primary key), `sale_id` and `product_id` (required foreign keys), `quantity` (INTEGER > 0), `unit_price` (INTEGER >= 0), unique combination of `sale_id` and `product_id` | Stores products sold, quantities, and prices charged. |
| `stock_movements` | `id` (INTEGER primary key), `product_id` (required foreign key), `change` (nonzero signed INTEGER), `reason` (`restock`, `adjustment`, or `sale`), `created_at` (required TEXT) | Tracks changes to product stock. |

### Table Relationships

The tables will be connected using primary keys and foreign keys.

- One supplier can supply multiple products.
- One sale can contain multiple sale items.
- One product can appear in multiple sales.
- One product can have multiple stock movements.

The `sale_items` table connects sales and products.

I'll use a foreign key from `sale_items.product_id` to `products.id` without cascading deletes. This protects sales history even if someone tries to delete a sold product directly through SQL.

Foreign keys will be enabled for every connection using `PRAGMA foreign_keys = ON`.

### Database Rules

The database will enforce important rules using `NOT NULL`, `UNIQUE`, `CHECK`, and foreign key constraints.

For example, duplicate SKUs, negative prices, and negative stock quantities will not be allowed.

All money values will be stored as whole cents using `INTEGER`.

For example, a product priced at $24.99 will be stored as `2499`. When displayed in the menu or reports, it will appear as `$24.99`.

I will also add an index on `products.supplier_id` to help with supplier-related queries.

The schema will use `IF NOT EXISTS` so running it again won't delete existing data.

will check the SQLite version before implementation. If it supports SQLite 3.37 or newer, I I will use `STRICT` tables. Otherwise, I document it that limitation in the README.

## 3. Sample Data

will create `seed_db.py` to set up the database and insert sample records.

The initial data will contain:

| Table | Records |
|---|---:|
| Suppliers | 4 |
| Products | 12 |
| Sales | 5 |
| Sale items | 12 |
| Stock movements | 0 |

The products will belong to at least three categories, such as Tools, Electrical, and Plumbing.

At least two products will have no sales history, and at least two will have stock at or below their reorder level.

I'll use SQL placeholders and `executemany()` to insert the data.

The script will print the number of records in each table after seeding.

I'll make the seed script safe to run more than once, so it won't create duplicate sample records or delete existing inventory data.

## 4. Functions

I'll keep most of the database operations in `inventory_db.py`.

Each function will accept a database connection so I can use an in-memory database during testing.

I'll use one `connect()` function to open database connections, enable foreign keys, and set `sqlite3.Row` so query results are easier to work with. I'll also use `contextlib.closing` to close connections properly.

These are the functions I plan to implement:

| Function | Inputs | Returns |
|---|---|---|
| `connect()` | `db_path=None` | SQLite connection |
| `initialize_database()` | `connection` | None |
| `seed_database()` | `connection` | None |
| `add_product()` | `connection, sku, name, category, supplier_id, unit_price, quantity, reorder_level` | New product ID |
| `get_product()` | `connection, product_id` | Product row with supplier name, or None |
| `change_price()` | `connection, product_id, new_price` | True if updated, False if missing |
| `delete_product()` | `connection, product_id` | True if deleted, False if missing |
| `search_products()` | `connection, text="", category=None, max_price=None, in_stock_only=False, low_stock_only=False` | Matching product rows |
| `stock_value_by_supplier()` | `connection` | Supplier names and stock values |
| `low_stock_report()` | `connection` | Low-stock products and units short |
| `sales_by_product()` | `connection` | Products, units sold, and revenue |
| `never_sold_report()` | `connection` | Products without sales |
| `restock_product()` | `connection, product_id, amount, timestamp=None` | Updated stock quantity |
| `adjust_stock()` | `connection, product_id, change, timestamp=None` | Updated stock quantity |
| `record_sale()` | `connection, items, timestamp=None` | New sale ID |
| `backup_database()` | `connection, destination_path` | Backup file path |

### Product Management

The application will support adding products, looking them up, changing their prices, and deleting them.

I'll validate the inputs and handle problems such as duplicate SKUs, missing suppliers, negative values, and attempts to delete products that have already been sold.

The menu will show understandable error messages instead of crashing.

### Product Search

The search function will look for text in the product name, SKU, or supplier name without case sensitivity.

It will also support optional filters for category, maximum price, products in stock, and low-stock products.

The filters can be combined, and results will be sorted by product name.

I'll use `?` placeholders for all user-provided SQL values. I'll also test the input `'; DROP TABLE products; --` to make sure it doesn't execute as SQL.

## 5. Reports

I'll create four reports using SQL joins and aggregation.

**Stock value by supplier:** Shows the total value of inventory from each supplier, sorted from highest to lowest.

**Low-stock report:** Shows products where the current quantity is at or below the reorder level, including how many units are short.

**Sales by product:** Shows the total units sold and revenue for each product, sorted by highest revenue.

**Never-sold report:** Shows products that haven't appeared in any sale.

For sales reports, I'll use the prices saved in `sale_items` rather than the current product prices. This keeps historical sales totals accurate.

All money calculations will use integer cents, and the results will be displayed with two decimal places.

I'll include the expected report results from my sample data in the README.

## 6. Stock Changes and Transactions

Stock changes and sales need to be handled carefully because several database updates may happen during one operation.

I'll use transactions so that either all changes are saved or none are saved.

### Restock

The `restock_product()` function will:

1. Check that the product exists.
2. Make sure the amount is greater than zero.
3. Increase the product's stock.
4. Add a positive stock movement with reason `restock`.
5. Save both changes together.

If an operation fails, the stock update and movement record will be rolled back.

### Stock Adjustment

The `adjust_stock()` function will:

1. Check that the product exists.
2. Accept a positive or negative stock change.
3. Calculate the new stock quantity.
4. Reject the adjustment if it would make stock negative.
5. Update the stock and add an `adjustment` movement.
6. Save both changes together.

A rejected adjustment must leave the stock quantity and movement history unchanged. Zero changes will also be rejected.

### Record a Sale

The `record_sale()` function will accept a list of product and quantity pairs.

For example:

`[(1, 2), (3, 1)]`

This means two units of product 1 and one unit of product 3.

The function will:

1. Check that the sale contains valid product and quantity pairs.
2. Reject duplicate products in the same sale.
3. Create a sale record.
4. Look up each product and its current price.
5. Check whether enough stock is available.
6. Insert the sale item with the price charged.
7. Reduce the product's stock quantity.
8. Add a negative stock movement with reason `sale`.
9. Repeat for the remaining items.
10. Save the sale only when every item succeeds.

I'll use one `with connection:` block around the complete sale operation. If an error occurs, the transaction will roll back instead of committing the partial changes.

This means a failed sale must leave:

- No new sale record.
- No new sale items.
- No new stock movements.
- No changes to product quantities.

For example, if the first product has enough stock but the second doesn't, the first product's changes must also be undone.

I'll write a test for this situation and show the database state before and after the failed sale in the README.

The stock and sale functions will accept an optional timestamp. If no timestamp is provided, they'll use the current time. Tests will be able to provide a fixed timestamp.

## 7. Terminal Menu

I'll create the interactive menu in `main.py`.

It will include options to search products with filters, look up a product, add a product, restock, record a sale, view all four reports, back up the database, and exit.

The menu will call functions from `inventory_db.py` rather than repeating SQL queries.

I'll handle invalid input, such as entering letters when a number is expected. I'll also catch specific database errors and display friendly messages.

The goal is for the program to continue running after expected input errors.

## 8. Testing

Each database test will use a fresh in-memory SQLite database, created through a fixture in `conftest.py`.

I'll write at least 23 tests covering:

- Database constraints and foreign keys.
- Adding products and rejecting duplicate SKUs.
- Missing suppliers and invalid prices or quantities.
- Updating prices and handling missing products.
- Deleting never-sold products and protecting sold products.
- Search by product name, SKU, and supplier.
- Individual and combined search filters.
- SQL injection protection.
- All four reports.
- Successful and invalid restocks.
- Stock adjustments and negative-stock prevention.
- Successful sales and historical prices.
- Failed sales and complete rollback.
- Unknown products and duplicate sale items.
- Backup integrity and matching row counts.

I'll use parametrized tests where appropriate and pytest's `tmp_path` fixture for backup testing.

Before opening each pull request, I'll run:

```bash
python -m pytest -v
python -m ruff check .
```

I'll keep the code simple, use clear names, and avoid unnecessary repetition.

## 9. Git and GitHub Workflow

I'll complete and commit this `PLAN.md` before writing application code.

Only the initial setup files (`.gitignore`, `requirements.txt`, and `conftest.py`) and `PLAN.md` will be committed directly to `main`.

The remaining work will be completed through six feature branches.

| Order | Branch | Work |
|---|---|---|
| 1 | `feature/database-and-seed` | Database schema, seed script, and tests |
| 2 | `feature/products-and-search` | Product management, search, and tests |
| 3 | `feature/reports` | Four reports and tests |
| 4 | `feature/stock-and-sales` | Restock, adjustments, sales, and rollback tests |
| 5 | `feature/menu-and-container` | Terminal menu, backup, Docker, CI, and documentation |
| 6 | `feature/low-stock-banner` | Low-stock banner for version 1.1.0 |

For each branch, I'll write tests, implement the feature, run the checks, and commit the changes.

Commit messages will begin with a verb.

I'll create a pull request with a meaningful title and a short description explaining what changed and how it was tested.

I'll merge only after CI passes, delete the branch, and update my local `main` branch before starting the next feature.

## 10. Continuous Integration

I'll use GitHub Actions to run automated checks whenever a pull request is opened or `main` changes.

The workflow will install dependencies, run pytest, and run Ruff.

When Docker support is added, I'll include a `docker-build` job that builds the image and runs tests inside it.

The latest CI run on `main` must be green before submission.

## 11. Docker

I'll create a Dockerfile and `.dockerignore` to package the application.

The Dockerfile will use a pinned Python version and follow the layer ordering explained in the Containerization article.

The application will read the database path from `INVENTORY_DB`. If the variable isn't set, it will use a database file beside the code.

Inside Docker, I'll store the database at `/data/inventory.db` and use a named Docker volume to preserve it.

I'll run the program with `docker run -it`.

I'll also test that the data remains available when I remove one container and start another with the same volume.

## 12. Backup and Restore

I'll use SQLite's backup function to create a copy of the database.

After creating the backup, I'll check it using `PRAGMA integrity_check` and compare the row counts in all five tables.

I'll write a pytest test using `tmp_path` to verify the backup.

The README will explain how to back up and restore the database, with actual command output showing the results.

## 13. Release Plan

The project will have two versions.

### Version 1.0.0

The first release will include the main inventory management features:

- Database and sample data.
- Product management.
- Search and filters.
- Four reports.
- Stock changes and sales.
- Terminal menu.
- Database backup.
- Automated tests.
- Docker support.
- CI and documentation.

After the first five feature branches are merged and all checks pass, I'll create Git tag `v1.0.0` and Docker image `hardware-inventory:1.0.0`.

### Version 1.1.0

The second release will add a low-stock count banner when the menu starts.

For example:

`Low-stock alert: 3 products need attention.`

I'll develop this change on `feature/low-stock-banner`.

After testing and merging, I'll create Git tag `v1.1.0` and Docker image `hardware-inventory:1.1.0`.

I'll record both releases in `CHANGELOG.md`.

### Rollback

To demonstrate rollback, I'll start the application using version 1.0.0 and a named Docker volume.

Then I'll switch to version 1.1.0 using the same volume.

Finally, I'll switch back to version 1.0.0 and confirm that the database still contains the same products, stock quantities, and sales history.

Both versions will use a compatible database structure.

I'll include the actual commands and results in the README.

## 14. README and Final Review

The README will explain how to set up, run, test, and use the application.

It will include the database configuration, sample data counts, expected report results, Docker instructions, backup and restore steps, and release rollback instructions.

I'll include real terminal output for the Docker build, data persistence, failed sale, backup verification, and rollback demonstration.

I will also include self-review of about half a page explaining what I would improve if I rebuilt the project and one area I'd like a reviewer to check.

Before submission, I'll make sure:

- All required features work.
- At least 23 tests pass.
- Ruff reports no errors.
- All six pull requests are merged.
- Feature branches are deleted after merging.
- Both release tags are available on GitHub.
- Both Docker image versions work.
- The latest CI run on `main` is green.
- The README and CHANGELOG are complete.
- The repository remains public for grading.