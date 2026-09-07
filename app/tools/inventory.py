from decimal import Decimal

from sqlalchemy import select, or_

from app.database import SessionLocal
from app.models import Product, Inventory


# =========================================================
# SEARCH PRODUCTS
# =========================================================

def search_products(query: str):
    db = SessionLocal()

    try:
        query = query.strip()

        if not query:
            return {
                "success": False,
                "error": "Search query cannot be empty."
            }

        search_term = f"%{query}%"

        products = db.execute(
            select(Product).where(
                or_(
                    Product.name.ilike(search_term),
                    Product.brand.ilike(search_term),
                    Product.sku.ilike(search_term),
                )
            )
        ).scalars().all()

        results = []

        for product in products:

            inventory = db.execute(
                select(Inventory).where(
                    Inventory.product_id == product.id
                )
            ).scalar_one_or_none()

            stock = (
                float(inventory.quantity)
                if inventory
                else 0.0
            )

            results.append({
                "id": product.id,
                "sku": product.sku,
                "name": product.name,
                "brand": product.brand,
                "unit": product.unit,
                "stock": stock,
                "sell_price": float(product.sell_price),
                "mrp": float(product.mrp),
                "gst_rate": float(product.gst_rate),
                "hsn_code": product.hsn_code,
            })

        return {
            "success": True,
            "count": len(results),
            "products": results,
        }

    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
        }

    finally:
        db.close()


# =========================================================
# GET STOCK
# =========================================================

def get_stock(product_id: int):
    db = SessionLocal()

    try:
        product = db.get(Product, product_id)

        if not product:
            return {
                "success": False,
                "error": "Product not found."
            }

        inventory = db.execute(
            select(Inventory).where(
                Inventory.product_id == product_id
            )
        ).scalar_one_or_none()

        if not inventory:
            return {
                "success": False,
                "error": "Inventory record not found."
            }

        return {
            "success": True,
            "product": product.name,
            "sku": product.sku,
            "unit": product.unit,
            "quantity": float(inventory.quantity),
            "reorder_level": float(product.reorder_level),
        }

    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
        }

    finally:
        db.close()


# =========================================================
# RECEIVE STOCK
# =========================================================

def receive_stock(product_id: int, quantity: float):
    db = SessionLocal()

    try:
        quantity = Decimal(str(quantity))

        if quantity <= 0:
            return {
                "success": False,
                "error": "Received quantity must be greater than zero."
            }

        product = db.get(Product, product_id)

        if not product:
            return {
                "success": False,
                "error": "Product not found."
            }

        inventory = db.execute(
            select(Inventory).where(
                Inventory.product_id == product_id
            )
        ).scalar_one_or_none()

        if not inventory:
            inventory = Inventory(
                product_id=product_id,
                quantity=Decimal("0")
            )

            db.add(inventory)

        inventory.quantity = (
            Decimal(str(inventory.quantity))
            + quantity
        )

        db.commit()
        db.refresh(inventory)

        return {
            "success": True,
            "message": f"Received {quantity} {product.unit} of {product.name}.",
            "product": product.name,
            "quantity_received": float(quantity),
            "new_stock": float(inventory.quantity),
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
# LOW STOCK
# =========================================================

def get_low_stock():
    db = SessionLocal()

    try:
        products = db.execute(
            select(Product)
        ).scalars().all()

        results = []

        for product in products:

            inventory = db.execute(
                select(Inventory).where(
                    Inventory.product_id == product.id
                )
            ).scalar_one_or_none()

            if not inventory:
                continue

            quantity = Decimal(
                str(inventory.quantity)
            )

            reorder_level = Decimal(
                str(product.reorder_level)
            )

            if quantity <= reorder_level:
                results.append({
                    "product_id": product.id,
                    "sku": product.sku,
                    "product": product.name,
                    "stock": float(quantity),
                    "reorder_level": float(reorder_level),
                    "unit": product.unit,
                })

        return {
            "success": True,
            "count": len(results),
            "low_stock_products": results,
        }

    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
        }

    finally:
        db.close()


