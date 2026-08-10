from pathlib import Path
import sys

# ============================================================
# PROJECT ROOT
# ============================================================

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from database.database import get_connection


# ============================================================
# CREATE RETURN REQUEST
# ============================================================

def create_return(order_id, reason):
    """
    Create a return request for an order.

    The function:
    1. Checks whether the order exists.
    2. Checks whether the order is eligible for return.
    3. Checks whether a return already exists.
    4. Creates a new return request.
    5. Returns the return details.
    """

    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    if not order_id:
        return {
            "success": False,
            "message": "Order ID is required."
        }

    if not reason:
        return {
            "success": False,
            "message": "Return reason is required."
        }

    connection = get_connection()
    cursor = connection.cursor()

    # --------------------------------------------------------
    # Check whether order exists
    # --------------------------------------------------------

    cursor.execute("""
        SELECT
            order_id,
            status
        FROM orders
        WHERE order_id = ?
    """, (order_id,))

    order = cursor.fetchone()

    if not order:
        connection.close()

        return {
            "success": False,
            "message": f"Order {order_id} was not found."
        }

    order_status = order[1]

    # --------------------------------------------------------
    # Check whether order is eligible for return
    # --------------------------------------------------------

    if order_status == "Cancelled":
        connection.close()

        return {
            "success": False,
            "message": (
                f"Order {order_id} cannot be returned "
                "because it was cancelled."
            )
        }

    # --------------------------------------------------------
    # Check whether return already exists
    # --------------------------------------------------------

    cursor.execute("""
        SELECT
            return_id,
            order_id,
            status,
            reason,
            created_at
        FROM returns
        WHERE order_id = ?
        ORDER BY created_at DESC
        LIMIT 1
    """, (order_id,))

    existing_return = cursor.fetchone()

    if existing_return:

        connection.close()

        return {
            "success": True,
            "return_id": existing_return[0],
            "order_id": existing_return[1],
            "status": existing_return[2],
            "reason": existing_return[3],
            "created_at": existing_return[4],
            "message": (
                "A return request already exists for this order."
            )
        }

    # --------------------------------------------------------
    # Generate Return ID
    # --------------------------------------------------------

    cursor.execute("""
        SELECT return_id
        FROM returns
        ORDER BY rowid DESC
        LIMIT 1
    """)

    last_return = cursor.fetchone()

    if last_return:

        last_return_id = last_return[0]

        try:
            # Example:
            # RET20260809132757

            numeric_part = ""

            for character in last_return_id:

                if character.isdigit():
                    numeric_part += character

            if numeric_part:
                last_number = int(numeric_part)

                new_number = last_number + 1

                return_id = f"RET{new_number}"

            else:
                return_id = "RET001"

        except Exception:
            return_id = "RET001"

    else:
        return_id = "RET001"

    # --------------------------------------------------------
    # Create return request
    # --------------------------------------------------------

    cursor.execute("""
        INSERT INTO returns
        (
            return_id,
            order_id,
            status,
            reason,
            created_at
        )
        VALUES (?, ?, ?, ?, datetime('now'))
    """, (
        return_id,
        order_id,
        "Requested",
        reason
    ))

    connection.commit()
    connection.close()

    # --------------------------------------------------------
    # Return successful result
    # --------------------------------------------------------

    return {
        "success": True,
        "return_id": return_id,
        "order_id": order_id,
        "status": "Requested",
        "reason": reason,
        "message": (
            f"Return request for order {order_id} "
            "has been created successfully."
        )
    }


# ============================================================
# GET RETURN STATUS
# ============================================================

def get_return_status(return_id):
    """
    Get the current status of a return request.
    """

    if not return_id:
        return {
            "success": False,
            "message": "Return ID is required."
        }

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            return_id,
            order_id,
            status,
            reason,
            created_at
        FROM returns
        WHERE return_id = ?
    """, (return_id,))

    row = cursor.fetchone()

    connection.close()

    # --------------------------------------------------------
    # Return not found
    # --------------------------------------------------------

    if not row:

        return {
            "success": False,
            "message": (
                f"Return request {return_id} was not found."
            )
        }

    # --------------------------------------------------------
    # Return details
    # --------------------------------------------------------

    return {
        "success": True,
        "return_id": row[0],
        "order_id": row[1],
        "status": row[2],
        "reason": row[3],
        "created_at": row[4]
    }


# ============================================================
# GET RETURN BY ORDER ID
# ============================================================

def get_return_by_order(order_id):
    """
    Get the return request associated with an order.
    """

    if not order_id:

        return {
            "success": False,
            "message": "Order ID is required."
        }

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            return_id,
            order_id,
            status,
            reason,
            created_at
        FROM returns
        WHERE order_id = ?
        ORDER BY created_at DESC
        LIMIT 1
    """, (order_id,))

    row = cursor.fetchone()

    connection.close()

    # --------------------------------------------------------
    # No return found
    # --------------------------------------------------------

    if not row:

        return {
            "success": False,
            "message": (
                f"No return request exists for order {order_id}."
            )
        }

    # --------------------------------------------------------
    # Return details
    # --------------------------------------------------------

    return {
        "success": True,
        "return_id": row[0],
        "order_id": row[1],
        "status": row[2],
        "reason": row[3],
        "created_at": row[4]
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("RETURN TOOLS TEST")
    print("=" * 60)

    print("\nReturn tools loaded successfully.")

    print("\nAvailable functions:")
    print("1. create_return()")
    print("2. get_return_status()")
    print("3. get_return_by_order()")

    print("\nReturn tools are ready.")