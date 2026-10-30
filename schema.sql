-- 1. Suppliers
CREATE TABLE IF NOT EXISTS suppliers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE CHECK (length(trim(name)) > 0),
    contact_email TEXT
) STRICT;


-- 2. Products
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    sku TEXT NOT NULL UNIQUE CHECK (length(trim(sku)) > 0),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    category TEXT NOT NULL CHECK (length(trim(category)) > 0),
    supplier_id INTEGER NOT NULL,
    unit_price INTEGER NOT NULL CHECK (unit_price >= 0),
    quantity INTEGER NOT NULL CHECK (quantity >= 0),
    reorder_level INTEGER NOT NULL CHECK (reorder_level >= 0),

    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
) STRICT;


-- 3. Sales
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY,
    sale_date TEXT NOT NULL,
    seed_key TEXT UNIQUE
) STRICT;


-- 4. Sale Items
CREATE TABLE IF NOT EXISTS sale_items (
    id INTEGER PRIMARY KEY,
    sale_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price INTEGER NOT NULL CHECK (unit_price >= 0),

    FOREIGN KEY (sale_id) REFERENCES sales(id),
    FOREIGN KEY (product_id) REFERENCES products(id),

    UNIQUE (sale_id, product_id)
) STRICT;


-- 5. Stock Movements
CREATE TABLE IF NOT EXISTS stock_movements (
    id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,
    change INTEGER NOT NULL CHECK (change != 0),
    reason TEXT NOT NULL CHECK (
        reason IN ('restock', 'adjustment', 'sale')
    ),
    created_at TEXT NOT NULL,

    FOREIGN KEY (product_id) REFERENCES products(id)
        ON DELETE CASCADE
) STRICT;


-- Indexes
CREATE INDEX IF NOT EXISTS idx_products_supplier
ON products(supplier_id);

CREATE INDEX IF NOT EXISTS idx_sale_items_product
ON sale_items(product_id);