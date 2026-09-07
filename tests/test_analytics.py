from app.tools.analytics import (
    get_daily_sales,
    get_top_items,
    get_daily_summary,
)


print("\n==============================")
print(" DAILY SALES ANALYTICS TEST")
print("==============================")


print("\n--- DAILY SALES ---")

sales = get_daily_sales()

print(sales)

if not sales["success"]:
    raise SystemExit("Daily sales failed.")


print("\n--- TOP ITEMS ---")

top_items = get_top_items()

print(top_items)

if not top_items["success"]:
    raise SystemExit("Top items failed.")


print("\n--- DAILY SUMMARY ---")

summary = get_daily_summary()

print(summary)

if not summary["success"]:
    raise SystemExit("Daily summary failed.")


print("\n=== ANALYTICS TEST PASSED ===")