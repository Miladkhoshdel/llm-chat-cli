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
        "content": " You are a Python programming language teacher. Answer in a single sentence of no more than 50 words.",
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
        max_tokens=500,
        temperature=0.1,
        top_p=0.9,
        extra_body={
            "reasoning": {
                "effort": "low",
                "exclude": True,
            }
        },
    )

    choice = completion.choices[0]

    if choice.finish_reason == "length":
        print("Warning: the answer may be incomplete.")

    answer = choice.message.content

    print(f"Assistant: {answer}")
    if completion.usage:
        print(f"Tokens: {completion.usage.total_tokens}")

    messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )
