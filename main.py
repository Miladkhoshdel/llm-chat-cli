from decouple import config
from openai import OpenAI

api_key = config("API_KEY", cast=str, default="")
base_url = config("BASE_URL", cast=str, default="")


if not api_key:
    raise ValueError("API_KEY not found")


if not base_url:
    raise ValueError("BASE_URL not found")

client = OpenAI(
    base_url=base_url,
    api_key=api_key,
)

messages = [
    {
        "role": "system",
        "content": "You are a perfect chef in a restaurant. answer by a single sentence with max 50 words.",
    }
]


while True:
    user_input = input("You: ").strip()

    if user_input.lower() in {"exit", "quit"}:
        break

    messages.append(
        {
            "role": "user",
            "content": user_input,
        }
    )

    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b:free",
        messages=messages,
        extra_body={
            "reasoning": {
                "effort": "low",
                "exclude": True,
            }
        },
    )

    answer = completion.choices[0].message.content

    print(f"Assistant: {answer}")
    print(f"Tokens: {completion.usage.total_tokens}")

    messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )
