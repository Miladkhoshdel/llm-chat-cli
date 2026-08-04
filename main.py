from openai import OpenAI, OpenAIError

from utils import get_required_config, read_input, read_number


def main():
    try:
        api_key = get_required_config("API_KEY", cast=str)
        base_url = get_required_config("BASE_URL", cast=str)
        model_name = get_required_config("MODEL_NAME", cast=str)
        show_usage = get_required_config("SHOW_USAGE", cast=bool)
        max_tokens = get_required_config("MAX_TOKENS", cast=int)
        temperature = get_required_config("TEMPERATURE", cast=float)
        top_p = get_required_config("TOP_P", cast=float)
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

        stream = client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stream=True,
            stream_options={"include_usage": True},
            extra_body={
                "reasoning": {
                    "effort": "low",
                    "exclude": True,
                }
            },
        )

        usage = None
        answer = []

        for chunk in stream:

            if chunk.usage is not None:
                usage = chunk.usage

            if not chunk.choices:
                continue

            choice = chunk.choices[0]
            content = choice.delta.content

            if content:
                answer.append(content)
                print(content, end="", flush=True)

            if choice.finish_reason is not None:
                finish_reason = choice.finish_reason

        answer = "".join(answer)

        if finish_reason == "length":
            print("Warning: the answer may be incomplete.")

        if show_usage and usage:
            print("\n-----")
            print("Prompt tokens:", usage.prompt_tokens)
            print("Completion tokens:", usage.completion_tokens)
            print("Total tokens:", usage.total_tokens)

            reasoning_tokens = (
                usage.completion_tokens_details.reasoning_tokens
                if usage.completion_tokens_details
                else None
            )

            print("Reasoning tokens:", reasoning_tokens)
            print("Cost:", getattr(usage, "cost", None))
            print("-----\n")

        messages.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )


if __name__ == "__main__":
    raise SystemExit(main())
