import csv
from pathlib import Path
import sys

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from database.database import get_connection


DATA_DIR = Path(__file__).resolve().parent


def load_products():
    csv_path = DATA_DIR / "products.csv"

    connection = get_connection()
    cursor = connection.cursor()

    with open(csv_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO products
                (
                    product_id,
                    name,
                    category,
                    description,
                    price,
                    color,
                    size,
                    stock,
                    rating
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row["product_id"],
                row["name"],
                row["category"],
                row["description"],
                float(row["price"]),
                row["color"],
                row["size"],
                int(row["stock"]),
                float(row["rating"])
            ))

    connection.commit()
    connection.close()

    print("Products loaded successfully!")


def load_customers():
    csv_path = DATA_DIR / "customers.csv"

    connection = get_connection()
    cursor = connection.cursor()

    with open(csv_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO customers
                (
                    customer_id,
                    name,
                    phone,
                    address
                )
                VALUES (?, ?, ?, ?)
            """, (
                row["customer_id"],
                row["name"],
                row["phone"],
                row["address"]
            ))

    connection.commit()
    connection.close()

    print("Customers loaded successfully!")


def load_orders():
    csv_path = DATA_DIR / "orders.csv"

    connection = get_connection()
    cursor = connection.cursor()

    with open(csv_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO orders
                (
                    order_id,
                    customer_id,
                    product_id,
                    quantity,
                    amount,
                    status,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                row["order_id"],
                row["customer_id"],
                row["product_id"],
                int(row["quantity"]),
                float(row["amount"]),
                row["status"],
                row["created_at"]
            ))

    connection.commit()
    connection.close()

    print("Orders loaded successfully!")


if __name__ == "__main__":

    print("\nLoading commerce data...\n")

    load_products()
    load_customers()
    load_orders()

    print("\nAll commerce data loaded successfully!")