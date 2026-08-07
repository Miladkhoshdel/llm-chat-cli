from dataclasses import dataclass, field

from decouple import config


def get_required_config(name, cast):
    raw_value = config(name, default=None)

    if raw_value is None or not str(raw_value).strip():
        raise ValueError(f"{name} is missing or empty in .env")

    try:
        value = config(name, cast=cast)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} has an invalid value: {error}") from error

    return value.strip() if isinstance(value, str) else value


@dataclass(frozen=True)
class Settings:
    api_key: str = field(repr=False)
    base_url: str
    model_name: str
    show_usage: bool
    max_tokens: int
    max_context_tokens: int
    temperature: float
    top_p: float
    memory_keep_count: int

    def __post_init__(self):
        if self.max_tokens <= 0:
            raise ValueError("MAX_TOKENS must be greater than 0")

        if self.max_context_tokens <= 0:
            raise ValueError("MAX_CONTEXT_TOKENS must be greater than 0")

        if self.max_tokens >= self.max_context_tokens:
            raise ValueError(
                "MAX_TOKENS must be smaller than MAX_CONTEXT_TOKENS"
            )

        if self.memory_keep_count < 0:
            raise ValueError("MEMORY_KEEP_COUNT must be 0 or greater")

    @property
    def input_token_budget(self):
        return self.max_context_tokens - self.max_tokens


def load_settings():
    return Settings(
        api_key=get_required_config("API_KEY", cast=str),
        base_url=get_required_config("BASE_URL", cast=str),
        model_name=get_required_config("MODEL_NAME", cast=str),
        show_usage=get_required_config("SHOW_USAGE", cast=bool),
        max_tokens=get_required_config("MAX_TOKENS", cast=int),
        max_context_tokens=get_required_config(
            "MAX_CONTEXT_TOKENS",
            cast=int,
        ),
        temperature=get_required_config("TEMPERATURE", cast=float),
        top_p=get_required_config("TOP_P", cast=float),
        memory_keep_count=get_required_config("MEMORY_KEEP_COUNT", cast=int),
    )


__all__ = ["Settings", "get_required_config", "load_settings"]
