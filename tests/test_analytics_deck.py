from app.tools.analytics_deck import (
    generate_weekly_sales_deck,
)


print("\n==============================")
print(" WEEKLY SALES DECK TEST")
print("==============================")


result = generate_weekly_sales_deck()

print("\n--- RESULT ---")

print(result)


if not result["success"]:
    raise SystemExit(
        "Weekly sales deck generation failed."
    )


print("\n--- PPTX CREATED ---")

print(result["pptx_path"])

print("\n=== PPTX TEST PASSED ===")