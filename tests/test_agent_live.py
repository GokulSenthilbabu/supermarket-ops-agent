from app.agent import run_agent, reset_chat


USER = "test-agent-user"


def ask(message):
    print("\nUSER:", message)

    response = run_agent(
        message,
        user_id=USER,
    )

    print("AGENT:", response)

    return response


print("\n==============================")
print(" LIVE AGENT TEST")
print("==============================")


ask("How much Aashirvaad Atta 5kg is in stock?")

ask("How much Maggi 70g is in stock?")

ask("What products are running low?")

print("\n=== AGENT TEST FINISHED ===")