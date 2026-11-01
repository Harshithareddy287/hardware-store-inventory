# Hardware Store Inventory Management System

## About the Project

This is a Python project I built to manage inventory for a hardware store.

I used SQLite to store information about products, suppliers, sales, and stock changes.

The application runs through a terminal menu. It allows users to manage products, update stock, record sales, and view reports.

## Features

- Add products and look up their details
- Update product prices and delete products using database functions
- Search products using different filters
- Restock products and adjust stock quantities
- Record sales and update inventory
- Keep a history of stock movements
- View stock value by supplier
- Find products that need restocking
- View sales by product
- Find products that have never been sold
- Create database backups
- Run the application using Docker

## Database

I used SQLite with five tables:

1. `suppliers`
2. `products`
3. `sales`
4. `sale_items`
5. `stock_movements`

Each product has a SKU, name, category, supplier, price, quantity in stock, and reorder level.

I stored prices as integer cents to avoid floating-point errors.

I also used foreign keys, constraints, and STRICT tables to help keep the data valid.

### Sample Data

I created `seed_db.py` to add sample data to the database.

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

## How to Run the Project

Install dependencies:

```bash
pip install -r requirements.txt
```

Create and seed the database:

```bash
python seed_db.py
```

Start the application:

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

The application also supports the `INVENTORY_DB` environment variable.

For example:

```bash
INVENTORY_DB=inventory.db python main.py
```

This allows me to choose which database file the application uses.

## Application Menu

The application uses a terminal menu.

```text
===== HARDWARE STORE INVENTORY =====

1. Search products
2. Look up product by SKU
3. Add product
4. Restock product
5. Record sale
6. View reports
7. Backup database
0. Exit
```

The menu allows users to manage inventory without writing SQL commands.

### Low-Stock Warning

In version 1.1.0, I added a warning that appears when the application starts if any product is at or below its reorder level.

When I tested it locally using the sample database, I got this output:

```text
===== LOW STOCK WARNING: 2 PRODUCTS =====
Drill (DRL001): 3 remaining, reorder level 5
Screws (SCS001): 5 remaining, reorder level 5
```

### Low-Stock Warning Test in Docker

I also tested the warning using Docker version 1.1.0.

The Docker database was different from my local database, so it initially had no low-stock products.

I added a product with these details:

| Field | Value |
|---|---|
| SKU | LOW001 |
| Product | Test Hammer |
| Quantity | 2 |
| Reorder Level | 5 |

I exited the application, removed the container, and started version 1.1.0 again using the same Docker volume.

Actual output:

```text
===== LOW STOCK WARNING: 1 PRODUCTS =====
Test Hammer (LOW001): 2 remaining, reorder level 5
```

This confirmed that the warning works and that the product data remains saved after restarting the container.

## Reports

I created four reports using the sample data.

### Stock Value by Supplier

This report shows the total value of available stock for each supplier.

| Supplier | Stock Value |
|---|---:|
| Power Equipment Co | $1,065.83 |
| Hardware World | $747.58 |
| ABC Tools | $610.53 |
| BuildMart Supplies | $319.40 |

### Low-Stock Products

This report shows products that are at or below their reorder level.

| SKU | Product | Units Short |
|---|---|---:|
| DRL001 | Drill | 2 |
| SCS001 | Screws | 0 |

Screws appears in the report because its quantity is equal to its reorder level.

### Sales by Product

This report shows how many units of each product were sold and the total revenue.

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

Revenue is calculated using the price recorded when each sale was made.

### Never-Sold Products

This report shows products that do not have any recorded sales.

| SKU | Product |
|---|---|
| WIR001 | Electrical Wire |
| OUT001 | Power Outlet |
| SND001 | Sander |

## Stock Changes and Sales

The application allows users to restock products and record sales.

When a product is restocked, its quantity increases. When a sale is recorded, the quantity decreases.

Stock changes are recorded in the `stock_movements` table so there is a history of inventory changes.

### Failed Sale Rollback

I used database transactions to make sure a failed sale does not partially change the inventory.

I tested a sale with 2 hammers and 10 drills.

Before the sale:

| Product | Quantity |
|---|---:|
| HAM001 | 10 |
| DRL001 | 3 |

Function call used in my test:

```python
record_sale(db, [("HAM001", 2), ("DRL001", 10)])
```

The sale failed because there were only 3 drills available.

Error:

```text
ValueError: Not enough stock
```

After the failed sale:

| Product | Quantity |
|---|---:|
| HAM001 | 10 |
| DRL001 | 3 |

I checked that the hammer quantity was unchanged and that no records were saved in the sales tables.

```text
sales: 0
sale_items: 0
stock_movements: 0
```

This confirmed that the transaction was rolled back and no partial changes were saved.

