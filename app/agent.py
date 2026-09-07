import os
from dotenv import load_dotenv

from google import genai
from google.genai import types

from app.tools.inventory import (
    search_products,
    get_stock,
    receive_stock,
    get_low_stock,
    add_product,
)

from app.tools.billing import (
    create_bill,
    add_bill_item,
    get_current_bill,
    remove_bill_item,
    finalize_bill,
)

from app.tools.khata import (
    add_credit,
    record_payment,
    get_balance,
)

from app.tools.analytics import (
    get_daily_sales,
    get_top_items,
    get_daily_summary,
)

from app.tools.analytics_deck import (
    generate_weekly_sales_deck,
)

from app.tools.preferences import (
    set_preference,
    get_preference,
    get_all_preferences,
)


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. "
        "Please add it to your .env file."
    )


# =========================================================
# GEMINI CLIENT
# =========================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# =========================================================
# INVENTORY TOOL WRAPPERS
# =========================================================

def tool_search_products(query: str) -> dict:
    """Search the supermarket product catalog.

    Args:
        query: Product name, brand name, SKU, or keyword.

    Returns:
        Matching products with prices, stock, GST and HSN information.
    """

    return search_products(query)


def tool_get_stock(product_id: int) -> dict:
    """Get the current stock for a product.

    Args:
        product_id: Database ID of the product.

    Returns:
        Current stock information.
    """

    return get_stock(product_id)


def tool_receive_stock(
    product_id: int,
    quantity: float,
) -> dict:
    """Receive new stock into supermarket inventory.

    Args:
        product_id: Database ID of the product.
        quantity: Quantity received.

    Returns:
        Updated inventory information.
    """

    return receive_stock(
        product_id=product_id,
        quantity=quantity,
    )


def tool_get_low_stock() -> dict:
    """Find products whose stock is at or below reorder level.

    Returns:
        List of low-stock products.
    """

    return get_low_stock()


def tool_add_product(
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
) -> dict:
    """Add a new product to the supermarket catalog.

    Args:
        sku: Unique product SKU.
        name: Product name.
        brand: Product brand.
        unit: Unit such as packet, kg, g, litre, ml, piece, or dozen.
        cost_price: Purchase/cost price.
        sell_price: Selling price.
        mrp: Maximum retail price.
        gst_rate: GST percentage.
        hsn_code: HSN code.
        reorder_level: Minimum stock level for reorder alerts.
        initial_stock: Initial inventory quantity.

    Returns:
        Newly created product and inventory information.
    """

    return add_product(
        sku=sku,
        name=name,
        brand=brand,
        unit=unit,
        cost_price=cost_price,
        sell_price=sell_price,
        mrp=mrp,
        gst_rate=gst_rate,
        hsn_code=hsn_code,
        reorder_level=reorder_level,
        initial_stock=initial_stock,
    )


# =========================================================
# BILLING TOOL WRAPPERS
# =========================================================

def tool_create_bill() -> dict:
    """Create a new draft supermarket bill.

    Returns:
        Newly created draft bill.
    """

    return create_bill()


def tool_add_bill_item(
    bill_id: int,
    product_id: int,
    quantity: float,
) -> dict:
    """Add a product to a draft bill.

    Inventory is NOT deducted at this stage.

    Args:
        bill_id: Draft bill ID.
        product_id: Product database ID.
        quantity: Quantity to add.

    Returns:
        Updated draft bill information.
    """

    return add_bill_item(
        bill_id=bill_id,
        product_id=product_id,
        quantity=quantity,
    )


def tool_get_current_bill(
    bill_id: int,
) -> dict:
    """Get the contents of a draft bill.

    Args:
        bill_id: Draft bill ID.

    Returns:
        Current bill and its items.
    """

    return get_current_bill(
        bill_id=bill_id
    )


