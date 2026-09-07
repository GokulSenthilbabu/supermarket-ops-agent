from decimal import Decimal

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Bill, BillItem, Product, Inventory
from app.services.gst import calculate_gst, money
from app.tools.invoice_pdf import generate_invoice_pdf


# =========================================================
# CREATE BILL
# =========================================================

def create_bill():
    db = SessionLocal()

    try:
        bill = Bill(
            bill_number=f"BILL-{__import__('uuid').uuid4().hex[:8].upper()}",
            status="DRAFT",
            subtotal=Decimal("0.00"),
            cgst=Decimal("0.00"),
            sgst=Decimal("0.00"),
            igst=Decimal("0.00"),
            grand_total=Decimal("0.00"),
        )

        db.add(bill)
        db.commit()
        db.refresh(bill)

        return {
            "success": True,
            "bill_id": bill.id,
            "bill_number": bill.bill_number,
            "status": bill.status,
        }

    except Exception as exc:
        db.rollback()

        return {
            "success": False,
            "error": str(exc),
        }

    finally:
        db.close()


# =========================================================
# ADD BILL ITEM
# =========================================================

def add_bill_item(
    bill_id: int,
    product_id: int,
    quantity: float,
):
    db = SessionLocal()

    try:
        quantity = Decimal(str(quantity))

        if quantity <= 0:
            return {
                "success": False,
                "error": "Quantity must be greater than zero.",
            }

        bill = db.get(Bill, bill_id)

        if not bill:
            return {
                "success": False,
                "error": "Bill not found.",
            }

        if bill.status != "DRAFT":
            return {
                "success": False,
                "error": "Only draft bills can be edited.",
            }

        product = db.get(Product, product_id)

        if not product:
            return {
                "success": False,
                "error": "Product not found.",
            }

        inventory = db.execute(
            select(Inventory).where(
                Inventory.product_id == product_id
            )
        ).scalar_one_or_none()

        if not inventory:
            return {
                "success": False,
                "error": "Inventory record not found.",
            }

        current_stock = Decimal(str(inventory.quantity))

        # -------------------------------------------------
        # Check existing quantity already present
        # -------------------------------------------------

        existing_items = db.execute(
            select(BillItem).where(
                BillItem.bill_id == bill_id,
                BillItem.product_id == product_id,
            )
        ).scalars().all()

        existing_quantity = sum(
            Decimal(str(item.quantity))
            for item in existing_items
        )

        total_requested = existing_quantity + quantity

        # -------------------------------------------------
        # Oversell protection during draft building
        # -------------------------------------------------

        if total_requested > current_stock:
            return {
                "success": False,
                "error": (
                    f"Insufficient stock for {product.name}. "
                    f"Available: {current_stock}, "
                    f"already in bill: {existing_quantity}, "
                    f"requested additional: {quantity}."
                ),
            }

        # -------------------------------------------------
        # Never sell below cost
        # -------------------------------------------------

        cost_price = Decimal(str(product.cost_price))
        sell_price = Decimal(str(product.sell_price))

        if sell_price < cost_price:
            return {
                "success": False,
                "error": (
                    f"Cannot sell {product.name} below cost price. "
                    f"Cost: ₹{money(cost_price)}, "
                    f"Selling price: ₹{money(sell_price)}."
                ),
            }

        item = BillItem(
            bill_id=bill_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=sell_price,
            cost_price=cost_price,
            gst_rate=Decimal(str(product.gst_rate)),
            hsn_code=product.hsn_code,
        )

        db.add(item)
        db.commit()
        db.refresh(item)

        return {
            "success": True,
            "bill_id": bill.id,
            "bill_number": bill.bill_number,
            "item_id": item.id,
            "product": product.name,
            "quantity_added": float(quantity),
            "total_quantity_in_bill": float(total_requested),
            "available_stock": float(current_stock),
            "status": bill.status,
        }

    except Exception as exc:
        db.rollback()

        return {
            "success": False,
            "error": str(exc),
        }

    finally:
        db.close()


# =========================================================
# GET CURRENT BILL
# =========================================================

