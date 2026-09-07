from app.tools.inventory import add_product, search_products


def main():

    print("\n--- ADD NEW PRODUCT ---")

    result = add_product(
        sku="THUMSUP-750ML",
        name="Thums Up 750ml",
        brand="Coca-Cola",
        unit="piece",
        cost_price=35,
        sell_price=45,
        mrp=50,
        gst_rate=12,
        hsn_code="22021010",
        reorder_level=10,
        initial_stock=20,
    )

    print(result)

    print("\n--- SEARCH NEW PRODUCT ---")

    result = search_products("Thums Up")

    print(result)


if __name__ == "__main__":
    main()