from decimal import Decimal

from app.services.gst import calculate_gst


result = calculate_gst(Decimal("56"), Decimal("12"))

print("GST TEST")
print(result)