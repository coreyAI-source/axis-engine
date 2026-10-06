"""Tests for GSTC Hotel Standard validation and enforcement."""
import pytest
from app.utils.gstc_validation import (
    validate_criteria_code,
    validate_criteria_codes,
    enforce_gstc_criteria,
    get_gstc_standard_info,
)
from app.services import gstc_standard


class TestValidateCriteriaCode:
    """Test single criteria code validation."""

    def test_valid_official_gstc_codes(self):
        """Official GSTC criteria should be valid."""
        codes = ["A1", "A14", "B1", "B9", "C1", "C4", "D1", "D13"]
        for code in codes:
            is_valid, reason = validate_criteria_code(code)
            assert is_valid, f"{code} should be valid: {reason}"
            assert "Official GSTC" in reason

    def test_case_insensitive_codes(self):
        """Criteria codes should be case-insensitive."""
        is_valid, _ = validate_criteria_code("a1")
        assert is_valid
        is_valid, _ = validate_criteria_code("b9")
        assert is_valid

    def test_valid_custom_codes(self):
        """Custom codes (X1, X2, etc.) should be valid."""
        codes = ["X1", "X2", "X99", "X100"]
        for code in codes:
            is_valid, reason = validate_criteria_code(code)
            assert is_valid, f"{code} should be valid: {reason}"
            assert "Custom criterion" in reason

    def test_invalid_codes(self):
        """Invalid codes should fail validation."""
        codes = ["A15", "B10", "Z1", "INVALID", "123", ""]
        for code in codes:
            is_valid, reason = validate_criteria_code(code)
            assert not is_valid, f"{code} should be invalid but was valid"

    def test_non_string_codes(self):
        """Non-string codes should be invalid."""
        is_valid, reason = validate_criteria_code(None)
        assert not is_valid
        is_valid, reason = validate_criteria_code(123)
        assert not is_valid

    def test_whitespace_handling(self):
        """Whitespace should be stripped."""
        is_valid, _ = validate_criteria_code("  A1  ")
        assert is_valid
        is_valid, _ = validate_criteria_code("\tB2\n")
        assert is_valid


class TestValidateCriteriaCodesList:
    """Test list validation."""

    def test_all_valid_gstc_codes(self):
        """List with only official GSTC codes."""
        result = validate_criteria_codes(["A1", "B2", "C3", "D4"])
        assert len(result["valid"]) == 4
        assert len(result["invalid"]) == 0
        assert len(result["custom"]) == 0
        assert len(result["errors"]) == 0

    def test_mixed_valid_and_invalid(self):
        """List with mix of valid and invalid codes."""
        result = validate_criteria_codes(["A1", "ZZ99", "B2", "INVALID"])
        assert "A1" in result["valid"]
        assert "B2" in result["valid"]
        assert "ZZ99" in result["invalid"]
        assert "INVALID" in result["invalid"]
        assert len(result["errors"]) == 2

    def test_custom_codes_identified(self):
        """Custom codes should be separated."""
        result = validate_criteria_codes(["A1", "X1", "B2", "X99"])
        assert "A1" in result["valid"]
        assert "B2" in result["valid"]
        assert "X1" in result["custom"]
        assert "X99" in result["custom"]

    def test_empty_list(self):
        """Empty list should be handled gracefully."""
        result = validate_criteria_codes([])
        assert result["valid"] == []
        assert result["invalid"] == []
        assert result["custom"] == []
        assert result["errors"] == []

    def test_non_list_input(self):
        """Non-list input should produce error."""
        result = validate_criteria_codes("not-a-list")
        assert len(result["errors"]) > 0
        assert result["valid"] == []

    def test_duplicate_codes(self):
        """Duplicate codes in the list should be handled."""
        result = validate_criteria_codes(["A1", "A1", "B2", "B2"])
        # Should only appear once in results
        assert result["valid"].count("A1") == 1
        assert result["valid"].count("B2") == 1

    def test_case_normalization(self):
        """Codes should be normalized to uppercase."""
        result = validate_criteria_codes(["a1", "b2", "x1"])
        assert "A1" in result["valid"]
        assert "B2" in result["valid"]
        assert "X1" in result["custom"]


