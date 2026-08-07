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


def read_input(prompt):
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")
        return None


def calculate_input_token_budget(context_limit, output_limit):
    """Calculate how many tokens are available for input messages."""
    if context_limit <= 0:
        raise ValueError("MAX_CONTEXT_TOKENS must be greater than 0")

    if output_limit <= 0:
        raise ValueError("MAX_TOKENS must be greater than 0")

    if output_limit >= context_limit:
        raise ValueError("MAX_TOKENS must be smaller than MAX_CONTEXT_TOKENS")

    return context_limit - output_limit


__all__ = ["calculate_input_token_budget", "get_required_config", "read_input"]
