from tools.orders_tools import create_order


result = create_order(
    customer_id="C001",
    product_id="P001",
    quantity=1
)

print("\nCreate Order Result:")
print(result)