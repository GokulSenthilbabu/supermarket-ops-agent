from app.agent import run_agent


def main():
    user_id = "test-user"

    print("\n==============================")
    print("SUPERMARKET OPS AGENT TEST")
    print("==============================\n")

    messages = [
        "How much Maggi 70g is currently in stock?",
        "What products do you have from Amul?",
        "What is Ramesh's current khata balance?",
    ]

    for message in messages:
        print("USER:")
        print(message)

        response = run_agent(
            message,
            user_id=user_id
        )

        print("\nAGENT:")
        print(response)

        print("\n------------------------------\n")


if __name__ == "__main__":
    main()