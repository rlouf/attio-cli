"""Shared table column definitions and value formatters."""

from attio_cli.output import ColumnSpec, Row


def extract_name(values: Row) -> str:
    """Extract a display name from record values."""
    for field in ["name", "full_name", "first_name", "title", "email_addresses"]:
        if field in values:
            val = values[field]
            if isinstance(val, list) and val:
                first = val[0]
                if isinstance(first, dict):
                    for key in ["value", "email_address", "full_name", "first_name"]:
                        if key in first:
                            return str(first[key])
                else:
                    return str(first)
            elif val:
                return str(val)
    return "-"


def truncate(value: str, length: int) -> str:
    """Truncate a string with ellipsis."""
    return value[:length] + "..." if len(value) > length else value


def summarize_value(item: Row) -> str:
    """Summarize an attribute value payload for table output."""
    metadata_keys = {
        "active_from",
        "active_until",
        "attribute_type",
        "created_by_actor",
    }
    value = {k: v for k, v in item.items() if k not in metadata_keys}
    return truncate(str(value), 60) if value else "-"


IDENTITY_COLUMNS: list[ColumnSpec] = [
    ("WORKSPACE", lambda x: x.get("workspace", {}).get("name", "-")),
    ("WORKSPACE ID", lambda x: x.get("workspace", {}).get("id", {}).get("workspace_id", "-")),
    ("ACCESS TYPE", lambda x: x.get("access_type", "-")),
]

OBJECT_COLUMNS: list[ColumnSpec] = [
    ("SLUG", lambda x: x.get("api_slug", "-")),
    ("SINGULAR", lambda x: x.get("singular_noun", "-")),
    ("PLURAL", lambda x: x.get("plural_noun", "-")),
    ("ID", lambda x: x.get("id", {}).get("object_id", "-")),
]

RECORD_COLUMNS: list[ColumnSpec] = [
    ("ID", lambda x: x.get("id", {}).get("record_id", "-")),
    ("NAME", lambda x: extract_name(x.get("values", {}))),
    ("VALUES", lambda x: truncate(str(x.get("values", {})), 60)),
]

SEARCH_COLUMNS: list[ColumnSpec] = [
    ("RECORD ID", lambda x: x.get("id", {}).get("record_id", "-")),
    ("OBJECT", lambda x: x.get("object_slug", "-")),
    ("TEXT", lambda x: x.get("record_text", "-")),
]

RECORD_ENTRY_COLUMNS: list[ColumnSpec] = [
    ("ENTRY ID", lambda x: x.get("entry_id", "-")),
    ("LIST", lambda x: x.get("list_api_slug", "-")),
    ("LIST ID", lambda x: x.get("list_id", "-")),
]

LIST_COLUMNS: list[ColumnSpec] = [
    ("SLUG", lambda x: x.get("api_slug", "-")),
    ("NAME", lambda x: x.get("name", "-")),
    (
        "PARENT OBJECT",
        lambda x: ", ".join(x.get("parent_object", [])) if x.get("parent_object") else "-",
    ),
    ("ID", lambda x: x.get("id", {}).get("list_id", "-")),
]

ENTRY_COLUMNS: list[ColumnSpec] = [
    ("ENTRY ID", lambda x: x.get("id", {}).get("entry_id", "-")),
    ("RECORD ID", lambda x: x.get("parent_record_id", "-")),
    ("VALUES", lambda x: truncate(str(x.get("entry_values", {})), 60)),
]

TASK_COLUMNS: list[ColumnSpec] = [
    ("ID", lambda x: x.get("id", {}).get("task_id", "-")),
    ("CONTENT", lambda x: truncate(x.get("content_plaintext", ""), 50)),
    ("COMPLETED", lambda x: "Y" if x.get("is_completed") else ""),
    ("DEADLINE", lambda x: x.get("deadline_at", "-") or "-"),
]

NOTE_COLUMNS: list[ColumnSpec] = [
    ("ID", lambda x: x.get("id", {}).get("note_id", "-")),
    ("TITLE", lambda x: x.get("title", "-") or "-"),
    (
        "PARENT",
        lambda x: f"{x.get('parent_object', '')}:{x.get('parent_record_id', '')[:8]}"
        if x.get("parent_record_id")
        else "-",
    ),
    ("CREATED", lambda x: (x.get("created_at", "") or "")[:10] or "-"),
]

ATTRIBUTE_COLUMNS: list[ColumnSpec] = [
    ("SLUG", lambda x: x.get("api_slug", "-")),
    ("TITLE", lambda x: x.get("title", "-")),
    ("TYPE", lambda x: x.get("type", "-")),
    ("REQUIRED", lambda x: "Y" if x.get("is_required") else ""),
    ("MULTISELECT", lambda x: "Y" if x.get("is_multiselect") else ""),
]

OPTION_COLUMNS: list[ColumnSpec] = [
    ("ID", lambda x: x.get("id", {}).get("option_id", "-")),
    ("TITLE", lambda x: x.get("title", "-")),
    ("ARCHIVED", lambda x: "Y" if x.get("is_archived") else ""),
]

STATUS_COLUMNS: list[ColumnSpec] = [
    ("ID", lambda x: x.get("id", {}).get("status_id", "-")),
    ("TITLE", lambda x: x.get("title", "-")),
    ("ARCHIVED", lambda x: "Y" if x.get("is_archived") else ""),
]

ATTRIBUTE_VALUE_COLUMNS: list[ColumnSpec] = [
    ("ACTIVE FROM", lambda x: x.get("active_from", "-") or "-"),
    ("ACTIVE UNTIL", lambda x: x.get("active_until", "-") or "-"),
    ("TYPE", lambda x: x.get("attribute_type", "-") or "-"),
    ("VALUE", lambda x: summarize_value(x)),
]

MEMBER_COLUMNS: list[ColumnSpec] = [
    ("ID", lambda x: x.get("id", {}).get("workspace_member_id", "-")),
    ("NAME", lambda x: f"{x.get('first_name', '')} {x.get('last_name', '')}".strip() or "-"),
    ("EMAIL", lambda x: x.get("email_address", "-") or "-"),
    ("ACCESS", lambda x: x.get("access_level", "-") or "-"),
]

WEBHOOK_COLUMNS: list[ColumnSpec] = [
    ("ID", lambda x: x.get("id", {}).get("webhook_id", "-")),
    ("TARGET URL", lambda x: x.get("target_url", "-")),
    ("STATUS", lambda x: x.get("status", "-") or "-"),
    (
        "SUBSCRIPTIONS",
        lambda x: f"{len(x.get('subscriptions', []))} events" if x.get("subscriptions") else "-",
    ),
]
