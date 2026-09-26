import os
import sys
from openai import OpenAI, OpenAIError

def get_api_key():
    """Retrieve API key from environment variable or prompt the user."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("⚠️ OPENAI_API_KEY environment variable not detected.")
        api_key = input("👉 Enter your OpenAI API key (sk-...): ").strip()
        if not api_key:
            print("❌ No API key provided. Exiting.")
            sys.exit(1)
    return api_key


def main():
    # 1. Initialize the OpenAI client
    api_key = get_api_key()
    client = OpenAI(api_key=api_key)

    # 2. Define the Chatbot's personality (System Prompt)
    system_prompt = {
        "role": "system",
        "content": (
            "You are a helpful, friendly, and knowledgeable AI assistant. "
            "Provide clear, accurate, and concise answers."
        ),
    }

    # 3. Initialize message history to maintain conversational memory
    messages = [system_prompt]

    print("\n" + "=" * 55)
    print("🤖 Welcome to the AI Chatbot!")
    print("Commands:")
    print("  - Type 'exit' or 'quit' to end the chat.")
    print("  - Type 'clear' to reset conversation memory.")
    print("  - Type 'history' to inspect current context.")
    print("=" * 55 + "\n")

    # 4. Interactive chat loop
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()

            # Skip empty inputs
            if not user_input:
                continue

            # Command: Exit
            if user_input.lower() in ["exit", "quit"]:
                print("\n👋 Goodbye! Have a great day!")
                break

            # Command: Clear Memory
            if user_input.lower() == "clear":
                messages = [system_prompt]
                print("\n🧹 Conversation memory cleared!\n")
                continue

            # Command: View History
            if user_input.lower() == "history":
                print("\n--- Current Memory ---")
                for msg in messages:
                    print(f"[{msg['role'].upper()}]: {msg['content']}")
                print("----------------------\n")
                continue

            # Append the user's message to the conversation history
            messages.append({"role": "user", "content": user_input})

            print("\nAI: ", end="", flush=True)

            # 5. Call the API with streaming enabled
            stream = client.chat.completions.create(
                model="gpt-4o-mini",  # Fast, smart, and cost-effective model
                messages=messages,
                stream=True,          # Words appear in real-time as they generate
            )

            # 6. Stream and accumulate the AI's response tokens
            assistant_reply = ""
            for chunk in stream:
                token = chunk.choices[0].delta.content or ""
                assistant_reply += token
                print(token, end="", flush=True)

            print("\n")  # New line after output completes

            # 7. Append the assistant's reply to history for multi-turn context
            messages.append({"role": "assistant", "content": assistant_reply})

        except KeyboardInterrupt:
            print("\n\nChat session interrupted. Goodbye!")
            break
        except OpenAIError as e:
            print(f"\n❌ API Error: {e}\n")
        except Exception as e:
            print(f"\n❌ Unexpected Error: {e}\n")


if __name__ == "__main__":
    main()