def try_parse_int(val: str) -> int | None:
    try:
        return int(val)
    except (ValueError, TypeError):
        return None
