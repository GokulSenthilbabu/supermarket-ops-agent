from app.tools.khata import (
    add_credit,
    get_balance,
    record_payment,
)


print("\n--- ADD ₹500 CREDIT FOR RAMESH ---")

credit = add_credit(
    customer_name="Ramesh",
    amount=500,
    note="Demo credit"
)

print(credit)


print("\n--- CHECK RAMESH BALANCE ---")

balance = get_balance("Ramesh")

print(balance)


print("\n--- RAMESH PAYS ₹300 ---")

payment = record_payment(
    customer_name="Ramesh",
    amount=300,
    note="Cash payment"
)

print(payment)


print("\n--- CHECK BALANCE AFTER PAYMENT ---")

balance = get_balance("Ramesh")

print(balance)


print("\n--- TRY INVALID PAYMENT ---")

invalid_payment = record_payment(
    customer_name="Ramesh",
    amount=500
)

print(invalid_payment)