# Hardware Store Inventory Management System

This is a Python project for managing inventory in a hardware store. I used SQLite to store product details, suppliers, sales, and stock changes.

The application helps keep track of available products, update stock, record sales, and generate inventory reports.

## Features

- Add, view, update, and delete products
- Search products using different filters
- Restock products and record sales
- Track stock movements
- View stock value by supplier
- Find low-stock products
- View sales by product
- Find products that have never been sold
- Back up the database
- Run the application using Docker

## Database

I used SQLite with five tables:

- `suppliers`
- `products`
- `sales`
- `sale_items`
- `stock_movements`

Prices are stored as integer cents to avoid floating-point errors.

I also used foreign keys, constraints, and STRICT tables to keep the data valid.

### Sample Data

I created `seed_db.py` to add sample data.

I tested it using a separate database:

```bash
INVENTORY_DB=seed_test.db python seed_db.py
```

Actual output:

```text
Database seeded successfully.

suppliers: 4
products: 12
sales: 5
sale_items: 12
stock_movements: 0
```

The sample data includes two low-stock products and three products that have never been sold.

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Create the database:

```bash
python seed_db.py
```

Run the application:

```bash
python main.py
```

Run tests:

```bash
python -m pytest -q
```

Check the code:

```bash
python -m ruff check .
```

The application also supports the `INVENTORY_DB` environment variable to choose a database file.

For example:

```bash
INVENTORY_DB=inventory.db python main.py
```

## Menu

The application uses a terminal menu to manage products, stock, sales, reports, and backups.

In version 1.1.0, I added a low-stock warning that appears when the application starts.

Example:

```text
===== LOW STOCK WARNING: 2 PRODUCTS =====
Drill (DRL001): 3 remaining, reorder level 5
Screws (SCS001): 5 remaining, reorder level 5
```

## Reports

I created four reports using the sample data.

### Stock Value by Supplier

| Supplier | Stock Value |
|---|---:|
| Power Equipment Co | $1,065.83 |
| Hardware World | $747.58 |
| ABC Tools | $610.53 |
| BuildMart Supplies | $319.40 |

### Low-Stock Products

| SKU | Product | Units Short |
|---|---|---:|
| DRL001 | Drill | 2 |
| SCS001 | Screws | 0 |

### Sales by Product

| SKU | Units Sold | Revenue |
|---|---:|---:|
| SAW001 | 1 | $79.99 |
| DRL001 | 1 | $49.99 |
| HAM001 | 3 | $47.97 |
| SCS001 | 7 | $34.93 |
| SCR001 | 3 | $26.97 |
| EXT001 | 1 | $19.99 |
| NAL001 | 5 | $19.95 |
| BLT001 | 2 | $13.98 |
| WRN001 | 1 | $12.99 |
| SND001 | 0 | $0.00 |
| WIR001 | 0 | $0.00 |
| OUT001 | 0 | $0.00 |

Revenue is calculated using the price recorded at the time of sale.

### Never-Sold Products

| SKU | Product |
|---|---|
| WIR001 | Electrical Wire |
| OUT001 | Power Outlet |
| SND001 | Sander |

## Failed Sale Rollback

I used database transactions to make sure a failed sale does not change the inventory.

I tested a sale with 2 hammers and 10 drills.

Before the sale:

| Product | Quantity |
|---|---:|
| HAM001 | 10 |
| DRL001 | 3 |

The sale failed because there were not enough drills.

```text
Sale failed: Not enough stock
```

After the failed sale:

| Product | Quantity |
|---|---:|
| HAM001 | 10 |
| DRL001 | 3 |

I also checked the test database after the rollback:

```text
sales: 0
sale_items: 0
stock_movements: 0
```

This confirmed that no changes were saved from the failed sale.

## Docker

I used Docker to run the application in a container.

Build the image:

```bash
docker build -t hardware-inventory:ci .
```

Run the application:

```bash
docker run -it --name hardware-inventory -v inventory-data:/data hardware-inventory:ci
```

I used a named volume to keep the database outside the container.

### Docker Persistence

I tested Docker persistence by adding a product inside the container.

```text
SKU: DOC001
Name: Docker Hammer
Quantity: 10
```

After removing the container and starting a new one with the same volume, I searched for the product again.

```text
SKU: DOC001
Name: Docker Hammer
Quantity: 10
```

The product was still available, which confirmed that the database was saved in the volume.

### Docker Tests

I ran the tests inside Docker:

```bash
docker run --rm hardware-inventory:ci python -m pytest -q
```

Actual output:

```text
42 passed in 0.04s
```

I also ran the tests and Ruff locally:

```text
42 passed in 0.03s
All checks passed!
```

## Database Backup and Restore

I added a backup option using SQLite's `backup()` function.

After creating the backup, I checked its integrity.

```text
Backup integrity: ok
```

I also compared the original database with the backup.

```text
suppliers: Original=4, Backup=4
products: Original=13, Backup=13
sales: Original=6, Backup=6
sale_items: Original=13, Backup=13
stock_movements: Original=2, Backup=2
```

All the row counts matched.

### Restore

To restore the database, first stop the application.

Create a restored copy:

```bash
cp inventory_backup.db inventory_restored.db
```

Check the restored database:

```bash
python -c "import sqlite3; c=sqlite3.connect('inventory_restored.db'); print(c.execute('PRAGMA integrity_check').fetchone()[0]); c.close()"
```

I also tested restoring the database using Python.

Actual output:

```text
Database restored successfully!
Integrity: ok
```

To use the restored database:

```bash
INVENTORY_DB=inventory_restored.db python main.py
```

## Releases

### v1.0.0

This is the first release of the project. It includes product management, search, reports, stock updates, sales, database backup, and Docker support.

### v1.1.0

This version adds a low-stock warning when the application starts.

## Docker Rollback

I used Docker image tags to manage different versions of the application.

To run version 1.1.0:

```bash
docker run -it --name hardware-inventory -v inventory-data:/data hardware-inventory:1.1.0
```

After exiting the application, remove the container:

```bash
docker rm hardware-inventory
```

Run version 1.0.0 using the same volume:

```bash
docker run -it --name hardware-inventory -v inventory-data:/data hardware-inventory:1.0.0
```

The goal is to confirm that the older version runs without the low-stock startup warning and that the inventory data is still available.

**Rollback test is pending. Actual output will be added after verification.**

## Self-Review

While working on this project, I learned how to use Python with SQLite and how to organize database operations into separate functions. I also got more practice with SQL queries, joins, constraints, and transactions.

One important thing I learned was how transactions work. When a sale fails because there is not enough stock, the database should not save any changes from that sale. Testing this helped me understand why transactions are useful.

I also learned how Docker volumes work. I tested this by removing a container and starting a new one using the same volume. The inventory data was still available.

If I worked on this project again, I would plan the database functions and tests earlier. This would help me organize the code better and avoid making too many changes later.