def get_current_bill(bill_id: int):
    db = SessionLocal()

    try:
        bill = db.get(Bill, bill_id)

        if not bill:
            return {
                "success": False,
                "error": "Bill not found.",
            }

        result_items = []

        for item in bill.items:
            product = db.get(Product, item.product_id)

            result_items.append({
                "item_id": item.id,
                "product_id": item.product_id,
                "product": product.name if product else "Unknown",
                "quantity": float(item.quantity),
                "unit_price": float(item.unit_price),
                "gst_rate": float(item.gst_rate),
                "hsn_code": item.hsn_code,
            })

        return {
            "success": True,
            "bill_id": bill.id,
            "bill_number": bill.bill_number,
            "status": bill.status,
            "items": result_items,
        }

    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
        }

    finally:
        db.close()


# =========================================================
# REMOVE BILL ITEM
# =========================================================

def remove_bill_item(
    bill_id: int,
    item_id: int,
):
    db = SessionLocal()

    try:
        bill = db.get(Bill, bill_id)

        if not bill:
            return {
                "success": False,
                "error": "Bill not found.",
            }

        if bill.status != "DRAFT":
            return {
                "success": False,
                "error": "Only draft bills can be edited.",
            }

        item = db.get(BillItem, item_id)

        if not item:
            return {
                "success": False,
                "error": "Bill item not found.",
            }

        if item.bill_id != bill_id:
            return {
                "success": False,
                "error": "This item does not belong to the specified bill.",
            }

        product = db.get(Product, item.product_id)

        product_name = product.name if product else "Unknown"

        db.delete(item)
        db.commit()

        return {
            "success": True,
            "message": f"{product_name} removed from the bill.",
            "bill_id": bill.id,
            "bill_number": bill.bill_number,
        }

    except Exception as exc:
        db.rollback()

        return {
            "success": False,
            "error": str(exc),
        }

    finally:
        db.close()


# =========================================================
# FINALIZE BILL
# =========================================================

