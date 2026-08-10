from tools.product_tools import search_products

from tools.orders_tools import (
    get_order_status,
    cancel_order,
    create_order,
)

from tools.return_tools import (
    get_return_by_order,
)


# ============================================================
# EXTRACT ORDER ID
# ============================================================

def extract_order_id(message):

    words = (
        message
        .upper()
        .replace("?", " ")
        .replace(".", " ")
        .replace(",", " ")
        .replace("!", " ")
        .replace(":", " ")
        .replace(";", " ")
        .split()
    )

    for word in words:

        if word == "ORDER":
            continue

        if (
            word.startswith("ORD")
            and len(word) > 3
            and word[3:].isdigit()
        ):
            return word

    return None


# ============================================================
# EXTRACT QUANTITY
# ============================================================

def extract_quantity(message):

    words = message.lower().split()

    for word in words:

        if word.isdigit():

            quantity = int(word)

            if quantity > 0:
                return quantity

    # Words such as "one", "two", "three"

    quantity_words = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5
    }

    for word in words:

        if word in quantity_words:

            return quantity_words[word]

    return None


# ============================================================
# CHECK CONFIRMATION
# ============================================================

def is_confirmation(message):

    message = message.lower().strip()

    confirmation_words = [
        "yes",
        "yes please",
        "yeah",
        "yep",
        "sure",
        "okay",
        "ok",
        "confirm",
        "place order",
        "buy it",
        "i want it",
        "i'll take it"
    ]

    return message in confirmation_words


# ============================================================
# CHECK NEGATIVE RESPONSE
# ============================================================

def is_negative(message):

    message = message.lower().strip()

    negative_words = [
        "no",
        "no thanks",
        "cancel",
        "not now",
        "don't"
    ]

    return message in negative_words


# ============================================================
# LOCAL COMMERCE AGENT
# ============================================================

