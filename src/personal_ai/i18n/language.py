from enum import StrEnum


class Language(StrEnum):
    VI = "vi"
    EN = "en"
    ZH = "zh"


DEFAULT_LANGUAGE = Language.VI


def resolve_language(value: str | None) -> Language:
    if value is None or not value.strip():
        return DEFAULT_LANGUAGE

    normalized = value.strip().lower()

    aliases = {
        "vi": Language.VI,
        "vn": Language.VI,
        "vietnamese": Language.VI,
        "en": Language.EN,
        "english": Language.EN,
        "zh": Language.ZH,
        "cn": Language.ZH,
        "chinese": Language.ZH,
    }

    try:
        return aliases[normalized]
    except KeyError as exc:
        raise ValueError(f"unsupported language: {value}") from exc