def finalize_bill(
    bill_id: int,
    payment_mode: str,
    payment_reference: str | None = None,
):
    db = SessionLocal()

    try:
        payment_mode = payment_mode.upper().strip()

        if payment_mode not in {"CASH", "UPI", "CARD"}:
            return {
                "success": False,
                "error": "Payment mode must be CASH, UPI, or CARD.",
            }

        # -------------------------------------------------
        # Start SQLite write transaction
        # -------------------------------------------------

        db.connection().exec_driver_sql("BEGIN IMMEDIATE")

        bill = db.get(Bill, bill_id)

        if not bill:
            db.rollback()

            return {
                "success": False,
                "error": "Bill not found.",
            }

        # -------------------------------------------------
        # IDEMPOTENCY
        # -------------------------------------------------

        if bill.status == "FINALIZED":
            db.commit()

            return {
                "success": True,
                "already_finalized": True,
                "bill_id": bill.id,
                "bill_number": bill.bill_number,
                "subtotal": float(bill.subtotal),
                "cgst": float(bill.cgst),
                "sgst": float(bill.sgst),
                "igst": float(bill.igst),
                "grand_total": float(bill.grand_total),
                "payment_mode": bill.payment_mode,
                "payment_reference": bill.payment_reference,
            }

        if bill.status != "DRAFT":
            db.rollback()

            return {
                "success": False,
                "error": f"Bill cannot be finalized from status {bill.status}.",
            }

        if not bill.items:
            db.rollback()

            return {
                "success": False,
                "error": "Cannot finalize an empty bill.",
            }

        # =================================================
        # STEP 1: AGGREGATE REQUIRED STOCK
        # =================================================

        required_quantities = {}

        for item in bill.items:
            product_id = item.product_id

            required_quantities[product_id] = (
                required_quantities.get(
                    product_id,
                    Decimal("0")
                )
                + Decimal(str(item.quantity))
            )

        # =================================================
        # STEP 2: VALIDATE ALL STOCK BEFORE ANY DEDUCTION
        # =================================================

        for product_id, required_quantity in required_quantities.items():

            inventory = db.execute(
                select(Inventory)
                .where(Inventory.product_id == product_id)
            ).scalar_one_or_none()

            product = db.get(Product, product_id)

            if not product:
                db.rollback()

                return {
                    "success": False,
                    "error": f"Product {product_id} not found.",
                }

            if not inventory:
                db.rollback()

                return {
                    "success": False,
                    "error": f"Inventory missing for {product.name}.",
                }

            available_quantity = Decimal(
                str(inventory.quantity)
            )

            if required_quantity > available_quantity:
                db.rollback()

                return {
                    "success": False,
                    "error": (
                        f"Cannot finalize bill. "
                        f"Insufficient stock for {product.name}. "
                        f"Required: {required_quantity}, "
                        f"Available: {available_quantity}."
                    ),
                }

        # =================================================
        # STEP 3: VALIDATE PRICES
        # =================================================

        for item in bill.items:

            product = db.get(Product, item.product_id)

            cost_price = Decimal(str(product.cost_price))
            sell_price = Decimal(str(item.unit_price))

            if sell_price < cost_price:
                db.rollback()

                return {
                    "success": False,
                    "error": (
                        f"Cannot finalize bill because "
                        f"{product.name} is being sold below cost."
                    ),
                }

        # =================================================
        # STEP 4: CALCULATE GST
        # =================================================

        subtotal = Decimal("0.00")
        total_cgst = Decimal("0.00")
        total_sgst = Decimal("0.00")
        total_igst = Decimal("0.00")
        grand_total = Decimal("0.00")

        for item in bill.items:

            quantity = Decimal(str(item.quantity))
            unit_price = Decimal(str(item.unit_price))
            gst_rate = Decimal(str(item.gst_rate))

            taxable_amount = money(
                quantity * unit_price
            )

            gst_result = calculate_gst(
                taxable_amount,
                gst_rate,
            )

            item.taxable_amount = gst_result["taxable_amount"]
            item.cgst = gst_result["cgst"]
            item.sgst = gst_result["sgst"]
            item.total = gst_result["total"]

            subtotal += gst_result["taxable_amount"]
            total_cgst += gst_result["cgst"]
            total_sgst += gst_result["sgst"]
            total_igst += gst_result["igst"]
            grand_total += gst_result["total"]

        subtotal = money(subtotal)
        total_cgst = money(total_cgst)
        total_sgst = money(total_sgst)
        total_igst = money(total_igst)
        grand_total = money(grand_total)

        # =================================================
        # STEP 5: DEDUCT STOCK
        # =================================================

        for product_id, required_quantity in required_quantities.items():

            inventory = db.execute(
                select(Inventory)
                .where(Inventory.product_id == product_id)
            ).scalar_one()

            inventory.quantity = (
                Decimal(str(inventory.quantity))
                - required_quantity
            )

        # =================================================
        # STEP 6: UPDATE BILL
        # =================================================

        bill.subtotal = subtotal
        bill.cgst = total_cgst
        bill.sgst = total_sgst
        bill.igst = total_igst
        bill.grand_total = grand_total

        bill.payment_mode = payment_mode
        bill.payment_reference = payment_reference

        bill.status = "FINALIZED"

        from datetime import datetime

        bill.finalized_at = datetime.utcnow()

        # -------------------------------------------------
        # SAVE BILL
        # -------------------------------------------------

        db.commit()

        # =================================================
        # STEP 7: GENERATE PDF INVOICE
        # =================================================

        pdf_result = generate_invoice_pdf(bill.id)

        return {
            "success": True,
            "already_finalized": False,
            "bill_id": bill.id,
            "bill_number": bill.bill_number,
            "subtotal": float(subtotal),
            "cgst": float(total_cgst),
            "sgst": float(total_sgst),
            "igst": float(total_igst),
            "grand_total": float(grand_total),
            "payment_mode": payment_mode,
            "payment_reference": payment_reference,
            "status": "FINALIZED",
            "invoice_pdf": pdf_result,
        }

    except Exception as exc:
        db.rollback()

        return {
            "success": False,
            "error": str(exc),
        }

    finally:
        db.close()