from personal_ai.file_intelligence.capability import (
    FileCapability,
    resolve_file_capability,
)


def test_text_mime_type_is_supported() -> None:
    capability = resolve_file_capability(
        mime_type="text/plain",
        extension=".txt",
    )

    assert isinstance(capability, FileCapability)
    assert capability.extraction_supported is True
    assert capability.extractor_type == "text"


def test_text_extension_is_supported_without_mime_type() -> None:
    capability = resolve_file_capability(
        mime_type=None,
        extension=".txt",
    )

    assert capability.extraction_supported is True
    assert capability.extractor_type == "text"


def test_unknown_type_is_unsupported() -> None:
    capability = resolve_file_capability(
        mime_type="application/x-unknown",
        extension=".xyz",
    )

    assert capability.extraction_supported is False
    assert capability.extractor_type is None


def test_pdf_is_not_claimed_supported_yet() -> None:
    capability = resolve_file_capability(
        mime_type="application/pdf",
        extension=".pdf",
    )

    assert capability.extraction_supported is False
    assert capability.extractor_type is None


def test_image_is_not_claimed_supported_yet() -> None:
    capability = resolve_file_capability(
        mime_type="image/jpeg",
        extension=".jpg",
    )

    assert capability.extraction_supported is False
    assert capability.extractor_type is None


def test_mime_matching_is_case_insensitive() -> None:
    capability = resolve_file_capability(
        mime_type="TEXT/PLAIN",
        extension=".TXT",
    )

    assert capability.extraction_supported is True
    assert capability.extractor_type == "text"
