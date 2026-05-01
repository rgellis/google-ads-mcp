import logging
import os
import re
from pathlib import Path
from typing import Any, Dict
from google.protobuf.json_format import MessageToDict


_GAQL_ENUM_NAME_RE = re.compile(r"[A-Z][A-Z0-9_]*")
_GAQL_RESOURCE_FIELD_RE = re.compile(r"[a-z][a-z0-9_]*")
_GAQL_STRING_DISALLOWED_CHAR_RE = re.compile(r"[\x00-\x1f\x7f]")
_CUSTOMER_ID_RE = re.compile(r"\d{10}")


def gaql_int(value: Any, field_name: str) -> str:
    """Coerce ``value`` to an int and return its string form for GAQL interpolation.

    Use for any numeric ID or LIMIT clause. Raises ``ValueError`` on input
    that isn't a clean integer — the LLM caller will see a clear error
    rather than producing a syntactically broken GAQL query.
    """
    try:
        return str(int(value))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be an integer; got {value!r}") from exc


def gaql_enum_name(value: Any, field_name: str) -> str:
    """Validate ``value`` looks like a GAQL enum name (e.g. ENABLED, NEGATIVE_KEYWORDS).

    Permits only uppercase letters, digits, and underscores starting with a
    letter. Catches typos with quotes/escapes/spaces before they are
    interpolated into a GAQL string literal. Google's API will still reject
    enum names that aren't members of the target field's enum, but the
    pre-check ensures malformed input fails locally with a useful error.
    """
    if not isinstance(value, str) or not _GAQL_ENUM_NAME_RE.fullmatch(value):
        raise ValueError(
            f"{field_name} must be an uppercase enum name "
            f"(letters, digits, underscores); got {value!r}"
        )
    return value


def gaql_resource_field(value: Any, field_name: str) -> str:
    """Validate ``value`` looks like a GAQL resource or field name.

    Permits only lowercase letters, digits, and underscores starting with
    a letter — the shape of every resource/field name in the v23 GAQL
    schema (e.g. ``campaign``, ``ad_group_criterion``, ``customer_match_user_list``).
    """
    if not isinstance(value, str) or not _GAQL_RESOURCE_FIELD_RE.fullmatch(value):
        raise ValueError(
            f"{field_name} must be a lowercase GAQL resource/field name "
            f"(letters, digits, underscores); got {value!r}"
        )
    return value


def gaql_string_literal(value: Any, field_name: str) -> str:
    """Escape ``value`` and wrap it as a GAQL single-quoted string literal.

    Use for freeform user content interpolated into GAQL — campaign names,
    asset text, search patterns, etc. Returns the value already enclosed
    in single quotes; the caller writes the equality/LIKE operator and
    inserts the result directly (no surrounding quotes in the f-string).

    Per the GAQL grammar
    (https://developers.google.com/google-ads/api/docs/query/grammar) string
    literals escape only ``\\`` and the surrounding quote character. We
    additionally reject ASCII control characters (``\\x00``-``\\x1f``,
    ``\\x7f``) because GAQL parsers typically do not accept them and the
    LLM has no legitimate reason to send them.

    Example::

        name_contains = "Joe's Pizza"
        query += f" AND campaign.name LIKE {gaql_string_literal('%' + name_contains + '%', 'name_contains')}"
        # → " AND campaign.name LIKE '%Joe\\'s Pizza%'"
    """
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string; got {type(value).__name__}")
    if _GAQL_STRING_DISALLOWED_CHAR_RE.search(value):
        raise ValueError(
            f"{field_name} contains a control character; "
            "control characters (\\x00-\\x1f, \\x7f) are not allowed in GAQL string literals"
        )
    escaped = value.replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped}'"


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def load_dotenv(dotenv_path: str = ".env") -> None:
    if not Path(dotenv_path).exists():
        raise FileNotFoundError(f"Dotenv file not found: {dotenv_path}")

    with Path(dotenv_path).open() as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


def format_customer_id(customer_id: Any) -> str:
    """Normalize and validate a Google Ads customer ID.

    Strips hyphens, then verifies the result is exactly 10 digits — the
    shape Google Ads customer IDs always take. Validating here means the
    normalized ID is safe to interpolate into GAQL string literals,
    resource names, or proto fields without further escaping.

    Args:
        customer_id: The customer ID with or without hyphens
            (e.g., "123-456-7890" or "1234567890")

    Returns:
        The customer ID with hyphens removed (e.g., "1234567890")

    Raises:
        ValueError: If the input isn't a string, or doesn't normalize to
            exactly 10 digits.
    """
    if not isinstance(customer_id, str):
        raise ValueError(
            f"customer_id must be a string; got {type(customer_id).__name__}"
        )
    normalized = customer_id.replace("-", "")
    if not _CUSTOMER_ID_RE.fullmatch(normalized):
        raise ValueError(
            f"customer_id must be 10 digits (with or without hyphens); "
            f"got {customer_id!r}"
        )
    return normalized


def set_request_options(
    request: Any,
    partial_failure: bool = False,
    validate_only: bool = False,
    response_content_type: Any = None,
) -> None:
    """Set common optional fields on a Google Ads API request.

    Safely sets partial_failure, validate_only, and response_content_type
    on any request object that supports them. Fields not present on the
    request type are silently skipped.

    Args:
        request: A Google Ads API request proto object
        partial_failure: If true, successful operations proceed even if others fail
        validate_only: If true, validate the request without executing
        response_content_type: Enum value controlling what's returned in the response
    """
    if partial_failure and hasattr(request, "partial_failure"):
        request.partial_failure = partial_failure
    if validate_only and hasattr(request, "validate_only"):
        request.validate_only = validate_only
    if response_content_type is not None and hasattr(request, "response_content_type"):
        request.response_content_type = response_content_type


def serialize_proto_message(
    message: Any, use_integers_for_enums: bool = False
) -> Dict[str, Any]:
    """Serialize a proto-plus message to a dictionary.

    Args:
        message: A proto-plus message object
        use_integers_for_enums: If True, return enum values as integers instead of strings

    Returns:
        A dictionary representation of the message
    """
    try:
        # For proto-plus messages, we need to convert to the underlying protobuf message
        if hasattr(message, "_pb"):
            # This is a proto-plus message
            return MessageToDict(
                message._pb,
                preserving_proto_field_name=True,
                use_integers_for_enums=use_integers_for_enums,
            )
        else:
            # This is a regular protobuf message
            return MessageToDict(
                message,
                preserving_proto_field_name=True,
                use_integers_for_enums=use_integers_for_enums,
            )
    except Exception as e:
        # Fallback to manual conversion if MessageToDict fails
        logger = get_logger(__name__)
        logger.warning(f"Failed to serialize message with MessageToDict: {e}")

        # Try to convert manually
        result = {}
        if hasattr(message, "__dict__"):
            for key, value in message.__dict__.items():
                if not key.startswith("_"):
                    result[key] = str(value) if value is not None else None
        return result
