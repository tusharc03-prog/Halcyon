import sqlite3
from pathlib import Path
from contextlib import contextmanager

class Database:
    def __init__(self, db_path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    @contextmanager
    def connection(self):
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON")
        try:
            yield con
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    def initialize(self):
        with self.connection() as con:
            con.executescript("""
                CREATE TABLE IF NOT EXISTS company (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    name TEXT NOT NULL DEFAULT 'HALCYON INDIA TECHNOSYS',
                    address TEXT DEFAULT '',
                    gstin TEXT DEFAULT '',
                    msme TEXT DEFAULT ''
                );

                INSERT OR IGNORE INTO company (id, name)
                VALUES (1, 'HALCYON INDIA TECHNOSYS');

                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sku TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    category TEXT DEFAULT '',
                    unit TEXT NOT NULL DEFAULT 'Nos',
                    purchase_price REAL NOT NULL DEFAULT 0,
                    reorder_level REAL NOT NULL DEFAULT 0,
                    active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS stock_movements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    movement_type TEXT NOT NULL CHECK (movement_type IN ('IN', 'OUT')),
                    quantity REAL NOT NULL CHECK (quantity > 0),
                    note TEXT DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(product_id) REFERENCES products(id)
                );

                CREATE INDEX IF NOT EXISTS idx_movements_product
                ON stock_movements(product_id);
            """)

    def get_company(self):
        with self.connection() as con:
            row = con.execute("SELECT * FROM company WHERE id=1").fetchone()
            return dict(row)

    def save_company(self, name, address, gstin, msme):
        if not name.strip():
            raise ValueError("Company name is required.")
        with self.connection() as con:
            con.execute("""
                UPDATE company SET name=?, address=?, gstin=?, msme=?
                WHERE id=1
            """, (name.strip(), address.strip(), gstin.strip(), msme.strip()))
        return self.get_company()

    def add_product(self, sku, name, category, unit, purchase_price, reorder_level):
        sku, name = sku.strip(), name.strip()
        if not sku or not name:
            raise ValueError("Product code and product name are required.")
        if purchase_price < 0 or reorder_level < 0:
            raise ValueError("Price and reorder level cannot be negative.")
        with self.connection() as con:
            cur = con.execute("""
                INSERT INTO products
                (sku, name, category, unit, purchase_price, reorder_level)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (sku, name, category.strip(), unit.strip() or "Nos",
                  purchase_price, reorder_level))
            product_id = cur.lastrowid
        return self.get_product(product_id)

    def get_product(self, product_id):
        with self.connection() as con:
            row = con.execute("""
                SELECT p.*,
                    COALESCE(SUM(CASE
                        WHEN m.movement_type='IN' THEN m.quantity
                        WHEN m.movement_type='OUT' THEN -m.quantity
                        ELSE 0 END), 0) AS balance
                FROM products p
                LEFT JOIN stock_movements m ON m.product_id=p.id
                WHERE p.id=?
                GROUP BY p.id
            """, (product_id,)).fetchone()
            return dict(row) if row else None

    def list_products(self):
        with self.connection() as con:
            rows = con.execute("""
                SELECT p.*,
                    COALESCE(SUM(CASE
                        WHEN m.movement_type='IN' THEN m.quantity
                        WHEN m.movement_type='OUT' THEN -m.quantity
                        ELSE 0 END), 0) AS balance
                FROM products p
                LEFT JOIN stock_movements m ON m.product_id=p.id
                WHERE p.active=1
                GROUP BY p.id
                ORDER BY p.name COLLATE NOCASE
            """).fetchall()
            return [dict(r) for r in rows]

    def record_movement(self, product_id, movement_type, quantity, note=""):
        movement_type = movement_type.upper()
        quantity = float(quantity)
        if movement_type not in ("IN", "OUT"):
            raise ValueError("Movement must be IN or OUT.")
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
        with self.connection() as con:
            product = con.execute(
                "SELECT id FROM products WHERE id=? AND active=1",
                (int(product_id),)
            ).fetchone()
            if not product:
                raise ValueError("Select a valid product.")
            if movement_type == "OUT":
                row = con.execute("""
                    SELECT COALESCE(SUM(
                        CASE WHEN movement_type='IN' THEN quantity
                             ELSE -quantity END
                    ), 0) AS balance
                    FROM stock_movements WHERE product_id=?
                """, (int(product_id),)).fetchone()
                if quantity > float(row["balance"]):
                    raise ValueError("Insufficient stock. Stock-out was not saved.")
            con.execute("""
                INSERT INTO stock_movements
                (product_id, movement_type, quantity, note)
                VALUES (?, ?, ?, ?)
            """, (int(product_id), movement_type, quantity, note.strip()))
        return {"success": True, "balance": self.get_product(product_id)["balance"]}

    def stock_report(self):
        products = self.list_products()
        movements = self.movement_history()
        total_units = sum(float(p["balance"]) for p in products)
        stock_value = sum(float(p["balance"]) * float(p["purchase_price"]) for p in products)
        low_stock = [p for p in products if float(p["balance"]) <= float(p["reorder_level"])]
        return {
            "product_count": len(products),
            "total_units": total_units,
            "stock_value": stock_value,
            "low_stock_count": len(low_stock),
            "low_stock": low_stock,
            "products": products,
            "movements": movements
        }

    def movement_history(self, limit=100):
        with self.connection() as con:
            rows = con.execute("""
                SELECT m.id, m.movement_type, m.quantity, m.note, m.created_at,
                       p.sku, p.name, p.unit
                FROM stock_movements m
                JOIN products p ON p.id=m.product_id
                ORDER BY m.id DESC LIMIT ?
            """, (int(limit),)).fetchall()
            return [dict(r) for r in rows]
