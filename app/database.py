
import csv
import os
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def get_connection():
    db_path = Path(
        os.getenv("SUPPLYCHAIN_DB_PATH", str(ROOT / "supplychain.db"))
    )
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def load_data(data_dir=None):
    folder = Path(data_dir) if data_dir else ROOT / "data"

    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS purchase_orders (
                purchase_order_id TEXT PRIMARY KEY,
                supplier TEXT NOT NULL,
                ordered_quantity INTEGER NOT NULL,
                unit_price_cents INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS deliveries (
                purchase_order_id TEXT PRIMARY KEY,
                received_quantity INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS invoices (
                purchase_order_id TEXT PRIMARY KEY,
                invoiced_quantity INTEGER NOT NULL
            );
        """)

        with open(
            folder / "purchase_orders.csv",
            newline="",
            encoding="utf-8-sig"
        ) as file:
            for row in csv.DictReader(file):
                quantity = int(row["ordered_quantity"])
                price_cents = round(float(row["unit_price"]) * 100)

                if quantity < 0 or price_cents < 0:
                    raise ValueError("Negative values are not allowed")

                conn.execute("""
                    INSERT OR REPLACE INTO purchase_orders
                    VALUES (?, ?, ?, ?)
                """, (
                    row["purchase_order_id"],
                    row["supplier"],
                    quantity,
                    price_cents
                ))

        for filename, table, column in [
            ("deliveries.csv", "deliveries", "received_quantity"),
            ("invoices.csv", "invoices", "invoiced_quantity")
        ]:
            with open(
                folder / filename,
                newline="",
                encoding="utf-8-sig"
            ) as file:
                for row in csv.DictReader(file):
                    quantity = int(row[column])

                    if quantity < 0:
                        raise ValueError("Negative quantity detected")

                    conn.execute(
                        f"INSERT OR REPLACE INTO {table} VALUES (?, ?)",
                        (row["purchase_order_id"], quantity)
                    )


def find_order(purchase_order_id):
    with get_connection() as conn:
        row = conn.execute("""
            SELECT
                p.purchase_order_id,
                p.supplier,
                p.ordered_quantity,
                p.unit_price_cents,
                d.received_quantity,
                i.invoiced_quantity
            FROM purchase_orders p
            LEFT JOIN deliveries d
                ON p.purchase_order_id = d.purchase_order_id
            LEFT JOIN invoices i
                ON p.purchase_order_id = i.purchase_order_id
            WHERE p.purchase_order_id = ?
        """, (purchase_order_id,)).fetchone()

    return dict(row) if row else None


if __name__ == "__main__":
    load_data()
    print("Supplychain-ai: data imported successfully.")