def local_commerce_agent(
    message,
    conversation_state=None
):

    if conversation_state is None:

        conversation_state = {}


    message_lower = message.lower().strip()


    # ========================================================
    # ORDER PLACEMENT STATE
    # ========================================================

    order_state = conversation_state.get(
        "order_state"
    )


    # --------------------------------------------------------
    # CUSTOMER IS CONFIRMING PRODUCT
    # --------------------------------------------------------

    if order_state == "waiting_confirmation":

        if is_confirmation(message):

            conversation_state["order_state"] = (
                "waiting_customer_id"
            )

            return (
                f"Great! You selected "
                f"**{conversation_state['product_name']}**.\n\n"
                f"Price: ₹{conversation_state['product_price']}\n"
                f"Quantity: {conversation_state['quantity']}\n\n"
                f"Please provide your **Customer ID** "
                f"to place the order."
            )


        if is_negative(message):

            conversation_state.clear()

            return (
                "No problem. I have cancelled "
                "the order process."
            )


        return (
            "Please confirm whether you would like "
            "to place the order.\n\n"
            "You can say **Yes** or **No**."
        )


    # --------------------------------------------------------
    # CUSTOMER ID
    # --------------------------------------------------------

    if order_state == "waiting_customer_id":

        customer_id = message.strip().upper()


        # Basic validation

        if not customer_id.startswith("C"):

            return (
                "Please provide a valid Customer ID, "
                "for example **C001**."
            )


        product_id = conversation_state[
            "product_id"
        ]

        quantity = conversation_state[
            "quantity"
        ]


        # Check stock again before creating order

        products = search_products(
            category=None
        )

        selected_product = None

        for product in products:

            if product["product_id"] == product_id:

                selected_product = product
                break


        if selected_product is None:

            conversation_state.clear()

            return (
                "Sorry, I could not find that product "
                "in the database."
            )


        if selected_product["stock"] < quantity:

            conversation_state.clear()

            return (
                "Sorry, there is not enough stock "
                "for this product."
            )


        # Create order

        result = create_order(
            customer_id=customer_id,
            product_id=product_id,
            quantity=quantity
        )


        print(
            "DEBUG - Create order result:",
            result
        )


        if not result.get("success"):

            return result.get(
                "message",
                "Unable to create the order."
            )


        order_id = result.get(
            "order_id",
            "Unknown"
        )


        amount = result.get(
            "amount",
            selected_product["price"] * quantity
        )


        # Clear order state

        conversation_state.clear()


        return (
            "🎉 **Order placed successfully!**\n\n"

            f"- **Order ID:** {order_id}\n"
            f"- **Customer ID:** {customer_id}\n"
            f"- **Product:** {selected_product['name']}\n"
            f"- **Quantity:** {quantity}\n"
            f"- **Amount:** ₹{amount}\n\n"

            "Thank you for your order!"
        )


    # ========================================================
    # ORDER STATUS
    # ========================================================

    if (
        "where is my order" in message_lower
        or "order status" in message_lower
        or "track my order" in message_lower
        or "where is the order" in message_lower
        or "track order" in message_lower
    ):

        order_id = extract_order_id(message)

        print(
            "DEBUG - Extracted order ID:",
            order_id
        )


        if not order_id:

            return "Please provide your order ID."


        result = get_order_status(order_id)


        print(
            "DEBUG - Order database result:",
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
    # CANCEL ORDER
    # ========================================================

    if "cancel" in message_lower:

        order_id = extract_order_id(message)


        print(
            "DEBUG - Extracted order ID:",
            order_id
        )


        if not order_id:

            return "Please provide your order ID."


        result = cancel_order(order_id)


        print(
            "DEBUG - Cancel database result:",
            result
        )


        return result.get(
            "message",
            "Unable to cancel the order."
        )


    # ========================================================
    # RETURN STATUS
    # ========================================================

    if (
        "return status" in message_lower
        or "return update" in message_lower
        or "status of my return" in message_lower
        or "return request" in message_lower
    ):

        order_id = extract_order_id(message)


        print(
            "DEBUG - Extracted return order ID:",
            order_id
        )


        if not order_id:

            return "Please provide your order ID."


        result = get_return_by_order(order_id)


        print(
            "DEBUG - Return database result:",
            result
        )


        if not result.get("success"):

            return result.get(
                "message",
                "No return request was found."
            )


        return (
            f"Your return request for order "
            f"**{result['order_id']}** is currently "
            f"**{result['status']}**.\n\n"

            f"- Return ID: {result['return_id']}\n"
            f"- Reason: {result['reason']}"
        )


    # ========================================================
    # RETURN REQUEST
    # ========================================================

    if "return" in message_lower:

        order_id = extract_order_id(message)


        if not order_id:

            return "Please provide your order ID."


        return (
            f"I can help you with the return for "
            f"**{order_id}**.\n\n"
            f"Please provide the reason for the return."
        )


    # ========================================================
    # PRODUCT SEARCH / ORDER START
    # ========================================================

    if (
        "dress" in message_lower
        or "shirt" in message_lower
        or "shoe" in message_lower
        or "shoes" in message_lower
    ):

        category = None


        if "dress" in message_lower:

            category = "Dress"

        elif "shirt" in message_lower:

            category = "Shirt"

        elif (
            "shoe" in message_lower
            or "shoes" in message_lower
        ):

            category = "Shoes"


        results = search_products(
            category=category
        )


        print(
            "DEBUG - Product database result:",
            results
        )


        if not results:

            return (
                "Sorry, I couldn't find "
                "matching products."
            )


        # ----------------------------------------------------
        # If customer wants to BUY / ORDER
        # ----------------------------------------------------

        wants_to_buy = any(
            phrase in message_lower
            for phrase in [
                "buy",
                "purchase",
                "order",
                "want",
                "get"
            ]
        )


        if wants_to_buy:

            # Use first matching product
            # for the local demo

            product = results[0]


            quantity = extract_quantity(message)

            if quantity is None:

                quantity = 1


            if product["stock"] < quantity:

                return (
                    f"Sorry, only "
                    f"{product['stock']} items are "
                    f"available."
                )


            conversation_state[
                "order_state"
            ] = "waiting_confirmation"


            conversation_state[
                "product_id"
            ] = product["product_id"]


            conversation_state[
                "product_name"
            ] = product["name"]


            conversation_state[
                "product_price"
            ] = product["price"]


            conversation_state[
                "quantity"
            ] = quantity


            return (
                f"I found this product for you:\n\n"

                f"**{product['name']}**\n\n"
                f"- Price: ₹{product['price']}\n"
                f"- Color: {product['color']}\n"
                f"- Size: {product['size']}\n"
                f"- Stock: {product['stock']}\n"
                f"- Rating: {product['rating']}/5\n\n"

                f"Would you like to place an order "
                f"for **{quantity}** item(s)?"
            )


        # ----------------------------------------------------
        # Normal product search
        # ----------------------------------------------------

        response = (
            "Here are the available products:\n\n"
        )


        for product in results:

            response += (
                f"**{product['name']}**\n"
                f"Price: ₹{product['price']}\n"
                f"Color: {product['color']}\n"
                f"Size: {product['size']}\n"
                f"Stock: {product['stock']}\n"
                f"Rating: {product['rating']}/5\n\n"
            )


        return response


    # ========================================================
    # DEFAULT RESPONSE
    # ========================================================

    return (
        "I can help you with:\n\n"
        "🛍️ Product search\n"
        "🛒 Place an order\n"
        "📦 Order tracking\n"
        "❌ Order cancellation\n"
        "↩️ Return requests"
    )


# ============================================================
# COMMAND LINE TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("AI COMMERCE COPILOT - LOCAL AGENT")
    print("=" * 60)


    conversation_state = {}


    while True:

        message = input("\nCustomer: ")


        if message.lower().strip() in [
            "exit",
            "quit"
        ]:

            print("\nAgent stopped.")
            break


        response = local_commerce_agent(
            message,
            conversation_state
        )


        print("\nAI Commerce Copilot:")
        print(response)