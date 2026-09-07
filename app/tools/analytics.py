from datetime import datetime, date, time
from decimal import Decimal

from sqlalchemy import select, func

from app.database import SessionLocal
from app.models import Bill, BillItem, Product


def get_daily_sales(target_date=None):
    db = SessionLocal()

    try:
        if target_date is None:
            target_date = date.today()

        start = datetime.combine(target_date, time.min)
        end = datetime.combine(target_date, time.max)

        bills = db.execute(
            select(Bill).where(
                Bill.status == "FINALIZED",
                Bill.finalized_at >= start,
                Bill.finalized_at <= end,
            )
        ).scalars().all()

        total_sales = Decimal("0.00")
        total_cgst = Decimal("0.00")
        total_sgst = Decimal("0.00")
        total_igst = Decimal("0.00")

        cash = Decimal("0.00")
        upi = Decimal("0.00")
        card = Decimal("0.00")

        for bill in bills:
            total_sales += Decimal(str(bill.grand_total or 0))
            total_cgst += Decimal(str(bill.cgst or 0))
            total_sgst += Decimal(str(bill.sgst or 0))
            total_igst += Decimal(str(bill.igst or 0))

            mode = (bill.payment_mode or "").upper()

            if mode == "CASH":
                cash += Decimal(str(bill.grand_total or 0))

            elif mode == "UPI":
                upi += Decimal(str(bill.grand_total or 0))

            elif mode == "CARD":
                card += Decimal(str(bill.grand_total or 0))

        tax_collected = (
            total_cgst
            + total_sgst
            + total_igst
        )

        return {
            "success": True,
            "date": target_date.isoformat(),
            "bill_count": len(bills),
            "total_sales": float(total_sales),
            "tax_collected": float(tax_collected),
            "cgst": float(total_cgst),
            "sgst": float(total_sgst),
            "igst": float(total_igst),
            "cash": float(cash),
            "upi": float(upi),
            "card": float(card),
        }

    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
        }

    finally:
        db.close()


def get_top_items(target_date=None, limit=5):
    db = SessionLocal()

    try:
        if target_date is None:
            target_date = date.today()

        start = datetime.combine(target_date, time.min)
        end = datetime.combine(target_date, time.max)

        rows = db.execute(
            select(
                Product.name,
                func.sum(BillItem.quantity).label("quantity"),
                func.sum(BillItem.total).label("sales"),
            )
            .join(
                BillItem,
                BillItem.product_id == Product.id,
            )
            .join(
                Bill,
                Bill.id == BillItem.bill_id,
            )
            .where(
                Bill.status == "FINALIZED",
                Bill.finalized_at >= start,
                Bill.finalized_at <= end,
            )
            .group_by(Product.id, Product.name)
            .order_by(
                func.sum(BillItem.quantity).desc()
            )
            .limit(limit)
        ).all()

        items = []

        for row in rows:
            items.append({
                "product": row.name,
                "quantity": float(row.quantity or 0),
                "sales": float(row.sales or 0),
            })

        return {
            "success": True,
            "date": target_date.isoformat(),
            "items": items,
        }

    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
        }

    finally:
        db.close()


def get_daily_summary(target_date=None):
    sales = get_daily_sales(target_date)

    if not sales["success"]:
        return sales

    top_items = get_top_items(target_date)

    if not top_items["success"]:
        return top_items

    return {
        "success": True,
        "date": sales["date"],
        "sales": sales,
        "top_items": top_items["items"],
    }