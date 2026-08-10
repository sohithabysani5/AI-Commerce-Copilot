from tools.product_tools import search_products

from tools.orders_tools import (
    get_order_status,
    get_customer_orders,
    cancel_order,
    create_order,
)

from tools.return_tools import (
    create_return,
    get_return_status,
    get_return_by_order,
)


print("=" * 60)
print("AI COMMERCE COPILOT - BACKEND TEST")
print("=" * 60)


# ============================================================
# 1. PRODUCT SEARCH
# ============================================================

print("\n[1] PRODUCT SEARCH")
print("-" * 60)

result = search_products(
    category="Dress",
    color="Black",
    max_price=2000
)

print(result)


# ============================================================
# 2. ORDER STATUS
# ============================================================

print("\n[2] ORDER STATUS")
print("-" * 60)

result = get_order_status("ORD001")

print(result)


# ============================================================
# 3. CUSTOMER ORDERS
# ============================================================

print("\n[3] CUSTOMER ORDERS")
print("-" * 60)

result = get_customer_orders("C001")

print(result)


# ============================================================
# 4. RETURN BY ORDER
# ============================================================

print("\n[4] RETURN BY ORDER")
print("-" * 60)

result = get_return_by_order("ORD004")

print(result)


# ============================================================
# 5. RETURN STATUS
# ============================================================

print("\n[5] RETURN STATUS")
print("-" * 60)

# Replace this with the actual return ID from your database
result = get_return_status("RET20260809132757")

print(result)


print("\n" + "=" * 60)
print("BACKEND TEST FINISHED")
print("=" * 60)