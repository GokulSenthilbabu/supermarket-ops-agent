from app.tools.inventory import (
    search_products,
    get_stock,
    receive_stock,
    get_low_stock,
)


print("\n--- SEARCH MAGGI ---")

result = search_products("Maggi")

print(result)

if not result["success"]:
    raise SystemExit("Search failed.")

products = result["products"]

if not products:
    raise SystemExit("Maggi not found.")

for product in products:
    print(product)


print("\n--- CHECK MAGGI STOCK ---")

maggi = products[0]

stock = get_stock(maggi["id"])

print(stock)


print("\n--- RECEIVE MAGGI STOCK ---")

received = receive_stock(maggi["id"], 10)

print(received)


print("\n--- CHECK MAGGI STOCK AGAIN ---")

stock = get_stock(maggi["id"])

print(stock)


print("\n--- LOW STOCK PRODUCTS ---")

low_stock = get_low_stock()

print(low_stock)

if low_stock["success"]:
    for product in low_stock["low_stock_products"]:
        print(product)