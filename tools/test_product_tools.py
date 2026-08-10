from product_tools import search_products


results = search_products(
    category="Dress",
    color="Black",
    size="M",
    max_price=2000
)

print("\nMatching Products:\n")

if not results:
    print("No products found.")
else:
    for product in results:
        print(product)