def tool_remove_bill_item(
    bill_id: int,
    item_id: int,
) -> dict:
    """Remove an item from a draft bill.

    Args:
        bill_id: Draft bill ID.
        item_id: Bill item ID.

    Returns:
        Updated draft bill.
    """

    return remove_bill_item(
        bill_id=bill_id,
        item_id=item_id,
    )


def tool_finalize_bill(
    bill_id: int,
    payment_mode: str,
    payment_reference: str | None = None,
) -> dict:
    """Finalize a supermarket bill and deduct stock.

    Valid payment modes are CASH, UPI and CARD.

    Inventory is deducted only when this function succeeds.

    Args:
        bill_id: Draft bill ID.
        payment_mode: CASH, UPI or CARD.
        payment_reference: Optional transaction/reference number.

    Returns:
        Finalized bill details including GST and total.
    """

    return finalize_bill(
        bill_id=bill_id,
        payment_mode=payment_mode,
        payment_reference=payment_reference,
    )


# =========================================================
# KHATA TOOL WRAPPERS
# =========================================================

def tool_add_credit(
    customer_name: str,
    amount: float,
    note: str | None = None,
) -> dict:
    """Add a credit transaction to a customer's khata.

    Args:
        customer_name: Customer name.
        amount: Credit amount.
        note: Optional note.

    Returns:
        Updated khata information.
    """

    return add_credit(
        customer_name=customer_name,
        amount=amount,
        note=note,
    )


def tool_record_payment(
    customer_name: str,
    amount: float,
    note: str | None = None,
) -> dict:
    """Record a payment made by a khata customer.

    The payment cannot exceed the customer's outstanding balance.

    Args:
        customer_name: Customer name.
        amount: Payment amount.
        note: Optional note.

    Returns:
        Updated khata information.
    """

    return record_payment(
        customer_name=customer_name,
        amount=amount,
        note=note,
    )


def tool_get_balance(
    customer_name: str,
) -> dict:
    """Get the outstanding khata balance of a customer.

    Args:
        customer_name: Customer name.

    Returns:
        Customer balance.
    """

    return get_balance(
        customer_name
    )


# =========================================================
# ANALYTICS TOOL WRAPPERS
# =========================================================

def tool_get_daily_sales() -> dict:
    """Get today's finalized sales summary.

    Returns:
        Daily sales, bill count, GST and payment-method totals.
    """

    return get_daily_sales()


def tool_get_top_items(
    limit: int = 5,
) -> dict:
    """Get the top-selling products for today.

    Args:
        limit: Maximum number of products to return.

    Returns:
        Top-selling products by quantity and sales.
    """

    return get_top_items(
        limit=limit
    )


def tool_get_daily_summary() -> dict:
    """Get the complete daily supermarket summary.

    Returns:
        Daily sales and top-selling product information.
    """

    return get_daily_summary()


def tool_generate_weekly_sales_deck() -> dict:
    """Generate the weekly sales analysis PowerPoint.

    Returns:
        Path and information about the generated PPTX file.
    """

    return generate_weekly_sales_deck()


# =========================================================
# SYSTEM INSTRUCTIONS
# =========================================================

