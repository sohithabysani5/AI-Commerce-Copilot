import re

from tools.product_tools import search_products
from tools.orders_tools import create_order
from tools.orders_tools import get_order_status
from tools.orders_tools import cancel_order
from tools.return_tools import get_return_status


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def extract_order_id(message):
    match = re.search(r"\bORD\d+\b", message.upper())

    if match:
        return match.group(0)

    return None


def extract_return_id(message):
    match = re.search(r"\bRET\d+\b", message.upper())

    if match:
        return match.group(0)

    return None


def extract_customer_id(message):
    match = re.search(r"\bC\d+\b", message.upper())

    if match:
        return match.group(0)

    return None


def is_yes(message):
    return message.strip().lower() in [
        "yes",
        "y",
        "yeah",
        "yep",
        "confirm",
        "confirmed",
        "place order"
    ]


def is_no(message):
    return message.strip().lower() in [
        "no",
        "n",
        "cancel",
        "don't",
        "dont"
    ]


# ============================================================
# PRODUCT SEARCH
# ============================================================

def handle_product_search(message):

    text = message.lower()

    category = None
    color = None
    max_price = None

    # --------------------------------------------------------
    # CATEGORY
    # --------------------------------------------------------

    categories = [
        "dress",
        "shirt",
        "shoes",
        "jeans",
        "tshirt",
        "t-shirt",
        "phone",
        "laptop"
    ]

    for item in categories:

        if item in text:

            if item in ["tshirt", "t-shirt"]:
                category = "T-Shirt"

            elif item == "phone":
                category = "Phone"

            elif item == "laptop":
                category = "Laptop"

            else:
                category = item.capitalize()

            break

    # --------------------------------------------------------
    # COLOR
    # --------------------------------------------------------

    colors = [
        "black",
        "blue",
        "red",
        "green",
        "white",
        "yellow"
    ]

    for item in colors:

        if item in text:
            color = item.capitalize()
            break

    # --------------------------------------------------------
    # PRICE
    # --------------------------------------------------------

    price_match = re.search(
        r"(?:under|below|less than|maximum|max)\s*[₹rs.]?\s*(\d+)",
        text
    )

    if price_match:

        max_price = float(
            price_match.group(1)
        )

    # --------------------------------------------------------
    # DATABASE SEARCH
    # --------------------------------------------------------

    results = search_products(
        category=category,
        color=color,
        max_price=max_price
    )

    if not results:

        return (
            "Sorry, I couldn't find any products "
            "matching your request."
        )

    response = (
        f"I found {len(results)} "
        f"products matching your request:\n\n"
    )

    for index, product in enumerate(
        results,
        start=1
    ):

        response += (
            f"{index}. **{product['name']}**\n"
            f"   Price: ₹{product['price']}\n"
            f"   Color: {product['color']}\n"
            f"   Size: {product['size']}\n"
            f"   Stock: {product['stock']}\n"
            f"   Rating: {product['rating']}/5\n\n"
        )

    return response, results


# ============================================================
# LOCAL COMMERCE AGENT
# ============================================================

