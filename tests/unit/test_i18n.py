import pytest

from personal_ai.i18n import Language, Translator, resolve_language


def test_default_language_is_vietnamese():
    assert resolve_language(None) is Language.VI


def test_vietnamese_translation():
    translator = Translator(Language.VI)

    assert translator("title") == "PERSONAL AI 0.1.0 - DEMO TƯƠNG TÁC"
    assert translator("security") == "Bảo mật"


def test_english_translation():
    translator = Translator(Language.EN)

    assert translator("title") == "PERSONAL AI 0.1.0 - INTERACTIVE DEMO"


def test_chinese_translation():
    translator = Translator(Language.ZH)

    assert translator("title") == "PERSONAL AI 0.1.0 - 交互式演示"


def test_language_aliases():
    assert resolve_language("vn") is Language.VI
    assert resolve_language("english") is Language.EN
    assert resolve_language("cn") is Language.ZH


def test_unknown_language_is_rejected():
    with pytest.raises(ValueError):
        resolve_language("fr")
