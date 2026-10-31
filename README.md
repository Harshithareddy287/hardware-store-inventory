# Hardware Store Inventory Management System

A Python-based inventory management system for a hardware store.

The application uses SQLite to manage products, suppliers,
inventory levels, sales, and stock movements.

## Features

- Add, look up, update, and delete products
- Search products using multiple filters
- Calculate stock value by supplier
- Identify low-stock products
- View sales by product
- Find products that have never been sold

## Database

The system uses five SQLite tables:

- suppliers
- products
- sales
- sale_items
- stock_movements

Prices are stored as integer cents to avoid floating-point errors.

## Setup

Install dependencies:

    pip install -r requirements.txt

Create and populate the database:

    python seed_db.py

Run tests:

    python -m pytest -v

## Reports

The following results are generated from the sample data.

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

Products at or below their reorder level are included.

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

Revenue uses the price recorded at the time of each sale.

### Never-Sold Products

| SKU | Product |
|---|---|
| WIR001 | Electrical Wire |
| OUT001 | Power Outlet |
| SND001 | Sander |

### Failed Sale Rollback Output

**Before the failed sale:**

| Product SKU | Quantity |
|-------------|----------|
| HAM001      | 10       |
| DRL001      | 3        |

**Sale Attempt:**

The customer tries to purchase 2 hammers and 10 drills.

**Result:** `Sale failed: Not enough stock`

**After the failed sale:**

| Product SKU | Quantity |
|-------------|----------|
| HAM001      | 10       |
| DRL001      | 3        |

**Database records after rollback:**

| Table | Record Count |
|-------|--------------|
| sales | 0 |
| sale_items | 0 |
| stock_movements | 0 |