def local_commerce_agent(
    user_message,
    state
):

    message = user_message.strip()
    lower_message = message.lower()

    print("\n====================================")
    print("DEBUG MESSAGE:", message)
    print("DEBUG STATE BEFORE:", state)
    print("====================================")


    # ========================================================
    # 1. WAITING FOR PRODUCT SELECTION
    # ========================================================

    if state.get("step") == "WAITING_FOR_PRODUCT":

        products = state.get(
            "products",
            []
        )

        # ----------------------------------------------------
        # CUSTOMER ENTERED A NUMBER
        # ----------------------------------------------------

        if message.isdigit():

            selected_number = int(message)

            # ------------------------------------------------
            # IMPORTANT FIX
            # ------------------------------------------------

            if len(products) == 0:

                print(
                    "DEBUG: Product list is empty."
                )

                state.clear()

                return (
                    "I lost the previous product list. "
                    "Let's search again.\n\n"
                    "What product would you like to order?\n\n"
                    "Example:\n"
                    "• I want a dress\n"
                    "• I want black shoes"
                )

            # ------------------------------------------------
            # INVALID NUMBER
            # ------------------------------------------------

            if (
                selected_number < 1
                or selected_number > len(products)
            ):

                return (
                    f"Please enter a number between "
                    f"1 and {len(products)}."
                )

            # ------------------------------------------------
            # SELECT PRODUCT
            # ------------------------------------------------

            selected_product = products[
                selected_number - 1
            ]

            state["selected_product"] = (
                selected_product
            )

            state["step"] = (
                "WAITING_FOR_QUANTITY"
            )

            print(
                "DEBUG SELECTED PRODUCT:",
                selected_product
            )

            print(
                "DEBUG STATE AFTER:",
                state
            )

            return (
                f"You selected "
                f"**{selected_product['name']}**.\n\n"
                f"Price: ₹{selected_product['price']}\n"
                f"Color: {selected_product['color']}\n"
                f"Size: {selected_product['size']}\n"
                f"Stock: {selected_product['stock']}\n"
                f"Rating: {selected_product['rating']}/5\n\n"
                "How many would you like to order?"
            )

        # ----------------------------------------------------
        # CUSTOMER ENTERED PRODUCT REQUEST
        # ----------------------------------------------------

        result = handle_product_search(
            message
        )

        if isinstance(result, str):

            return result

        response, products = result

        # ----------------------------------------------------
        # SAVE PRODUCT LIST
        # ----------------------------------------------------

        state["products"] = products

        state["step"] = (
            "WAITING_FOR_PRODUCT"
        )

        print(
            "DEBUG PRODUCTS SAVED:",
            products
        )

        print(
            "DEBUG STATE AFTER SEARCH:",
            state
        )

        return (
            response
            + "\nPlease enter the number of "
              "the product you want to order."
        )


    # ========================================================
    # 2. WAITING FOR QUANTITY
    # ========================================================

    if state.get("step") == "WAITING_FOR_QUANTITY":

        selected_product = state.get(
            "selected_product"
        )

        if not selected_product:

            state.clear()

            return (
                "Something went wrong with the "
                "product selection.\n\n"
                "Please start the order again."
            )

        # ----------------------------------------------------
        # QUANTITY MUST BE NUMBER
        # ----------------------------------------------------

        if not message.isdigit():

            return (
                "Please enter the quantity as a number.\n\n"
                "Example: 1 or 2"
            )

        quantity = int(message)

        # ----------------------------------------------------
        # QUANTITY VALIDATION
        # ----------------------------------------------------

        if quantity <= 0:

            return (
                "Quantity must be at least 1."
            )

        stock = int(
            selected_product["stock"]
        )

        if quantity > stock:

            return (
                f"Sorry, only {stock} units "
                f"are available."
            )

        # ----------------------------------------------------
        # CALCULATE TOTAL
        # ----------------------------------------------------

        price = float(
            selected_product["price"]
        )

        total = price * quantity

        # ----------------------------------------------------
        # SAVE STATE
        # ----------------------------------------------------

        state["quantity"] = quantity

        state["total"] = total

        state["step"] = (
            "WAITING_FOR_CONFIRMATION"
        )

        print(
            "DEBUG QUANTITY:",
            quantity
        )

        print(
            "DEBUG TOTAL:",
            total
        )

        print(
            "DEBUG STATE AFTER:",
            state
        )

        return (
            "Please confirm your order:\n\n"
            f"**Product:** "
            f"{selected_product['name']}\n"
            f"**Quantity:** {quantity}\n"
            f"**Price per item:** ₹{price}\n"
            f"**Total:** ₹{total}\n\n"
            "Would you like to place this order?\n\n"
            "Please answer **Yes** or **No**."
        )


    # ========================================================
    # 3. WAITING FOR CONFIRMATION
    # ========================================================

    if state.get("step") == "WAITING_FOR_CONFIRMATION":

        # ----------------------------------------------------
        # NO
        # ----------------------------------------------------

        if is_no(message):

            state.clear()

            return (
                "No problem. Your order was cancelled.\n\n"
                "You can start a new order whenever you want."
            )

        # ----------------------------------------------------
        # YES
        # ----------------------------------------------------

        if is_yes(message):

            state["step"] = (
                "WAITING_FOR_CUSTOMER_ID"
            )

            print(
                "DEBUG STATE AFTER:",
                state
            )

            return (
                "Great! 🛒 Your order is ready.\n\n"
                "Please provide your Customer ID "
                "to complete the order.\n\n"
                "Example: C001"
            )

        return (
            "Please confirm the order by answering "
            "**Yes** or **No**."
        )


    # ========================================================
    # 4. WAITING FOR CUSTOMER ID
    # ========================================================

    if state.get("step") == "WAITING_FOR_CUSTOMER_ID":

        customer_id = extract_customer_id(
            message
        )

        if not customer_id:

            return (
                "Please provide a valid Customer ID.\n\n"
                "Example: C001"
            )

        selected_product = state.get(
            "selected_product"
        )

        quantity = state.get(
            "quantity"
        )

        if not selected_product or not quantity:

            state.clear()

            return (
                "The order information was lost.\n\n"
                "Please start the order again."
            )

        # ----------------------------------------------------
        # CREATE ORDER
        # ----------------------------------------------------

        try:

            result = create_order(
                customer_id,
                selected_product["product_id"],
                quantity
            )

        except Exception as e:

            print(
                "DEBUG CREATE ORDER ERROR:",
                e
            )

            return (
                "Sorry, I couldn't create the order.\n\n"
                f"Error: {str(e)}"
            )

        print(
            "DEBUG ORDER RESULT:",
            result
        )

        # ----------------------------------------------------
        # ORDER FAILED
        # ----------------------------------------------------

        if not result.get("success"):

            return (
                "Sorry, I couldn't place the order.\n\n"
                f"{result.get('message', 'Unknown error')}"
            )

        # ----------------------------------------------------
        # ORDER SUCCESS
        # ----------------------------------------------------

        order_id = result.get(
            "order_id"
        )

        total = result.get(
            "amount",
            state.get("total")
        )

        product_name = selected_product[
            "name"
        ]

        # Clear order state
        state.clear()

        return (
            "🎉 **Order placed successfully!**\n\n"
            f"**Order ID:** {order_id}\n"
            f"**Customer ID:** {customer_id}\n"
            f"**Product:** {product_name}\n"
            f"**Quantity:** {quantity}\n"
            f"**Total:** ₹{total}\n\n"
            "Thank you for shopping with us! 🛒"
        )


    # ========================================================
    # 5. START ORDER
    # ========================================================

    if (
        "i want to order" in lower_message
        or "place an order" in lower_message
        or "buy something" in lower_message
        or lower_message == "order"
    ):

        state.clear()

        state["step"] = (
            "WAITING_FOR_PRODUCT"
        )

        print(
            "DEBUG ORDER START STATE:",
            state
        )

        return (
            "Sure! 🛒 Let's place your order.\n\n"
            "What product would you like to order?\n\n"
            "For example:\n\n"
            "- I want a dress\n"
            "- Show me dresses\n"
            "- I want a black dress under ₹2000"
        )


    # ========================================================
    # 6. PRODUCT SEARCH
    # ========================================================

    product_keywords = [
        "dress",
        "shirt",
        "shoes",
        "jeans",
        "tshirt",
        "t-shirt",
        "phone",
        "laptop"
    ]

    contains_product_request = any(
        keyword in lower_message
        for keyword in product_keywords
    )

    if contains_product_request:

        result = handle_product_search(
            message
        )

        if isinstance(result, str):

            return result

        response, products = result

        # ----------------------------------------------------
        # SAVE PRODUCTS
        # ----------------------------------------------------

        state["products"] = products

        # IMPORTANT:
        # If customer is simply searching products,
        # we still allow product selection.
        state["step"] = (
            "WAITING_FOR_PRODUCT"
        )

        print(
            "DEBUG PRODUCT SEARCH RESULT:",
            products
        )

        print(
            "DEBUG STATE AFTER PRODUCT SEARCH:",
            state
        )

        return (
            response
            + "\nPlease enter the number of "
              "the product you want."
        )


    # ========================================================
    # 7. ORDER TRACKING
    # ========================================================

    if (
        "where is my order" in lower_message
        or "order status" in lower_message
        or "track my order" in lower_message
        or "status of my order" in lower_message
    ):

        order_id = extract_order_id(
            message
        )

        if not order_id:

            return (
                "Please provide your Order ID.\n\n"
                "Example: ORD001"
            )

        result = get_order_status(
            order_id
        )

        print(
            "DEBUG ORDER STATUS:",
            result
        )

        if not result.get("success"):

            return result.get(
                "message",
                "Order not found."
            )

        return (
            f"Your order **{result['order_id']}** "
            f"for **{result['product']}** is currently "
            f"**{result['status']}**.\n\n"
            f"- Quantity: {result['quantity']}\n"
            f"- Amount: ₹{result['amount']}\n"
            f"- Order Date: {result['created_at']}"
        )


    # ========================================================
    # 8. CANCEL ORDER
    # ========================================================

    if (
        "cancel order" in lower_message
        or "cancel my order" in lower_message
    ):

        order_id = extract_order_id(
            message
        )

        if not order_id:

            return (
                "Please provide your Order ID.\n\n"
                "Example: Cancel order ORD002"
            )

        try:

            result = cancel_order(
                order_id
            )

        except Exception as e:

            return (
                f"Unable to cancel the order: {str(e)}"
            )

        print(
            "DEBUG CANCEL RESULT:",
            result
        )

        if not result.get("success"):

            return result.get(
                "message",
                "Order cannot be cancelled."
            )

        return (
            f"Order **{order_id}** has been "
            f"cancelled successfully."
        )


    # ========================================================
    # 9. RETURN STATUS
    # ========================================================

    if (
        "return" in lower_message
        and (
            "status" in lower_message
            or "where" in lower_message
        )
    ):

        return_id = extract_return_id(
            message
        )

        if return_id:

            result = get_return_status(
                return_id
            )

        else:

            return (
                "Please provide your Return ID.\n\n"
                "Example:\n"
                "RET20260809132757"
            )

        print(
            "DEBUG RETURN RESULT:",
            result
        )

        if not result.get("success"):

            return result.get(
                "message",
                "Return request not found."
            )

        return (
            f"Your return request for order "
            f"**{result['order_id']}** is currently "
            f"**{result['status']}**.\n\n"
            f"- Return ID: {result['return_id']}\n"
            f"- Reason: {result['reason']}"
        )


    # ========================================================
    # 10. GENERAL HELP
    # ========================================================

    return (
        "I can help you with:\n\n"
        "🛍️ **Product search**\n"
        "🛒 **Place an order**\n"
        "📦 **Order tracking**\n"
        "❌ **Order cancellation**\n"
        "↩️ **Return requests**\n\n"
        "Try saying:\n\n"
        "• I want a dress\n"
        "• I want to order\n"
        "• Show me dresses\n"
        "• Where is my order ORD001?\n"
        "• Cancel order ORD002"
    )