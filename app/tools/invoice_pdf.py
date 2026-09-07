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

from app.database import SessionLocal
from app.models import Bill, Product
from app.services.gst import money


def generate_invoice_pdf(bill_id: int):
    db = SessionLocal()

    try:
        bill = db.get(Bill, bill_id)

        if not bill:
            return {
                "success": False,
                "error": "Bill not found.",
            }

        if bill.status != "FINALIZED":
            return {
                "success": False,
                "error": "PDF can only be generated for a finalized bill.",
            }

        # -------------------------------------------------
        # PDF OUTPUT DIRECTORY
        # -------------------------------------------------

        output_dir = Path("generated_invoices")
        output_dir.mkdir(parents=True, exist_ok=True)

        pdf_path = output_dir / f"{bill.bill_number}.pdf"

        # -------------------------------------------------
        # DOCUMENT
        # -------------------------------------------------

        document = SimpleDocTemplate(
            str(pdf_path),
            pagesize=A4,
            rightMargin=15 * mm,
            leftMargin=15 * mm,
            topMargin=15 * mm,
            bottomMargin=15 * mm,
        )

        styles = getSampleStyleSheet()

        story = []

        # -------------------------------------------------
        # HEADER
        # -------------------------------------------------

        story.append(
            Paragraph(
                "<b>SUPERMARKET / KIRANA STORE</b>",
                styles["Title"],
            )
        )

        story.append(
            Paragraph(
                "GST TAX INVOICE",
                styles["Heading2"],
            )
        )

        story.append(Spacer(1, 8))

        # -------------------------------------------------
        # BILL INFORMATION
        # -------------------------------------------------

        bill_info = [
            ["Bill Number", bill.bill_number],
            ["Status", bill.status],
            ["Payment Mode", bill.payment_mode or "-"],
            [
                "Payment Reference",
                bill.payment_reference or "-",
            ],
            [
                "Date",
                str(bill.finalized_at or "-"),
            ],
        ]

        info_table = Table(
            bill_info,
            colWidths=[45 * mm, 120 * mm],
        )

        info_table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )

        story.append(info_table)
        story.append(Spacer(1, 12))

        # -------------------------------------------------
        # ITEMS
        # -------------------------------------------------

        item_data = [
            [
                "Product",
                "HSN",
                "Qty",
                "Unit Price",
                "GST %",
                "Taxable",
                "CGST",
                "SGST",
                "Total",
            ]
        ]

        for item in bill.items:

            product = db.get(Product, item.product_id)

            product_name = (
                product.name if product else "Unknown"
            )

            item_data.append(
                [
                    product_name,
                    item.hsn_code or "-",
                    str(item.quantity),
                    f"₹{money(Decimal(str(item.unit_price)))}",
                    f"{item.gst_rate}%",
                    f"₹{money(Decimal(str(item.taxable_amount)))}",
                    f"₹{money(Decimal(str(item.cgst)))}",
                    f"₹{money(Decimal(str(item.sgst)))}",
                    f"₹{money(Decimal(str(item.total)))}",
                ]
            )

        items_table = Table(
            item_data,
            repeatRows=1,
            colWidths=[
                35 * mm,
                15 * mm,
                12 * mm,
                22 * mm,
                15 * mm,
                22 * mm,
                18 * mm,
                18 * mm,
                22 * mm,
            ],
        )

        items_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "ALIGN",
                        (1, 1),
                        (-1, -1),
                        "RIGHT",
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        7,
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

        story.append(items_table)
        story.append(Spacer(1, 12))

        # -------------------------------------------------
        # TOTALS
        # -------------------------------------------------

        totals_data = [
            [
                "Subtotal",
                f"₹{money(Decimal(str(bill.subtotal)))}",
            ],
            [
                "CGST",
                f"₹{money(Decimal(str(bill.cgst)))}",
            ],
            [
                "SGST",
                f"₹{money(Decimal(str(bill.sgst)))}",
            ],
            [
                "IGST",
                f"₹{money(Decimal(str(bill.igst)))}",
            ],
            [
                "GRAND TOTAL",
                f"₹{money(Decimal(str(bill.grand_total)))}",
            ],
        ]

        totals_table = Table(
            totals_data,
            colWidths=[50 * mm, 40 * mm],
            hAlign="RIGHT",
        )

        totals_table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ("BACKGROUND", (0, 4), (-1, 4), colors.lightgrey),
                    ("FONTSIZE", (0, 4), (-1, 4), 11),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )

        story.append(totals_table)

        story.append(Spacer(1, 15))

        story.append(
            Paragraph(
                "Thank you for shopping with us!",
                styles["Normal"],
            )
        )

        # -------------------------------------------------
        # BUILD PDF
        # -------------------------------------------------

        document.build(story)

        return {
            "success": True,
            "bill_id": bill.id,
            "bill_number": bill.bill_number,
            "pdf_path": str(pdf_path),
        }

    except Exception as exc:

        return {
            "success": False,
            "error": str(exc),
        }

    finally:
        db.close()