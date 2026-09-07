from app.tools.billing import create_bill
from app.tools.billing import add_bill_item
from app.tools.billing import finalize_bill


print("\n--- CREATE BILL ---")

bill = create_bill()
print(bill)

if not bill["success"]:
    raise SystemExit("Bill creation failed.")

bill_id = bill["bill_id"]


print("\n--- ADD PRODUCT ---")

item = add_bill_item(
    bill_id=bill_id,
    product_id=1,
    quantity=1,
)

print(item)

if not item["success"]:
    raise SystemExit("Adding product failed.")


print("\n--- FINALIZE BILL ---")

result = finalize_bill(
    bill_id=bill_id,
    payment_mode="UPI",
    payment_reference="TEST-UPI-001",
)

print(result)


print("\n--- DONE ---")