SYSTEM_INSTRUCTIONS = """
You are the Supermarket Ops Agent for an Indian kirana/supermarket.

Your job is to operate the supermarket using the provided tools.

You are an agent, not a simple chatbot.

Use the available tools to observe the current state,
reason about what action is required, perform the action,
inspect the tool result, and continue until the user's
request is complete.

=========================================================
1. REAL DATA
=========================================================

ALWAYS use tools for real supermarket data.

Never invent:

- product names
- prices
- stock quantities
- GST rates
- HSN codes
- bill totals
- khata balances
- sales totals
- payment totals

The database and tools are authoritative.


=========================================================
2. PRODUCT LOOKUP
=========================================================

If the user asks about a product:

1. Search the product catalog.
2. Inspect the returned products.
3. Use the product ID from the tool result.

Never guess a product ID.


=========================================================
3. AMBIGUOUS PRODUCTS
=========================================================

If multiple products match the user's request:

Ask the user to clarify which product they mean.

Do not randomly choose a product.


=========================================================
4. INVENTORY
=========================================================

Always use inventory tools for inventory information.

Never manually invent or calculate stock.

When the user asks:

- how much stock
- stock available
- inventory
- quantity available

use the stock/search tools.


=========================================================
5. RECEIVE STOCK
=========================================================

Use the receive_stock tool when the user says things such as:

- stock arrived
- stock received
- purchase received
- goods received
- received inventory
- add stock

First identify the correct product.

Then receive the requested quantity.

Never receive negative or zero stock.


=========================================================
6. LOW STOCK
=========================================================

Use the low-stock tool when the user asks:

- what is running low
- which products are low
- which items need restocking
- reorder list
- low stock
- products to reorder

Do not guess reorder levels.


=========================================================
7. ADD PRODUCT
=========================================================

When the user wants to add a completely new product,
use the add_product tool.

Required information:

- SKU
- product name
- brand
- unit
- cost price
- selling price
- MRP
- GST rate
- HSN code

Optional:

- reorder level
- initial stock

If required information is missing:

Ask the user for it.

Never invent:

- GST
- HSN
- cost price
- selling price
- MRP
- SKU

Never create a duplicate SKU.

Never allow selling price below cost price.


=========================================================
8. BILLING
=========================================================

Billing follows this lifecycle:

CREATE BILL
    ↓
ADD ITEMS
    ↓
EDIT / REMOVE ITEMS
    ↓
REVIEW BILL
    ↓
FINALIZE
    ↓
PAYMENT
    ↓
STOCK DEDUCTION
    ↓
INVOICE


A bill must be created before adding items.

Keep the current bill ID in the conversation.

When the user adds more products to the same bill,
continue using the existing draft bill.

Do not create a second bill unnecessarily.


=========================================================
9. BILL EDITING
=========================================================

If the user says:

- remove
- delete
- drop
- take out
- remove this item

remove the relevant bill item.

If the user wants to change a quantity,
use the available billing operations appropriately.

Always show the updated bill after an important edit.


=========================================================
10. STOCK DURING BILLING
=========================================================

Stock MUST NOT be deducted while a bill is still a draft.

Stock is deducted only when finalize_bill succeeds.

Never manually deduct stock.


=========================================================
11. OVERSELL PROTECTION
=========================================================

Never allow a bill to sell more stock than is available.

The billing tool is authoritative.

If the tool rejects an oversell:

Tell the user that the requested quantity is unavailable.

Do not claim the item was added.


=========================================================
12. SELLING BELOW COST
=========================================================

Never allow a product to be sold below its cost price.

The billing tool is authoritative.

If the tool rejects the operation:

Explain that the selling price cannot be below cost.


=========================================================
13. PAYMENT
=========================================================

Allowed payment modes:

- CASH
- UPI
- CARD

If payment mode is ambiguous:

Ask the user to clarify.

Do not invent payment references.

If the user provides a UPI/card transaction reference,
pass it to the billing tool.


=========================================================
14. GST
=========================================================

GST calculations are handled by the billing system.

Never manually calculate the final bill total when the
billing tool provides the result.

Use the GST values returned by the tool.

Report:

- subtotal
- CGST
- SGST
- IGST if applicable
- grand total


=========================================================
15. BILL FINALIZATION
=========================================================

Only say that the bill is completed after finalize_bill
successfully returns.

When finalization succeeds:

Report:

- bill number
- subtotal
- CGST
- SGST
- IGST
- grand total
- payment mode

If the billing tool reports that the bill was already
finalized, do not finalize it again.


=========================================================
16. PDF INVOICE
=========================================================

When the user asks for:

- invoice
- bill PDF
- receipt PDF
- send the bill
- send invoice
- generate invoice

use the billing/PDF functionality available through the tools.

Never invent a PDF path.

If PDF generation succeeds, tell the user that the invoice
was generated.

If PDF generation fails, report the failure honestly.


=========================================================
17. KHATA
=========================================================

Use tools for every khata operation.

Never invent:

- customer accounts
- customer balances
- credit amounts
- payment amounts

For credit:

Use the add_credit tool.

For payment:

Use record_payment.

For balance:

Use get_balance.


=========================================================
18. KHATA PAYMENT SAFETY
=========================================================

Never allow a customer payment greater than their
outstanding balance.

If the tool rejects the payment:

Tell the user the payment cannot be greater than the
outstanding balance.

If the customer does not exist:

Do not invent an account.

Ask the user what they want to do.


=========================================================
19. DAILY SALES
=========================================================

When the user asks:

- today's sales
- how much did we sell today
- daily sales
- sales today
- today's revenue

use the daily sales tool.

Report real values returned by the tool.

Useful fields include:

- bill count
- total sales
- tax collected
- CGST
- SGST
- IGST
- cash
- UPI
- card


=========================================================
20. TOP PRODUCTS
=========================================================

When the user asks:

- top products
- best selling products
- what sold most
- top sellers
- best sellers

use the top-items tool.

Do not guess popularity.


=========================================================
21. DAILY CLOSE
=========================================================

When the user asks:

- close the day
- daily close
- end of day
- today's summary
- close today's business

use the daily summary tool.

Provide a concise business summary including:

- number of bills
- total sales
- GST collected
- payment breakdown
- top-selling products


=========================================================
22. WEEKLY SALES ANALYSIS
=========================================================

When the user asks:

- weekly analysis
- weekly report
- sales report
- create sales PPT
- generate PPT
- weekly sales presentation
- business analysis

use the weekly sales deck tool.

Do not claim that a PPTX was generated unless the tool
successfully returns a generated artifact.


=========================================================
23. PREFERENCES / MEMORY
=========================================================

The supermarket owner may have persistent preferences.

Examples:

- preferred payment method
- preferred reporting style
- preferred invoice style
- other operational preferences

When the user explicitly asks you to remember something:

Store it using the preference tool.

When the user asks what they prefer:

Retrieve it using the preference tool.

Preferences are persistent database data.

A new chat must NOT delete preferences.


=========================================================
24. PREFERENCE SAFETY
=========================================================

Never claim that a preference was remembered unless the
preference tool successfully stores it.

Never invent an existing preference.

If no preference exists:

Say that no preference has been stored.


=========================================================
25. NEW CHAT
=========================================================

A new chat only resets conversational context.

It does NOT delete:

- products
- inventory
- bills
- finalized sales
- khata
- preferences


=========================================================
26. CONVERSATION
=========================================================

Understand natural language.

Do NOT use a hardcoded keyword or regex intent router.

Decide which tools are necessary based on the user's request.

You may call multiple tools when necessary.


=========================================================
27. TOOL RESULTS
=========================================================

Tool results are authoritative.

After calling a tool:

- inspect the result
- continue if another action is required
- report errors honestly

Never claim success when a tool returned failure.


=========================================================
28. FINANCIAL SAFETY
=========================================================

Never invent financial values.

Always use the database/tool result for:

- prices
- cost
- GST
- bill totals
- sales
- payments
- khata balances


=========================================================
29. RESPONSE STYLE
=========================================================

Be concise and practical.

Use Indian Rupees:

₹

For bills, clearly show:

Subtotal
CGST
SGST
IGST
Grand Total
Payment Mode

For inventory:

Product
Quantity
Unit

For errors:

Explain what went wrong and what the user should do next.


=========================================================
30. AGENT BEHAVIOUR
=========================================================

You should behave like a supermarket operations assistant.

Do not merely explain how an operation could be performed.

When the user asks you to perform an operation:

USE THE TOOL.

Observe the tool result.

Then continue until the requested operation is complete.
"""


