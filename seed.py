from decimal import Decimal

from app.database import SessionLocal
from app.models import Product, Inventory


PRODUCTS = [
    {
        "sku": "AASHI-ATTA-5KG",
        "name": "Aashirvaad Atta 5kg",
        "brand": "Aashirvaad",
        "unit": "packet",
        "is_loose": False,
        "cost_price": Decimal("240.00"),
        "sell_price": Decimal("260.00"),
        "mrp": Decimal("270.00"),
        "gst_rate": Decimal("5.00"),
        "hsn_code": "11010000",
        "reorder_level": Decimal("10"),
        "quantity": Decimal("20"),
    },
    {
        "sku": "TATA-SALT-1KG",
        "name": "Tata Salt 1kg",
        "brand": "Tata",
        "unit": "packet",
        "is_loose": False,
        "cost_price": Decimal("22.00"),
        "sell_price": Decimal("25.00"),
        "mrp": Decimal("28.00"),
        "gst_rate": Decimal("0.00"),
        "hsn_code": "25010010",
        "reorder_level": Decimal("20"),
        "quantity": Decimal("50"),
    },
    {
        "sku": "AMUL-BUTTER-100G",
        "name": "Amul Butter 100g",
        "brand": "Amul",
        "unit": "packet",
        "is_loose": False,
        "cost_price": Decimal("52.00"),
        "sell_price": Decimal("58.00"),
        "mrp": Decimal("60.00"),
        "gst_rate": Decimal("12.00"),
        "hsn_code": "04051000",
        "reorder_level": Decimal("10"),
        "quantity": Decimal("25"),
    },
    {
        "sku": "FORTUNE-OIL-1L",
        "name": "Fortune Sunflower Oil 1L",
        "brand": "Fortune",
        "unit": "litre",
        "is_loose": False,
        "cost_price": Decimal("110.00"),
        "sell_price": Decimal("125.00"),
        "mrp": Decimal("130.00"),
        "gst_rate": Decimal("5.00"),
        "hsn_code": "15121910",
        "reorder_level": Decimal("10"),
        "quantity": Decimal("30"),
    },
    {
        "sku": "MAGGI-70G",
        "name": "Maggi 70g",
        "brand": "Nestle",
        "unit": "packet",
        "is_loose": False,
        "cost_price": Decimal("11.00"),
        "sell_price": Decimal("14.00"),
        "mrp": Decimal("14.00"),
        "gst_rate": Decimal("12.00"),
        "hsn_code": "19023010",
        "reorder_level": Decimal("20"),
        "quantity": Decimal("60"),
    },
    {
        "sku": "PARLE-G",
        "name": "Parle-G",
        "brand": "Parle",
        "unit": "packet",
        "is_loose": False,
        "cost_price": Decimal("5.00"),
        "sell_price": Decimal("5.00"),
        "mrp": Decimal("5.00"),
        "gst_rate": Decimal("0.00"),
        "hsn_code": "19053100",
        "reorder_level": Decimal("20"),
        "quantity": Decimal("50"),
    },
    {
        "sku": "SURF-EXCEL",
        "name": "Surf Excel",
        "brand": "Surf Excel",
        "unit": "packet",
        "is_loose": False,
        "cost_price": Decimal("90.00"),
        "sell_price": Decimal("105.00"),
        "mrp": Decimal("110.00"),
        "gst_rate": Decimal("18.00"),
        "hsn_code": "34022090",
        "reorder_level": Decimal("10"),
        "quantity": Decimal("20"),
    },
]


def seed_database():
    db = SessionLocal()

    try:
        for data in PRODUCTS:
            quantity = data.pop("quantity")

            existing = (
                db.query(Product)
                .filter(Product.sku == data["sku"])
                .first()
            )

            if existing:
                print(f"Already exists: {data['name']}")
                continue

            product = Product(**data)

            db.add(product)
            db.flush()

            inventory = Inventory(
                product_id=product.id,
                quantity=quantity
            )

            db.add(inventory)

            print(f"Added: {product.name}")

        db.commit()
        print("\nProducts seeded successfully!")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()