from return_tools import create_return_request


result = create_return_request(
    "ORD004",
    "Product is not suitable"
)

print("\nReturn Request:\n")
print(result)