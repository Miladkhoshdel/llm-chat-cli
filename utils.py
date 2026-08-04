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


__all__ = ["get_required_config", "read_input"]
