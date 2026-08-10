from pathlib import Path
import sys

# Make project root available
sys.path.append(str(Path(__file__).resolve().parent.parent))

from database.database import get_connection


# ============================================================
# GET ORDER STATUS
# ============================================================

def get_order_status(order_id):
    """
    Get the current status and details of an order.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            o.order_id,
            o.customer_id,
            p.name,
            o.quantity,
            o.amount,
            o.status,
            o.created_at
        FROM orders o
        JOIN products p
            ON o.product_id = p.product_id
        WHERE o.order_id = ?
    """, (order_id,))

    row = cursor.fetchone()

    connection.close()

    if not row:
        return {
            "success": False,
            "message": "Order not found."
        }

    return {
        "success": True,
        "order_id": row[0],
        "customer_id": row[1],
        "product": row[2],
        "quantity": row[3],
        "amount": row[4],
        "status": row[5],
        "created_at": row[6]
    }


# ============================================================
# GET CUSTOMER ORDERS
# ============================================================

def get_customer_orders(customer_id):
    """
    Get all orders belonging to a customer.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            o.order_id,
            p.name,
            o.quantity,
            o.amount,
            o.status,
            o.created_at
        FROM orders o
        JOIN products p
            ON o.product_id = p.product_id
        WHERE o.customer_id = ?
        ORDER BY o.created_at DESC
    """, (customer_id,))

    rows = cursor.fetchall()

    connection.close()

    orders = []

    for row in rows:
        orders.append({
            "order_id": row[0],
            "product": row[1],
            "quantity": row[2],
            "amount": row[3],
            "status": row[4],
            "created_at": row[5]
        })

    return orders


# ============================================================
# CANCEL ORDER
# ============================================================

def cancel_order(order_id):
    """
    Cancel an order if it is still eligible.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT status
        FROM orders
        WHERE order_id = ?
    """, (order_id,))

    row = cursor.fetchone()

    if not row:
        connection.close()

        return {
            "success": False,
            "message": "Order not found."
        }

    current_status = row[0]

    # Orders that cannot be cancelled
    if current_status in [
        "Shipped",
        "Out for Delivery",
        "Delivered",
        "Cancelled"
    ]:

        connection.close()

        if current_status == "Cancelled":
            return {
                "success": False,
                "message": f"Order {order_id} is already cancelled."
            }

        return {
            "success": False,
            "message": (
                f"Order cannot be cancelled because it is "
                f"already {current_status}."
            )
        }

    cursor.execute("""
        UPDATE orders
        SET status = 'Cancelled'
        WHERE order_id = ?
    """, (order_id,))

    connection.commit()
    connection.close()

    return {
        "success": True,
        "order_id": order_id,
        "status": "Cancelled",
        "message": f"Order {order_id} has been cancelled."
    }


# ============================================================
# CREATE ORDER
# ============================================================

def create_order(customer_id, product_id, quantity):
    """
    Create a new order for a customer.

    Steps:
    1. Check whether the product exists.
    2. Check whether enough stock is available.
    3. Calculate the total amount.
    4. Generate a new order ID.
    5. Insert the order.
    6. Reduce product stock.
    """

    # --------------------------------------------------------
    # Validate quantity
    # --------------------------------------------------------

    if quantity is None or quantity <= 0:
        return {
            "success": False,
            "message": "Quantity must be greater than zero."
        }

    connection = get_connection()
    cursor = connection.cursor()

    # --------------------------------------------------------
    # Check customer
    # --------------------------------------------------------

    cursor.execute("""
        SELECT customer_id
        FROM customers
        WHERE customer_id = ?
    """, (customer_id,))

    customer = cursor.fetchone()

    if not customer:
        connection.close()

        return {
            "success": False,
            "message": f"Customer {customer_id} was not found."
        }

    # --------------------------------------------------------
    # Check product
    # --------------------------------------------------------

    cursor.execute("""
        SELECT
            product_id,
            name,
            price,
            stock
        FROM products
        WHERE product_id = ?
    """, (product_id,))

    product = cursor.fetchone()

    if not product:
        connection.close()

        return {
            "success": False,
            "message": f"Product {product_id} was not found."
        }

    product_id_db = product[0]
    product_name = product[1]
    price = product[2]
    stock = product[3]

    # --------------------------------------------------------
    # Check stock
    # --------------------------------------------------------

    if stock <= 0:
        connection.close()

        return {
            "success": False,
            "message": (
                f"{product_name} is currently out of stock."
            )
        }

    if stock < quantity:
        connection.close()

        return {
            "success": False,
            "message": (
                f"Only {stock} item(s) of {product_name} "
                f"are available."
            )
        }

    # --------------------------------------------------------
    # Calculate total amount
    # --------------------------------------------------------

    amount = price * quantity

    # --------------------------------------------------------
    # Generate new order ID
    # --------------------------------------------------------

    cursor.execute("""
        SELECT order_id
        FROM orders
        ORDER BY rowid DESC
        LIMIT 1
    """)

    last_order = cursor.fetchone()

    if last_order:
        last_order_id = last_order[0]

        try:
            last_number = int(
                last_order_id.replace("ORD", "")
            )

            new_number = last_number + 1

        except (ValueError, AttributeError):
            new_number = 1

    else:
        new_number = 1

    order_id = f"ORD{new_number:03d}"

    # --------------------------------------------------------
    # Insert new order
    # --------------------------------------------------------

    cursor.execute("""
        INSERT INTO orders
        (
            order_id,
            customer_id,
            product_id,
            quantity,
            amount,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
    """, (
        order_id,
        customer_id,
        product_id_db,
        quantity,
        amount,
        "Placed",
    ))

    # --------------------------------------------------------
    # Reduce product stock
    # --------------------------------------------------------

    cursor.execute("""
        UPDATE products
        SET stock = stock - ?
        WHERE product_id = ?
    """, (
        quantity,
        product_id_db,
    ))

    # --------------------------------------------------------
    # Save changes
    # --------------------------------------------------------

    connection.commit()
    connection.close()

    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return {
        "success": True,
        "order_id": order_id,
        "customer_id": customer_id,
        "product_id": product_id_db,
        "product": product_name,
        "quantity": quantity,
        "amount": amount,
        "status": "Placed",
        "message": (
            f"Order {order_id} has been placed successfully."
        )
    }