# =========================================================
# ADD NEW PRODUCT
# =========================================================

def add_product(
    sku: str,
    name: str,
    brand: str,
    unit: str,
    cost_price: float,
    sell_price: float,
    mrp: float,
    gst_rate: float,
    hsn_code: str,
    reorder_level: float = 0,
    initial_stock: float = 0,
):
    db = SessionLocal()

    try:
        # -------------------------------------------------
        # Basic validation
        # -------------------------------------------------

        sku = sku.strip()
        name = name.strip()
        brand = brand.strip() if brand else ""
        unit = unit.strip().lower()
        hsn_code = hsn_code.strip()

        cost_price = Decimal(str(cost_price))
        sell_price = Decimal(str(sell_price))
        mrp = Decimal(str(mrp))
        gst_rate = Decimal(str(gst_rate))
        reorder_level = Decimal(str(reorder_level))
        initial_stock = Decimal(str(initial_stock))

        if not sku:
            return {
                "success": False,
                "error": "SKU is required."
            }

        if not name:
            return {
                "success": False,
                "error": "Product name is required."
            }

        if not unit:
            return {
                "success": False,
                "error": "Unit is required."
            }

        if cost_price < 0:
            return {
                "success": False,
                "error": "Cost price cannot be negative."
            }

        if sell_price < 0:
            return {
                "success": False,
                "error": "Selling price cannot be negative."
            }

        if mrp < 0:
            return {
                "success": False,
                "error": "MRP cannot be negative."
            }

        if gst_rate < 0 or gst_rate > 100:
            return {
                "success": False,
                "error": "GST rate must be between 0 and 100."
            }

        if reorder_level < 0:
            return {
                "success": False,
                "error": "Reorder level cannot be negative."
            }

        if initial_stock < 0:
            return {
                "success": False,
                "error": "Initial stock cannot be negative."
            }

        # -------------------------------------------------
        # Prevent selling below cost
        # -------------------------------------------------

        if sell_price < cost_price:
            return {
                "success": False,
                "error": (
                    f"Selling price ₹{sell_price} cannot be "
                    f"lower than cost price ₹{cost_price}."
                )
            }

        # -------------------------------------------------
        # Check duplicate SKU
        # -------------------------------------------------

        existing_product = db.execute(
            select(Product).where(
                Product.sku == sku
            )
        ).scalar_one_or_none()

        if existing_product:
            return {
                "success": False,
                "error": (
                    f"A product with SKU '{sku}' already exists."
                )
            }

        # -------------------------------------------------
        # Create product
        # -------------------------------------------------

        product = Product(
            sku=sku,
            name=name,
            brand=brand,
            unit=unit,
            is_loose=False,
            cost_price=cost_price,
            sell_price=sell_price,
            mrp=mrp,
            gst_rate=gst_rate,
            hsn_code=hsn_code,
            reorder_level=reorder_level,
        )

        db.add(product)

        db.flush()

        # -------------------------------------------------
        # Create inventory record
        # -------------------------------------------------

        inventory = Inventory(
            product_id=product.id,
            quantity=initial_stock,
        )

        db.add(inventory)

        db.commit()

        db.refresh(product)
        db.refresh(inventory)

        return {
            "success": True,
            "message": f"Product '{product.name}' added successfully.",
            "product": {
                "id": product.id,
                "sku": product.sku,
                "name": product.name,
                "brand": product.brand,
                "unit": product.unit,
                "cost_price": float(product.cost_price),
                "sell_price": float(product.sell_price),
                "mrp": float(product.mrp),
                "gst_rate": float(product.gst_rate),
                "hsn_code": product.hsn_code,
                "reorder_level": float(product.reorder_level),
                "initial_stock": float(inventory.quantity),
            }
        }

    except Exception as exc:
        db.rollback()

        return {
            "success": False,
            "error": str(exc),
        }

    finally:
        db.close()