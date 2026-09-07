from app.tools.preferences import (
    set_preference,
    get_preference,
    get_all_preferences,
)

owner = "direct-test-user"

print("\n==============================")
print(" PREFERENCE TOOL TEST")
print("==============================")

print("\nSET:")
print(
    set_preference(
        owner,
        "default_payment",
        "UPI"
    )
)

print("\nGET:")
print(
    get_preference(
        owner,
        "default_payment"
    )
)

print("\nALL:")
print(
    get_all_preferences(
        owner
    )
)

print("\n=== PREFERENCE TEST PASSED ===")