class TestEnforceGstcCriteria:
    """Test bundle validation."""

    def test_empty_bundle(self):
        """Empty bundle should not produce warnings."""
        warnings = enforce_gstc_criteria({})
        # Empty bundle is valid
        assert len(warnings) == 0 or all("Invalid" in w for w in warnings)

    def test_bundle_with_valid_gstc_criteria(self):
        """Bundle with only official GSTC criteria."""
        bundle = {
            "requirements": [
                {"id": "req1", "source": {"clause": "A1"}, "reviewStatus": "approved"},
                {"id": "req2", "source": {"clause": "B2"}, "reviewStatus": "approved"},
            ]
        }
        warnings = enforce_gstc_criteria(bundle)
        # Should not warn about official GSTC criteria
        assert not any("non-GSTC" in w for w in warnings)

    def test_bundle_with_unapproved_custom_criteria(self):
        """Bundle with custom criteria that need approval."""
        bundle = {
            "requirements": [
                {"id": "req1", "source": {"clause": "X1"}, "reviewStatus": "draft"},
            ]
        }
        warnings = enforce_gstc_criteria(bundle)
        assert any("Custom criterion" in w and "draft" in w for w in warnings)

    def test_bundle_with_approved_custom_criteria(self):
        """Bundle with approved custom criteria should not warn."""
        bundle = {
            "requirements": [
                {"id": "req1", "source": {"clause": "X1"}, "reviewStatus": "approved"},
            ]
        }
        warnings = enforce_gstc_criteria(bundle)
        assert not any("not 'approved'" in w for w in warnings)

    def test_bundle_with_invalid_criteria(self):
        """Bundle with non-GSTC, non-custom criteria."""
        bundle = {
            "requirements": [
                {"id": "req1", "source": {"clause": "ZZ99"}},
            ]
        }
        warnings = enforce_gstc_criteria(bundle)
        assert any("non-GSTC" in w for w in warnings)

    def test_invalid_bundle_structure(self):
        """Malformed bundles should produce error."""
        warnings = enforce_gstc_criteria("not-a-dict")
        assert len(warnings) > 0

    def test_bundle_with_missing_clause(self):
        """Requirement without clause should be skipped."""
        bundle = {
            "requirements": [
                {"id": "req1", "source": {}},  # No clause
            ]
        }
        warnings = enforce_gstc_criteria(bundle)
        assert len(warnings) == 0


class TestGetGstcStandardInfo:
    """Test GSTC standard info retrieval."""

    def test_standard_info_structure(self):
        """Standard info should have expected structure."""
        info = get_gstc_standard_info()

        assert "metadata" in info
        assert "criteria_by_pillar" in info
        assert "total_criteria" in info
        assert "valid_pillar_codes" in info
        assert "custom_criteria_pattern" in info
        assert "sample_criteria" in info

    def test_metadata_completeness(self):
        """Metadata should contain version and source."""
        info = get_gstc_standard_info()
        metadata = info["metadata"]

        assert "version" in metadata
        assert "source" in metadata
        assert "date" in metadata
        assert "total_criteria" in metadata
        assert metadata["version"] == "4.01"

    def test_pillar_counts(self):
        """Pillar counts should match GSTC standard."""
        info = get_gstc_standard_info()
        pillar_counts = info["criteria_by_pillar"]

        assert pillar_counts.get("A") == 14  # 40 total criteria in GSTC v4.01
        assert pillar_counts.get("B") == 9
        assert pillar_counts.get("C") == 4
        assert pillar_counts.get("D") == 13

    def test_total_criteria_count(self):
        """Total criteria should be 40."""
        info = get_gstc_standard_info()
        assert info["total_criteria"] == 40

    def test_valid_pillar_codes(self):
        """Valid pillar codes should be A, B, C, D."""
        info = get_gstc_standard_info()
        assert info["valid_pillar_codes"] == ["A", "B", "C", "D"]

    def test_sample_criteria_availability(self):
        """Sample criteria should be retrievable."""
        info = get_gstc_standard_info()
        samples = info["sample_criteria"]

        assert "A1" in samples
        assert "B1" in samples
        assert "C1" in samples
        assert "D1" in samples

        # Each sample should have code and title
        for code, criterion in samples.items():
            if criterion:  # Some might be None if criteria don't exist
                assert "code" in criterion
                assert "title" in criterion


class TestGstcStandardLoading:
    """Test that GSTC standard is properly loaded."""

    def test_gstc_standard_available(self):
        """GSTC standard should be loadable."""
        criteria = gstc_standard.get_all_criteria()
        assert len(criteria) > 0

    def test_all_40_criteria_present(self):
        """All 40 criteria should be loaded."""
        criteria = gstc_standard.get_all_criteria()
        assert len(criteria) == 40

    def test_criterion_a1_available(self):
        """Criterion A1 should exist."""
        a1 = gstc_standard.get_criterion("A1")
        assert a1 is not None
        assert a1["code"] == "A1"
        assert "title" in a1
        assert "statement" in a1

    def test_all_pillars_have_criteria(self):
        """All pillars should have criteria."""
        for pillar in ["A", "B", "C", "D"]:
            criteria = gstc_standard.get_pillar_criteria(pillar)
            assert len(criteria) > 0, f"Pillar {pillar} has no criteria"

    def test_criterion_structure(self):
        """Each criterion should have required fields."""
        all_criteria = gstc_standard.get_all_criteria()
        required_fields = {"code", "title", "statement", "indicators"}

        for code, criterion in all_criteria.items():
            for field in required_fields:
                assert field in criterion, f"{code} missing field: {field}"