# =========================================================
# COMMON GEMINI TOOLS
# =========================================================

COMMON_TOOLS = [
    # Inventory
    tool_search_products,
    tool_get_stock,
    tool_receive_stock,
    tool_get_low_stock,
    tool_add_product,

    # Billing
    tool_create_bill,
    tool_add_bill_item,
    tool_get_current_bill,
    tool_remove_bill_item,
    tool_finalize_bill,

    # Khata
    tool_add_credit,
    tool_record_payment,
    tool_get_balance,

    # Analytics
    tool_get_daily_sales,
    tool_get_top_items,
    tool_get_daily_summary,
    tool_generate_weekly_sales_deck,
]


# =========================================================
# USER-SPECIFIC PREFERENCE TOOL FACTORY
# =========================================================

def build_preference_tools(owner_id: str):
    """
    Build preference tools bound to a specific owner/user.

    The Gemini model does NOT choose the owner_id.
    The application supplies it from the current user session.
    """

    def tool_set_preference(
        key: str,
        value: str,
    ) -> dict:
        """Store a persistent preference for the current supermarket owner.

        Args:
            key: Preference name.
            value: Preference value.

        Returns:
            Stored preference information.
        """

        return set_preference(
            owner_id=owner_id,
            key=key,
            value=value,
        )

    def tool_get_preference(
        key: str,
    ) -> dict:
        """Get a stored preference for the current supermarket owner.

        Args:
            key: Preference name.

        Returns:
            Stored preference or a not-found result.
        """

        return get_preference(
            owner_id=owner_id,
            key=key,
        )

    def tool_get_all_preferences() -> dict:
        """Get all stored preferences for the current supermarket owner.

        Returns:
            All persistent preferences.
        """

        return get_all_preferences(
            owner_id=owner_id,
        )

    return [
        tool_set_preference,
        tool_get_preference,
        tool_get_all_preferences,
    ]


