from app.agent import run_agent, reset_chat

user_id = "preference-test-user"

print("\n==============================")
print(" PREFERENCE TEST")
print("==============================")

print("\nUSER: Use UPI by default.")
print("AGENT:", run_agent(
    "Remember that I prefer UPI as my default payment method.",
    user_id
))

reset_chat(user_id)

print("\n--- NEW CHAT ---")

print("\nUSER: What payment method do I prefer?")
print("AGENT:", run_agent(
    "What payment method do I prefer?",
    user_id
))

print("\n=== PREFERENCE TEST FINISHED ===")