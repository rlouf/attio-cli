from attio_cli.columns import extract_name, summarize_value, truncate


def test_extract_name_prefers_simple_name_field():
    assert extract_name({"name": "Jane Doe"}) == "Jane Doe"


def test_extract_name_reads_nested_email_address():
    assert (
        extract_name({"email_addresses": [{"email_address": "jane@example.com"}]})
        == "jane@example.com"
    )


def test_extract_name_falls_back_to_dash_when_empty():
    assert extract_name({}) == "-"


def test_truncate_adds_ellipsis_for_long_strings():
    assert truncate("abcdefghij", 5) == "abcde..."


def test_truncate_leaves_short_strings_alone():
    assert truncate("abc", 5) == "abc"


def test_summarize_value_removes_metadata_keys():
    summary = summarize_value(
        {
            "active_from": "2026-01-01",
            "attribute_type": "text",
            "created_by_actor": {"id": "actor_1"},
            "value": "EMEA",
        }
    )

    assert "active_from" not in summary
    assert "attribute_type" not in summary
    assert "EMEA" in summary


def test_summarize_value_returns_dash_when_only_metadata():
    assert (
        summarize_value(
            {
                "active_from": "2026-01-01",
                "active_until": "2026-02-01",
                "attribute_type": "text",
                "created_by_actor": {"id": "actor_1"},
            }
        )
        == "-"
    )
