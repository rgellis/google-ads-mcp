"""Tests for the GAQL interpolation helpers in src.utils."""

import pytest

from src.utils import gaql_enum_name, gaql_int, gaql_resource_field


class TestGaqlInt:
    """Tests for gaql_int."""

    def test_accepts_int(self) -> None:
        assert gaql_int(123, "campaign_id") == "123"

    def test_accepts_numeric_string(self) -> None:
        assert gaql_int("456", "limit") == "456"

    def test_accepts_negative(self) -> None:
        # Some IDs aren't negative, but the helper just stringifies the int.
        assert gaql_int(-1, "limit") == "-1"

    def test_rejects_non_numeric_string(self) -> None:
        with pytest.raises(ValueError, match="campaign_id"):
            gaql_int("abc", "campaign_id")

    def test_rejects_quote_injection(self) -> None:
        with pytest.raises(ValueError, match="batch_job_id"):
            gaql_int("1' OR 1=1", "batch_job_id")

    def test_rejects_none(self) -> None:
        with pytest.raises(ValueError, match="limit"):
            gaql_int(None, "limit")

    def test_rejects_float_with_fraction(self) -> None:
        with pytest.raises(ValueError, match="limit"):
            gaql_int("1.5", "limit")


class TestGaqlEnumName:
    """Tests for gaql_enum_name."""

    def test_accepts_enabled(self) -> None:
        assert gaql_enum_name("ENABLED", "status_filter") == "ENABLED"

    def test_accepts_underscore_name(self) -> None:
        assert (
            gaql_enum_name("NEGATIVE_KEYWORDS", "criterion_type") == "NEGATIVE_KEYWORDS"
        )

    def test_accepts_digits_after_letter(self) -> None:
        # Some enum names embed digits, e.g. SHA256_EMAIL.
        assert gaql_enum_name("SHA256_EMAIL", "match_type") == "SHA256_EMAIL"

    def test_rejects_lowercase(self) -> None:
        with pytest.raises(ValueError, match="status_filter"):
            gaql_enum_name("enabled", "status_filter")

    def test_rejects_quote_injection(self) -> None:
        with pytest.raises(ValueError, match="status_filter"):
            gaql_enum_name("ENABLED' OR '1'='1", "status_filter")

    def test_rejects_space(self) -> None:
        with pytest.raises(ValueError, match="type_filter"):
            gaql_enum_name("FOO BAR", "type_filter")

    def test_rejects_leading_digit(self) -> None:
        with pytest.raises(ValueError, match="status_filter"):
            gaql_enum_name("1ABC", "status_filter")

    def test_rejects_non_string(self) -> None:
        with pytest.raises(ValueError, match="status_filter"):
            gaql_enum_name(123, "status_filter")

    def test_rejects_empty(self) -> None:
        with pytest.raises(ValueError, match="status_filter"):
            gaql_enum_name("", "status_filter")


class TestGaqlResourceField:
    """Tests for gaql_resource_field."""

    def test_accepts_simple(self) -> None:
        assert gaql_resource_field("campaign", "resource_name") == "campaign"

    def test_accepts_underscore_name(self) -> None:
        assert (
            gaql_resource_field("ad_group_criterion", "resource_name")
            == "ad_group_criterion"
        )

    def test_rejects_dot(self) -> None:
        # Dots aren't permitted — the helper validates a single name segment.
        with pytest.raises(ValueError, match="resource_name"):
            gaql_resource_field("campaign.id", "resource_name")

    def test_rejects_uppercase(self) -> None:
        with pytest.raises(ValueError, match="resource_name"):
            gaql_resource_field("Campaign", "resource_name")

    def test_rejects_quote_injection(self) -> None:
        with pytest.raises(ValueError, match="resource_name"):
            gaql_resource_field("campaign' OR '1'='1", "resource_name")

    def test_rejects_slash(self) -> None:
        # Resource paths (with slashes) can't go through this helper.
        with pytest.raises(ValueError, match="resource_name"):
            gaql_resource_field("customers/123/campaigns/456", "resource_name")

    def test_rejects_non_string(self) -> None:
        with pytest.raises(ValueError, match="resource_name"):
            gaql_resource_field(42, "resource_name")

    def test_rejects_empty(self) -> None:
        with pytest.raises(ValueError, match="resource_name"):
            gaql_resource_field("", "resource_name")
