from pathlib import Path
from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

INVOICE_DIR = BASE_DIR / "generated" / "invoices"
INVOICE_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# HELPERS
# =========================================================

def money(value):
    return f"₹{Decimal(str(value)):.2f}"


# =========================================================
# GENERATE INVOICE PDF
# =========================================================

def generate_invoice_pdf(bill: dict) -> str:
    """
    Generate a GST invoice PDF from finalized bill data.

    Args:
        bill: Finalized bill dictionary returned by billing tools.

    Returns:
        Absolute path of generated PDF.
    """

    bill_id = bill.get("bill_id")

    bill_number = bill.get(
        "bill_number",
        f"BILL-{bill_id}"
    )

    filename = f"{bill_number}.pdf"

    output_path = INVOICE_DIR / filename

    # -----------------------------------------------------
    # Document
    # -----------------------------------------------------

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    heading_style = styles["Heading2"]
    normal_style = styles["Normal"]

    story = []

    # -----------------------------------------------------
    # Header
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "SUPERMARKET GST INVOICE",
            title_style,
        )
    )

    story.append(Spacer(1, 5 * mm))

    story.append(
        Paragraph(
            f"<b>Invoice No:</b> {bill_number}",
            normal_style,
        )
    )

    story.append(
        Paragraph(
            f"<b>Bill ID:</b> {bill_id}",
            normal_style,
        )
    )

    payment_mode = bill.get(
        "payment_mode",
        "N/A"
    )

    story.append(
        Paragraph(
            f"<b>Payment Mode:</b> {payment_mode}",
            normal_style,
        )
    )

    payment_reference = bill.get(
        "payment_reference"
    )

    if payment_reference:
        story.append(
            Paragraph(
                f"<b>Payment Reference:</b> "
                f"{payment_reference}",
                normal_style,
            )
        )

    story.append(Spacer(1, 8 * mm))

    # -----------------------------------------------------
    # Items
    # -----------------------------------------------------

    items = bill.get("items", [])

    table_data = [
        [
            "S.No",
            "Product",
            "HSN",
            "Qty",
            "Rate",
            "GST %",
            "Taxable",
            "CGST",
            "SGST",
            "Total",
        ]
    ]

    for index, item in enumerate(items, start=1):

        table_data.append(
            [
                str(index),
                str(item.get("product", "")),
                str(item.get("hsn_code", "")),
                str(item.get("quantity", "")),
                money(item.get("unit_price", 0)),
                f"{item.get('gst_rate', 0)}%",
                money(item.get("taxable_amount", 0)),
                money(item.get("cgst", 0)),
                money(item.get("sgst", 0)),
                money(item.get("total", 0)),
            ]
        )

    item_table = Table(
        table_data,
        repeatRows=1,
        colWidths=[
            8 * mm,
            34 * mm,
            20 * mm,
            12 * mm,
            20 * mm,
            14 * mm,
            22 * mm,
            20 * mm,
            20 * mm,
            22 * mm,
        ],
    )

    item_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey,
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.black,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
            ]
        )
    )

    story.append(item_table)

    story.append(Spacer(1, 8 * mm))

    # -----------------------------------------------------
    # Totals
    # -----------------------------------------------------

    subtotal = bill.get("subtotal", 0)
    cgst = bill.get("cgst", 0)
    sgst = bill.get("sgst", 0)
    igst = bill.get("igst", 0)
    grand_total = bill.get("grand_total", 0)

    totals_data = [
        ["Subtotal", money(subtotal)],
        ["CGST", money(cgst)],
        ["SGST", money(sgst)],
        ["IGST", money(igst)],
        ["Grand Total", money(grand_total)],
    ]

    totals_table = Table(
        totals_data,
        colWidths=[
            45 * mm,
            35 * mm,
        ],
        hAlign="RIGHT",
    )

    totals_table.setStyle(
        TableStyle(
            [
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, -1),
                    "Helvetica",
                ),
                (
                    "FONTNAME",
                    (0, -1),
                    (-1, -1),
                    "Helvetica-Bold",
                ),
                (
                    "ALIGN",
                    (1, 0),
                    (1, -1),
                    "RIGHT",
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
            ]
        )
    )

    story.append(totals_table)

    story.append(Spacer(1, 10 * mm))

    story.append(
        Paragraph(
            "<b>Thank you for shopping with us!</b>",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            "This invoice contains GST details including "
            "HSN, CGST and SGST.",
            normal_style,
        )
    )

    # -----------------------------------------------------
    # Build PDF
    # -----------------------------------------------------

    document.build(story)

    return str(output_path)