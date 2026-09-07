from app.agent import run_agent

print("\n==============================")
print(" AGENT BUSINESS FEATURES TEST")
print("==============================")

tests = [
    "Show today's sales.",
    "What are the top selling products today?",
    "Give me today's business summary.",
    "Create the weekly sales analysis PPTX."
]

for message in tests:
    print("\nUSER:", message)
    print("AGENT:", run_agent(message, "feature-test-user"))

print("\n=== FEATURE TEST FINISHED ===")