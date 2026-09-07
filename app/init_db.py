from .database import engine, Base
from .models import (
    Product,
    Inventory,
    Bill,
    BillItem,
    KhataCustomer,
    KhataTransaction,
    Preference,
)


def initialize_database():
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")


if __name__ == "__main__":
    initialize_database()