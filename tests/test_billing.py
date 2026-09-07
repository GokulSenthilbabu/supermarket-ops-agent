from app.tools.inventory import search_products, get_stock
from app.tools.billing import (
    create_bill,
    add_bill_item,
    get_current_bill,
    finalize_bill,
)


print("\n--- CREATE BILL ---")

bill = create_bill()
print(bill)

bill_id = bill["bill_id"]

print("\n--- FIND MAGGI ---")

result = search_products("Maggi")

print(result)

if not result["success"]:
    raise SystemExit("Search failed.")

products = result["products"]

if not products:
    raise SystemExit("Maggi not found.")

maggi = products[0]

print(maggi)


print("\n--- STOCK BEFORE BILL ---")

before = get_stock(maggi["id"])
print(before)

stock_before = before["quantity"]


print("\n--- ADD 2 MAGGI ---")

item = add_bill_item(
    bill_id=bill_id,
    product_id=maggi["id"],
    quantity=2
)

print(item)


print("\n--- CURRENT BILL ---")

current_bill = get_current_bill(bill_id)
print(current_bill)


print("\n--- FINALIZE BILL WITH UPI ---")

finalized = finalize_bill(
    bill_id=bill_id,
    payment_mode="UPI",
    payment_reference="UPI-DEMO-001"
)

print(finalized)


print("\n--- STOCK AFTER FINALIZATION ---")

after = get_stock(maggi["id"])
print(after)

stock_after = after["quantity"]


print("\n--- STOCK CHECK ---")

print(
    f"Stock before: {stock_before}"
)

print(
    f"Stock after: {stock_after}"
)

print(
    f"Stock deducted: {stock_before - stock_after}"
)


print("\n--- TRY FINALIZING SAME BILL AGAIN ---")

second_attempt = finalize_bill(
    bill_id=bill_id,
    payment_mode="UPI",
    payment_reference="UPI-DEMO-001"
)

print(second_attempt)


print("\n--- FINAL STOCK CHECK ---")

final_stock = get_stock(maggi["id"])
print(final_stock)