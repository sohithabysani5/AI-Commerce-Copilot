import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

from tools.product_tools import search_products
from tools.orders_tools import (
    get_order_status,
    cancel_order,
    create_order,
)

load_dotenv()

# ============================================================
# GEMINI CLIENT
# ============================================================

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY was not found. Check your .env file."
    )

client = genai.Client(api_key=api_key)


# ============================================================
# PRODUCT SEARCH TOOL
# ============================================================

search_products_tool = types.FunctionDeclaration(
    name="search_products",
    description=(
        "Search the store product database. "
        "Use this when the customer wants to find products "
        "based on category, color, size, or maximum price."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "category": types.Schema(
                type=types.Type.STRING,
                description="Product category such as Dress, Shirt or Shoes."
            ),
            "color": types.Schema(
                type=types.Type.STRING,
                description="Product color such as Black, Red or Blue."
            ),
            "size": types.Schema(
                type=types.Type.STRING,
                description="Product size such as S, M, L or XL."
            ),
            "max_price": types.Schema(
                type=types.Type.NUMBER,
                description="Maximum price the customer wants to pay."
            ),
        },
    ),
)


# ============================================================
# GET ORDER STATUS TOOL
# ============================================================

get_order_status_tool = types.FunctionDeclaration(
    name="get_order_status",
    description=(
        "Get the current status and details of a customer's order."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "order_id": types.Schema(
                type=types.Type.STRING,
                description="Order ID such as ORD001."
            ),
        },
        required=["order_id"],
    ),
)


# ============================================================
# CANCEL ORDER TOOL
# ============================================================

cancel_order_tool = types.FunctionDeclaration(
    name="cancel_order",
    description=(
        "Cancel a customer's order if the order is eligible "
        "for cancellation."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "order_id": types.Schema(
                type=types.Type.STRING,
                description="Order ID such as ORD001."
            ),
        },
        required=["order_id"],
    ),
)


# ============================================================
# CREATE ORDER TOOL
# ============================================================

create_order_tool = types.FunctionDeclaration(
    name="create_order",
    description=(
        "Place a new order for a customer. "
        "Use this ONLY after the customer clearly confirms "
        "that they want to purchase the product."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "customer_id": types.Schema(
                type=types.Type.STRING,
                description="Customer ID such as C001."
            ),
            "product_id": types.Schema(
                type=types.Type.STRING,
                description="Product ID such as P001."
            ),
            "quantity": types.Schema(
                type=types.Type.INTEGER,
                description="Quantity the customer wants to order."
            ),
        },
        required=[
            "customer_id",
            "product_id",
            "quantity",
        ],
    ),
)


# ============================================================
# COMMERCE TOOLS
# ============================================================

commerce_tools = types.Tool(
    function_declarations=[
        search_products_tool,
        get_order_status_tool,
        cancel_order_tool,
        create_order_tool,
    ]
)


# ============================================================
# SYSTEM INSTRUCTION
# ============================================================

SYSTEM_INSTRUCTION = """
You are an AI Commerce Copilot for an online store.

You act as a helpful AI employee.

Your responsibilities:

- Help customers find products.
- Recommend products.
- Check order status.
- Cancel eligible orders.
- Place new orders.
- Answer customer questions.
- Never invent information.

PRODUCT SEARCH:
Use search_products whenever product information is required.

Never invent:
- Product names
- Prices
- Stock
- Ratings
- Product IDs

Only use information returned by the database.

ORDER STATUS:
When a customer asks about an order, use get_order_status.

Never guess an order status.

ORDER CANCELLATION:
When the customer clearly wants to cancel an order,
use cancel_order.

Never claim an order was cancelled unless the database
confirms it.

ORDER PLACEMENT:
Never place an order simply because the customer asks
about a product.

First search for the product.

Show the customer the product information.

Ask for confirmation.

Only place the order after clear confirmation.

Examples of clear confirmation:

"Yes, place the order."
"I want to buy it."
"Order one for me."
"Yes, I'll take it."
"Please order it."

Never invent a product ID.

Never invent an order ID.

The database generates the order ID.

CUSTOMER ID:
For this prototype, use C001 when no customer ID
is available.

QUANTITY:
Use the quantity specified by the customer.

If the quantity is not clear, ask the customer.

COMMUNICATION:
Be friendly, concise and natural.

You can understand English and mixed Telugu-English.

After successfully placing an order, tell the customer:

- Order ID
- Product
- Quantity
- Total amount
- Order status
"""


# ============================================================
# EXECUTE TOOL
# ============================================================

def execute_tool(function_name, function_args):

    print("\nTool selected by AI:", function_name)
    print("Tool arguments:", function_args)

    # --------------------------------------------------------
    # SEARCH PRODUCTS
    # --------------------------------------------------------

    if function_name == "search_products":

        result = search_products(
            category=function_args.get("category"),
            color=function_args.get("color"),
            size=function_args.get("size"),
            max_price=function_args.get("max_price"),
        )

        print("\nProduct database result:")
        print(result)

        return {
            "products": result
        }

    # --------------------------------------------------------
    # ORDER STATUS
    # --------------------------------------------------------

    elif function_name == "get_order_status":

        order_id = function_args.get("order_id")

        result = get_order_status(order_id)

        print("\nOrder database result:")
        print(result)

        return result

    # --------------------------------------------------------
    # CANCEL ORDER
    # --------------------------------------------------------

    elif function_name == "cancel_order":

        order_id = function_args.get("order_id")

        result = cancel_order(order_id)

        print("\nCancel order database result:")
        print(result)

        return result

    # --------------------------------------------------------
    # CREATE ORDER
    # --------------------------------------------------------

    elif function_name == "create_order":

        customer_id = function_args.get("customer_id")
        product_id = function_args.get("product_id")
        quantity = function_args.get("quantity")

        result = create_order(
            customer_id=customer_id,
            product_id=product_id,
            quantity=quantity,
        )

        print("\nCreate order database result:")
        print(result)

        return result

    # --------------------------------------------------------
    # UNKNOWN TOOL
    # --------------------------------------------------------

    return {
        "success": False,
        "message": f"Unknown tool: {function_name}"
    }


# ============================================================
# AI COMMERCE AGENT
# ============================================================

def ask_commerce_agent(user_message):

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=[commerce_tools],
        ),
    )

    # ========================================================
    # GEMINI WANTS TO USE A TOOL
    # ========================================================

    if response.function_calls:

        function_call = response.function_calls[0]

        function_name = function_call.name
        function_args = function_call.args

        # Execute Python/database function
        tool_result = execute_tool(
            function_name,
            function_args,
        )

        # Send result back to Gemini
        tool_response = types.Part.from_function_response(
            name=function_name,
            response=tool_result,
        )

        final_response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(
                            text=user_message
                        )
                    ],
                ),
                response.candidates[0].content,
                tool_response,
            ],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
            ),
        )

        return final_response.text

    # ========================================================
    # NORMAL AI RESPONSE
    # ========================================================

    return response.text