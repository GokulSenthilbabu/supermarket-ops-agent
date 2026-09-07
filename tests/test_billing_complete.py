from app.tools.billing import (
    create_bill,
    add_bill_item,
    finalize_bill,
)

from app.database import SessionLocal
from app.models import Product


def find_product(name):
    db = SessionLocal()

    try:
        product = db.query(Product).filter(Product.name == name).first()

        if not product:
            raise SystemExit(f"Product not found: {name}")

        return product.id

    finally:
        db.close()


def main():

    print("\n=== COMPLETE BILLING TEST ===")

    # -----------------------------------------
    # 1. FIND PRODUCT
    # -----------------------------------------

    print("\n--- FIND PRODUCT ---")

    product_id = find_product("Aashirvaad Atta 5kg")

    print("Product ID:", product_id)

    # -----------------------------------------
    # 2. CREATE BILL
    # -----------------------------------------

    print("\n--- CREATE BILL ---")

    result = create_bill()

    print(result)

    if not result["success"]:
        raise SystemExit("Create bill failed.")

    bill_id = result["bill_id"]

    print("Bill ID:", bill_id)

    # -----------------------------------------
    # 3. ADD PRODUCT
    # -----------------------------------------

    print("\n--- ADD PRODUCT ---")

    result = add_bill_item(
        bill_id=bill_id,
        product_id=product_id,
        quantity=1,
    )

    print(result)

    if not result["success"]:
        raise SystemExit("Add product failed.")

    # -----------------------------------------
    # 4. FINALIZE FIRST TIME
    # -----------------------------------------

    print("\n--- FIRST FINALIZE ---")

    first = finalize_bill(
        bill_id=bill_id,
        payment_mode="UPI",
        payment_reference="TEST-IDEMPOTENCY-001",
    )

    print(first)

    if not first["success"]:
        raise SystemExit("First finalization failed.")

    if first.get("already_finalized"):
        raise SystemExit(
            "ERROR: First finalize incorrectly reported already_finalized."
        )

    # -----------------------------------------
    # 5. FINALIZE SECOND TIME
    # -----------------------------------------

    print("\n--- SECOND FINALIZE ---")

    second = finalize_bill(
        bill_id=bill_id,
        payment_mode="UPI",
        payment_reference="TEST-IDEMPOTENCY-001",
    )

    print(second)

    if not second["success"]:
        raise SystemExit("Second finalization failed.")

    # -----------------------------------------
    # 6. IDEMPOTENCY CHECK
    # -----------------------------------------

    print("\n--- IDEMPOTENCY CHECK ---")

    if not second.get("already_finalized"):
        raise SystemExit(
            "ERROR: Second finalize did not report already_finalized."
        )

    print("PASS: Bill was not finalized twice.")

    # -----------------------------------------
    # DONE
    # -----------------------------------------

    print("\n=== TEST PASSED ===")


if __name__ == "__main__":
    main()