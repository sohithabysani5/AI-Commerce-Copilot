from pathlib import Path
import sys

# Add project root to Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from database.database import get_connection


def search_products(
    category=None,
    color=None,
    size=None,
    max_price=None,
    min_price=None
):
    """
    Search products using filters.
    """

    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT
            product_id,
            name,
            category,
            description,
            price,
            color,
            size,
            stock,
            rating
        FROM products
        WHERE stock > 0
    """

    parameters = []

    if category:
        query += " AND LOWER(category) = LOWER(?)"
        parameters.append(category)

    if color:
        query += " AND LOWER(color) = LOWER(?)"
        parameters.append(color)

    if size:
        query += " AND LOWER(size) = LOWER(?)"
        parameters.append(size)

    if max_price is not None:
        query += " AND price <= ?"
        parameters.append(max_price)

    if min_price is not None:
        query += " AND price >= ?"
        parameters.append(min_price)

    query += " ORDER BY rating DESC"

    cursor.execute(query, parameters)

    rows = cursor.fetchall()

    connection.close()

    products = []

    for row in rows:
        products.append({
            "product_id": row[0],
            "name": row[1],
            "category": row[2],
            "description": row[3],
            "price": row[4],
            "color": row[5],
            "size": row[6],
            "stock": row[7],
            "rating": row[8]
        })

    return products


def get_product_details(product_id):
    """
    Get complete information about one product.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            product_id,
            name,
            category,
            description,
            price,
            color,
            size,
            stock,
            rating
        FROM products
        WHERE product_id = ?
    """, (product_id,))

    row = cursor.fetchone()

    connection.close()

    if not row:
        return {
            "success": False,
            "message": "Product not found."
        }

    return {
        "success": True,
        "product_id": row[0],
        "name": row[1],
        "category": row[2],
        "description": row[3],
        "price": row[4],
        "color": row[5],
        "size": row[6],
        "stock": row[7],
        "rating": row[8]
    }


def check_stock(product_id):
    """
    Check stock availability for a product.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT name, stock
        FROM products
        WHERE product_id = ?
    """, (product_id,))

    row = cursor.fetchone()

    connection.close()

    if not row:
        return {
            "success": False,
            "message": "Product not found."
        }

    return {
        "success": True,
        "product_id": product_id,
        "product_name": row[0],
        "stock": row[1],
        "available": row[1] > 0
    }