# =========================================================
# CHAT SESSIONS
# =========================================================

_sessions = {}


def get_chat(user_id: str):
    """
    Get or create a Gemini chat session for a user.

    Each user gets:
    - their own conversation context
    - their own preference tools
    """

    if user_id not in _sessions:

        user_preference_tools = build_preference_tools(
            owner_id=user_id
        )

        user_tools = [
            *COMMON_TOOLS,
            *user_preference_tools,
        ]

        user_system_instructions = (
            SYSTEM_INSTRUCTIONS
            + "\n\n"
            + "=========================================================\n"
            + "CURRENT OWNER / USER CONTEXT\n"
            + "=========================================================\n"
            + f"The current application owner_id is: {user_id}\n"
            + "\n"
            + "Preference tools are already securely bound to this "
              "owner_id.\n"
            + "Do not ask the user for an owner_id.\n"
        )

        user_config = types.GenerateContentConfig(
            system_instruction=user_system_instructions,
            tools=user_tools,
        )

        _sessions[user_id] = client.chats.create(
            model="gemini-3.6-flash",
            config=user_config,
        )

    return _sessions[user_id]


# =========================================================
# RESET CHAT
# =========================================================

def reset_chat(user_id: str):
    """
    Reset only the conversation context.

    Database data is NOT deleted.

    This means:

    /new chat
        ↓
    Gemini conversation cleared

    But these remain:

    products
    inventory
    bills
    sales
    khata
    preferences
    """

    _sessions.pop(
        user_id,
        None,
    )


# =========================================================
# RUN AGENT
# =========================================================

def run_agent(
    message: str,
    user_id: str = "test-user",
) -> str:
    """
    Send a user message to the supermarket agent.

    Args:
        message: Natural-language user request.
        user_id: Application/Telegram user ID.

    Returns:
        Agent response text.
    """

    if not message or not message.strip():
        return "Please enter a request."

    try:

        chat = get_chat(user_id)

        response = chat.send_message(
            message.strip()
        )

        if response.text:
            return response.text

        return "I couldn't generate a response."

    except Exception as exc:

        return f"Agent error: {exc}"