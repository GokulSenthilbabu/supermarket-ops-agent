from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
)

from sqlalchemy.orm import relationship

from .database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    sku = Column(String(100), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    brand = Column(String(100))
    unit = Column(String(30), nullable=False)
    is_loose = Column(Boolean, default=False)

    cost_price = Column(Numeric(10, 2), nullable=False)
    sell_price = Column(Numeric(10, 2), nullable=False)
    mrp = Column(Numeric(10, 2), nullable=False)

    gst_rate = Column(Numeric(5, 2), nullable=False)
    hsn_code = Column(String(20), nullable=False)

    reorder_level = Column(Numeric(10, 3), default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    inventory = relationship(
        "Inventory",
        back_populates="product",
        uselist=False
    )


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True)
    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        unique=True,
        nullable=False
    )

    quantity = Column(Numeric(10, 3), default=0)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    product = relationship(
        "Product",
        back_populates="inventory"
    )


class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True)
    bill_number = Column(String(50), unique=True, nullable=False)

    status = Column(String(20), default="DRAFT")

    subtotal = Column(Numeric(12, 2), default=0)
    cgst = Column(Numeric(12, 2), default=0)
    sgst = Column(Numeric(12, 2), default=0)
    igst = Column(Numeric(12, 2), default=0)
    grand_total = Column(Numeric(12, 2), default=0)

    payment_mode = Column(String(20))
    payment_reference = Column(String(200))

    idempotency_key = Column(String(200), unique=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    finalized_at = Column(DateTime)

    items = relationship(
        "BillItem",
        back_populates="bill",
        cascade="all, delete-orphan"
    )


class BillItem(Base):
    __tablename__ = "bill_items"

    id = Column(Integer, primary_key=True)

    bill_id = Column(
        Integer,
        ForeignKey("bills.id"),
        nullable=False
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )

    quantity = Column(Numeric(10, 3), nullable=False)

    unit_price = Column(Numeric(10, 2), nullable=False)
    cost_price = Column(Numeric(10, 2), nullable=False)

    gst_rate = Column(Numeric(5, 2), nullable=False)
    hsn_code = Column(String(20), nullable=False)

    taxable_amount = Column(Numeric(12, 2), default=0)
    cgst = Column(Numeric(12, 2), default=0)
    sgst = Column(Numeric(12, 2), default=0)
    total = Column(Numeric(12, 2), default=0)

    bill = relationship(
        "Bill",
        back_populates="items"
    )


class KhataCustomer(Base):
    __tablename__ = "khata_customers"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    phone = Column(String(30))

    created_at = Column(DateTime, default=datetime.utcnow)

    transactions = relationship(
        "KhataTransaction",
        back_populates="customer",
        cascade="all, delete-orphan"
    )


class KhataTransaction(Base):
    __tablename__ = "khata_transactions"

    id = Column(Integer, primary_key=True)

    customer_id = Column(
        Integer,
        ForeignKey("khata_customers.id"),
        nullable=False
    )

    transaction_type = Column(
        String(20),
        nullable=False
    )

    amount = Column(
        Numeric(12, 2),
        nullable=False
    )

    bill_id = Column(Integer, ForeignKey("bills.id"))
    note = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship(
        "KhataCustomer",
        back_populates="transactions"
    )


class Preference(Base):
    __tablename__ = "preferences"

    id = Column(Integer, primary_key=True)

    owner_id = Column(
        String(100),
        nullable=False
    )

    key = Column(
        String(100),
        nullable=False
    )

    value = Column(Text)

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )