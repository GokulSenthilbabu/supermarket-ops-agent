from decimal import Decimal, ROUND_HALF_UP


TWO_PLACES = Decimal("0.01")


def money(value):
    """Round money to 2 decimal places."""
    return Decimal(str(value)).quantize(
        TWO_PLACES,
        rounding=ROUND_HALF_UP
    )


def calculate_gst(taxable_amount, gst_rate):
    """
    Calculate GST for an intra-state sale.

    CGST and SGST are split equally.
    """

    taxable_amount = Decimal(str(taxable_amount))
    gst_rate = Decimal(str(gst_rate))

    total_gst = money(
        taxable_amount * gst_rate / Decimal("100")
    )

    cgst = money(total_gst / Decimal("2"))
    sgst = money(total_gst - cgst)

    total = money(taxable_amount + cgst + sgst)

    return {
        "taxable_amount": money(taxable_amount),
        "gst_rate": gst_rate,
        "cgst": cgst,
        "sgst": sgst,
        "igst": Decimal("0.00"),
        "total_gst": money(cgst + sgst),
        "total": total,
    }