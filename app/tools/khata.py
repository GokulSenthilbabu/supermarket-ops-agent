from decimal import Decimal
from app.database import SessionLocal
from app.models import KhataCustomer, KhataTransaction


def get_or_create_customer(name: str, phone: str = None):
    """Find a customer or create a new khata customer."""

    db = SessionLocal()

    try:
        customer = (
            db.query(KhataCustomer)
            .filter(KhataCustomer.name.ilike(name.strip()))
            .first()
        )

        if customer:
            return {
                "success": True,
                "customer_id": customer.id,
                "name": customer.name,
                "phone": customer.phone,
                "created": False,
            }

        customer = KhataCustomer(
            name=name.strip(),
            phone=phone,
        )

        db.add(customer)
        db.commit()
        db.refresh(customer)

        return {
            "success": True,
            "customer_id": customer.id,
            "name": customer.name,
            "phone": customer.phone,
            "created": True,
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def add_credit(
    customer_name: str,
    amount: float,
    note: str = None,
    bill_id: int = None
):
    """Add an amount to a customer's khata balance."""

    if amount <= 0:
        return {
            "success": False,
            "error": "Credit amount must be greater than zero"
        }

    customer_result = get_or_create_customer(customer_name)

    if not customer_result["success"]:
        return customer_result

    db = SessionLocal()

    try:
        customer = (
            db.query(KhataCustomer)
            .filter(
                KhataCustomer.id
                == customer_result["customer_id"]
            )
            .first()
        )

        transaction = KhataTransaction(
            customer_id=customer.id,
            transaction_type="CREDIT",
            amount=Decimal(str(amount)),
            bill_id=bill_id,
            note=note,
        )

        db.add(transaction)
        db.commit()

        balance = calculate_balance(db, customer.id)

        return {
            "success": True,
            "customer": customer.name,
            "transaction_type": "CREDIT",
            "amount": float(amount),
            "balance": float(balance),
            "message": (
                f"₹{amount:.2f} added to "
                f"{customer.name}'s khata."
            ),
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def record_payment(
    customer_name: str,
    amount: float,
    note: str = None
):
    """Record a customer payment against khata."""

    if amount <= 0:
        return {
            "success": False,
            "error": "Payment amount must be greater than zero"
        }

    customer_result = get_or_create_customer(customer_name)

    if not customer_result["success"]:
        return customer_result

    db = SessionLocal()

    try:
        customer = (
            db.query(KhataCustomer)
            .filter(
                KhataCustomer.id
                == customer_result["customer_id"]
            )
            .first()
        )

        current_balance = calculate_balance(
            db,
            customer.id
        )

        payment = Decimal(str(amount))

        if payment > current_balance:
            return {
                "success": False,
                "error": (
                    f"Payment of ₹{payment:.2f} exceeds "
                    f"outstanding balance of "
                    f"₹{current_balance:.2f}"
                ),
            }

        transaction = KhataTransaction(
            customer_id=customer.id,
            transaction_type="PAYMENT",
            amount=payment,
            note=note,
        )

        db.add(transaction)
        db.commit()

        new_balance = calculate_balance(
            db,
            customer.id
        )

        return {
            "success": True,
            "customer": customer.name,
            "transaction_type": "PAYMENT",
            "amount": float(payment),
            "balance": float(new_balance),
            "message": (
                f"₹{payment:.2f} payment recorded for "
                f"{customer.name}."
            ),
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def calculate_balance(db, customer_id: int):
    """Calculate outstanding khata balance."""

    transactions = (
        db.query(KhataTransaction)
        .filter(
            KhataTransaction.customer_id
            == customer_id
        )
        .all()
    )

    balance = Decimal("0.00")

    for transaction in transactions:

        if transaction.transaction_type == "CREDIT":
            balance += Decimal(str(transaction.amount))

        elif transaction.transaction_type == "PAYMENT":
            balance -= Decimal(str(transaction.amount))

    return balance


def get_balance(customer_name: str):
    """Get customer's current outstanding balance."""

    db = SessionLocal()

    try:
        customer = (
            db.query(KhataCustomer)
            .filter(
                KhataCustomer.name.ilike(
                    customer_name.strip()
                )
            )
            .first()
        )

        if not customer:
            return {
                "success": False,
                "error": "Customer not found in khata"
            }

        balance = calculate_balance(
            db,
            customer.id
        )

        return {
            "success": True,
            "customer": customer.name,
            "balance": float(balance),
        }

    finally:
        db.close()