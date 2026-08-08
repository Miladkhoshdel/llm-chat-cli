from openai import OpenAIError

from llm import LLM
from settings import load_settings
from utils import print_usage, read_input


def trim_history(messages, keep_count):
    """Keep the system message and the latest completed exchanges."""
    if keep_count < 0:
        raise ValueError("MEMORY_KEEP_COUNT must be 0 or greater")

    if keep_count == 0:
        return messages[:1]

    conversation = messages[1:]
    conversation_start = -(keep_count * 2)
    return messages[:1] + conversation[conversation_start:]


def main():
    try:
        settings = load_settings()
    except ValueError as error:
        print(f"Configuration error: {error}")
        return 1

    model = LLM(settings)

    while True:
        system_rule = read_input("System rule: ")

        if system_rule is None:
            return 0

        if system_rule:
            break

        print("Please enter a system rule.")

    messages = [
        {
            "role": "system",
            "content": system_rule,
        }
    ]

    while True:
        user_input = read_input("\nYou: ")

        if user_input is None or user_input.lower() in {"exit", "quit"}:
            return 0

        if not user_input:
            print("Please enter a message.")
            continue

        messages.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        try:
            response = model.complete(
                messages,
                on_text=lambda text: print(text, end="", flush=True),
            )
        except OpenAIError as error:
            messages.pop()
            print(f"\nRequest failed: {error}")
            continue

        if response.finish_reason == "length":
            print("Warning: the answer may be incomplete.")

        if settings.show_usage and response.usage:
            print_usage(response.usage)

        messages.append(
            {
                "role": "assistant",
                "content": response.content,
            }
        )
        messages = trim_history(messages, settings.memory_keep_count)


if __name__ == "__main__":
    raise SystemExit(main())