## Testing

I used pytest to test the database operations and application features.

I also used Ruff to check the code.

### Local Test Results

```text
42 passed in 0.03s
All checks passed!
```

I added a GitHub Actions workflow to run the tests and check the code when changes are pushed or a pull request is opened.

The Docker build was also checked through GitHub Actions.

## Docker

I used Docker to run the application in a container.

### Build the Image

```bash
docker build -t hardware-inventory:ci .
```

### Docker Build Verification

I built the Docker image and checked that it completed successfully.

Actual output:

```text
[+] Building 0.6s (10/10) FINISHED
=> CACHED [2/5] WORKDIR /app
=> CACHED [3/5] COPY requirements.txt .
=> CACHED [4/5] RUN pip install --no-cache-dir -r requirements.txt
=> [5/5] COPY . .
=> exporting to image
=> naming to docker.io/library/hardware-inventory:ci
=> unpacking to docker.io/library/hardware-inventory:ci
```

The image built successfully without errors.

### Run the Application

```bash
docker run -it --name hardware-inventory -v inventory-data:/data hardware-inventory:ci
```

I used a named volume called `inventory-data` to store the SQLite database outside the container.

This allows the data to remain available even when the container is removed.

### Docker Persistence Test

I tested Docker persistence by adding a product inside the container.

```text
SKU: DOC001
Name: Docker Hammer
Quantity: 10
```

I exited the application, removed the container, and started another container using the same volume.

I then searched for the product.

Actual output:

```text
SKU: DOC001
Name: Docker Hammer
Quantity: 10
```

The product was still available.

This confirmed that the database was stored in the Docker volume.

### Docker Test Results

I ran the tests inside Docker:

```bash
docker run --rm hardware-inventory:ci python -m pytest -q
```

Actual output:

```text
42 passed in 0.04s
```

## Database Backup and Restore

I added a backup feature using SQLite's `backup()` function.

This creates a copy of the database.

### Backup Verification

After creating the backup, I checked its integrity.

```text
Backup integrity: ok
```

I also compared the number of records in the original database and the backup.

```text
suppliers: Original=4, Backup=4
products: Original=13, Backup=13
sales: Original=6, Backup=6
sale_items: Original=13, Backup=13
stock_movements: Original=2, Backup=2
```

All the row counts matched.

### Restore Verification

To restore the database, I first stopped the application.

I created a restored copy using:

```bash
cp inventory_backup.db inventory_restored.db
```

I checked the restored database using:

```bash
python -c "import sqlite3; c=sqlite3.connect('inventory_restored.db'); print(c.execute('PRAGMA integrity_check').fetchone()[0]); c.close()"
```

I also tested restoring the database using Python.

Actual output:

```text
Database restored successfully!
Integrity: ok
```

I could then run the application using the restored database:

```bash
INVENTORY_DB=inventory_restored.db python main.py
```

This confirmed that the backup could be used to restore the database.

## Releases

I created two versions of the project.

### Version 1.0.0

This was the first release. It includes product management, search, reports, stock updates, sales, database backup, and Docker support.

### Version 1.1.0

In this version, I added a low-stock warning that appears when the application starts.

### Docker Rollback Verification

I tested rolling back from version 1.1.0 to version 1.0.0.

First, I ran version 1.1.0 using the `inventory-data` Docker volume.

I checked that the product `DOC001` was available.

Then I exited the application, removed the container, and started version 1.0.0 using the same volume.

Command:

```bash
docker run -it --name hardware-inventory -v inventory-data:/data hardware-inventory:1.0.0
```

I searched for the same product.

Actual output:

```text
Enter your choice: 2
Enter product SKU: DOC001
SKU: DOC001
Name: Docker Hammer
Price: $15.00
Quantity: 10
Supplier: ABC Tools
```

The product was still available after switching back to version 1.0.0.

Its quantity also remained the same.

This confirmed that I could roll back to an older application version without losing the inventory data stored in the Docker volume.

## Self-Review

While working on this project, I learned how to connect Python with SQLite and organize database operations into separate functions. I also got more practice writing SQL queries, using joins, and adding database constraints.

One important thing I learned was how transactions work. When a sale fails because there is not enough stock, the database should not save part of that sale. Testing this helped me understand why transactions are important.

I also learned how Docker volumes work. I tested this by removing a container and starting another one using the same volume. My product data was still available.

Another thing I learned was how to create different releases and roll back to an older version. I tested both versions using the same Docker volume to make sure the inventory data was not lost.

If I worked on this project again, I would spend more time reviewing edge cases, especially invalid inputs and failed database operations. This would help me identify possible problems earlier and make my tests more complete.

One question I have for a reviewer is whether my transaction handling could be improved when a sale contains multiple products and one product does not have enough stock.