from openai import OpenAI, OpenAIError

from llm import LLMResponse, LLMUsage
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

    client = OpenAI(
        base_url=settings.base_url,
        api_key=settings.api_key,
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

        usage = None
        finish_reason = None
        answer = []

        try:
            with client.chat.completions.create(
                model=settings.model_name,
                messages=messages,
                max_tokens=settings.max_tokens,
                temperature=settings.temperature,
                top_p=settings.top_p,
                stream=True,
                stream_options={"include_usage": settings.show_usage},
                extra_body={
                    "reasoning": {
                        "effort": "low",
                        "exclude": True,
                    }
                },
            ) as stream:

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

        except OpenAIError as error:
            messages.pop()
            print(f"\nRequest failed: {error}")
            continue

        response_usage = None

        if usage is not None:

            completion_details = getattr(
                usage,
                "completion_tokens_details",
                None,
            )

            response_usage = LLMUsage(
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
                reasoning_tokens=getattr(
                    completion_details,
                    "reasoning_tokens",
                    None,
                ),
                cost=getattr(usage, "cost", None),
            )

        response = LLMResponse(
            content="".join(answer),
            finish_reason=finish_reason,
            usage=response_usage,
        )

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
