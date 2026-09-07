from app.agent import run_agent, reset_chat

user_id = "billing-agent-test"

messages = [
    "Start a new bill.",
    "Add 2 Maggi 70g.",
    "Actually make the Maggi quantity 3.",
    "Add 1 Aashirvaad Atta 5kg.",
    "Show me the current bill.",
    "Finalize the bill and pay by UPI."
]

print("\n==============================")
print(" AGENT BILLING FLOW")
print("==============================")

for message in messages:
    print("\nUSER:", message)
    print("AGENT:", run_agent(message, user_id))

print("\n=== BILLING FLOW FINISHED ===")