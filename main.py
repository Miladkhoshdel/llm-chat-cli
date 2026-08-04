from math import isfinite

from decouple import config
from openai import OpenAI, OpenAIError


def get_required_config(name):
    value = config(name, cast=str, default="").strip()

    if not value:
        raise ValueError(f"{name} is missing or empty in .env")

    return value


def read_input(prompt):
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")
        return None


def read_number(prompt, number_type, minimum, maximum=None):
    while True:
        raw_value = read_input(prompt)

        if raw_value is None:
            return None

        try:
            value = number_type(raw_value)
        except ValueError:
            print("Please enter a valid number.")
            continue

        if not isfinite(value):
            print("Please enter a finite number.")
            continue

        if value < minimum or (maximum is not None and value > maximum):
            if maximum is None:
                print(f"Value must be at least {minimum}.")
            else:
                print(f"Value must be between {minimum} and {maximum}.")
            continue

        return value


def main():
    try:
        api_key = get_required_config("API_KEY")
        base_url = get_required_config("BASE_URL")
        model_name = get_required_config("MODEL_NAME")
    except ValueError as error:
        print(f"Configuration error: {error}")
        return 1

    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
    )

    while True:
        system_rule = read_input("System rule: ")

        if system_rule is None:
            return 0

        if system_rule:
            break

        print("Please enter a system rule.")

    max_tokens = read_number("Max tokens: ", int, 1)
    if max_tokens is None:
        return 0

    temperature = read_number("Temperature (0-2): ", float, 0, 2)
    if temperature is None:
        return 0

    top_p = read_number("Top-p (0-1): ", float, 0, 1)
    if top_p is None:
        return 0

    messages = [
        {
            "role": "system",
            "content": system_rule,
        }
    ]

    while True:
        user_input = read_input("You: ")

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
            completion = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                extra_body={
                    "reasoning": {
                        "effort": "low",
                        "exclude": True,
                    }
                },
            )
        except OpenAIError as error:
            messages.pop()
            print(f"Request failed: {error}")
            continue

        if not completion.choices:
            messages.pop()
            print("Request failed: the provider returned no response choices.")
            continue

        choice = completion.choices[0]
        answer = choice.message.content

        if not answer:
            messages.pop()
            print("Request failed: the provider returned an empty response.")
            continue

        if choice.finish_reason == "length":
            print("Warning: the answer may be incomplete.")

        print(f"Assistant: {answer}")

        if completion.usage and completion.usage.total_tokens is not None:
            print(f"Tokens: {completion.usage.total_tokens}")

        messages.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )


if __name__ == "__main__":
    raise SystemExit(main())
