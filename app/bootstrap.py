
from app.database import get_connection, load_data


def initialize_database():
    with get_connection() as conn:
        exists = conn.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name = 'purchase_orders'
        """).fetchone()

        if exists:
            count = conn.execute(
                "SELECT COUNT(*) FROM purchase_orders"
            ).fetchone()[0]

            if count > 0:
                print(
                    "Database already contains purchase orders. "
                    "Skipping sample data import."
                )
                return

    print("Initializing sample database...")
    load_data()
    print("Database initialized successfully.")


if __name__ == "__main__":
    initialize_database()
