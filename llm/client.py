from openai import OpenAI

from .models import LLMResponse, LLMUsage


class LLM:
    def __init__(self, settings, client=None):
        self.settings = settings

        if client is None:
            client = OpenAI(
                base_url=settings.base_url,
                api_key=settings.api_key,
            )

        self.client = client

    def create_stream(self, messages):
        return self.client.chat.completions.create(
            model=self.settings.model_name,
            messages=messages,
            max_tokens=self.settings.max_tokens,
            temperature=self.settings.temperature,
            top_p=self.settings.top_p,
            stream=True,
            stream_options={
                "include_usage": self.settings.show_usage,
            },
            extra_body={
                "reasoning": {
                    "effort": "low",
                    "exclude": True,
                }
            },
        )

    @staticmethod
    def build_usage(usage):
        if usage is None:
            return None

        completion_details = getattr(
            usage,
            "completion_tokens_details",
            None,
        )

        return LLMUsage(
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

    def build_response(self, answer, finish_reason, usage):
        return LLMResponse(
            content="".join(answer),
            finish_reason=finish_reason,
            usage=self.build_usage(usage),
        )

    def complete(self, messages, on_text=None):
        usage = None
        finish_reason = None
        answer = []

        with self.create_stream(messages) as stream:
            for chunk in stream:
                if chunk.usage is not None:
                    usage = chunk.usage

                if not chunk.choices:
                    continue

                choice = chunk.choices[0]
                content = choice.delta.content

                if content:
                    answer.append(content)
                    if on_text is not None:
                        on_text(content)

                if choice.finish_reason is not None:
                    finish_reason = choice.finish_reason

        return self.build_response(answer, finish_reason, usage)


__all__ = ["LLM", "LLMResponse", "LLMUsage"]
