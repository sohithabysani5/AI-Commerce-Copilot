from agents.commerce_agent import ask_commerce_agent


print("=" * 60)
print("AI COMMERCE COPILOT TEST")
print("=" * 60)

while True:

    message = input("\nCustomer: ")

    if message.lower() == "exit":
        break

    try:

        response = ask_commerce_agent(message)

        print("\nAI Commerce Copilot:")
        print(response)

    except Exception as e:

        print("\nERROR:")
        print(e)