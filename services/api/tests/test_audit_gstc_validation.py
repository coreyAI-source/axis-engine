"""
GSTC Audit Validation Test Suite

Tests for all validators in audit_validator.py against GSTC Section 8.5 requirements.
"""
import pytest
from datetime import date, timedelta

from app.services.audit_validator import (
    validate_risk_level,
    validate_audit_duration,
    validate_extremely_low_risk_qualification,
    validate_sensitive_area_assignment,
    validate_audit_section_coverage,
    validate_surveillance_audit_dates,
)


class TestRiskLevelValidation:
    """GSTC 8.5.12.4-6: Risk Assessment"""

    def test_valid_high_risk(self):
        """HIGH risk valid when corruption index < 50 or negative impacts present."""
        is_valid, msg = validate_risk_level("HIGH", country_corruption_index=40)
        assert is_valid
        assert msg is None

    def test_valid_high_risk_with_impacts(self):
        """HIGH risk valid with significant negative impacts."""
        is_valid, msg = validate_risk_level("HIGH", has_negative_impacts=True)
        assert is_valid

    def test_valid_low_risk(self):
        """LOW risk valid when corruption index >= 50 and no negative impacts."""
        is_valid, msg = validate_risk_level("LOW", country_corruption_index=60, has_negative_impacts=False)
        assert is_valid

    def test_invalid_high_risk_clean_country(self):
        """HIGH risk invalid when no impacts and corruption index >= 50."""
        is_valid, msg = validate_risk_level("HIGH", country_corruption_index=60, has_negative_impacts=False)
        assert not is_valid
        assert "cannot be assigned" in msg

    def test_invalid_low_risk_with_impacts(self):
        """LOW risk invalid with significant negative impacts."""
        is_valid, msg = validate_risk_level("LOW", has_negative_impacts=True)
        assert not is_valid

    def test_invalid_low_risk_corrupt_country(self):
        """LOW risk invalid in countries with corruption index < 50."""
        is_valid, msg = validate_risk_level("LOW", country_corruption_index=40)
        assert not is_valid

    def test_invalid_risk_level(self):
        """Invalid risk level rejected."""
        is_valid, msg = validate_risk_level("MEDIUM")
        assert not is_valid
        assert "Invalid risk level" in msg

    def test_missing_risk_level(self):
        """Missing risk level rejected."""
        is_valid, msg = validate_risk_level(None)
        assert not is_valid


class TestAuditDurationValidation:
    """GSTC 8.5.12.8-9: Audit Duration Rules"""

    def test_low_risk_onsite_1day(self):
        """LOW risk on-site: 1 day standard."""
        is_valid, msg = validate_audit_duration("LOW", "OnSite", 1.0)
        assert is_valid

    def test_low_risk_onsite_2days(self):
        """LOW risk on-site: 2 days acceptable."""
        is_valid, msg = validate_audit_duration("LOW", "OnSite", 2.0)
        assert is_valid

    def test_low_risk_onsite_invalid_duration(self):
        """LOW risk on-site: 3 days requires justification."""
        is_valid, msg = validate_audit_duration("LOW", "OnSite", 3.0)
        assert not is_valid
        assert "duration_justification" in msg

    def test_low_risk_onsite_with_justification(self):
        """LOW risk on-site: deviation accepted with justification."""
        is_valid, msg = validate_audit_duration(
            "LOW", "OnSite", 3.0, duration_justification="Additional remote sites audited"
        )
        assert is_valid

    def test_high_risk_onsite_2days(self):
        """HIGH risk on-site: 2+ days required."""
        is_valid, msg = validate_audit_duration("HIGH", "OnSite", 2.0)
        assert is_valid

    def test_high_risk_onsite_3days(self):
        """HIGH risk on-site: 3 days acceptable."""
        is_valid, msg = validate_audit_duration("HIGH", "OnSite", 3.0)
        assert is_valid

    def test_high_risk_onsite_1day_invalid(self):
        """HIGH risk on-site: 1 day insufficient."""
        is_valid, msg = validate_audit_duration("HIGH", "OnSite", 1.0)
        assert not is_valid

    def test_extremely_low_risk_onsite_half_day(self):
        """EXTREMELY_LOW risk on-site: 0.5 day acceptable."""
        is_valid, msg = validate_audit_duration("EXTREMELY_LOW", "OnSite", 0.5)
        assert is_valid

    def test_extremely_low_risk_onsite_1day(self):
        """EXTREMELY_LOW risk on-site: 1 day acceptable."""
        is_valid, msg = validate_audit_duration("EXTREMELY_LOW", "OnSite", 1.0)
        assert is_valid

    def test_extremely_low_risk_onsite_2days_invalid(self):
        """EXTREMELY_LOW risk on-site: 2 days too long."""
        is_valid, msg = validate_audit_duration("EXTREMELY_LOW", "OnSite", 2.0)
        assert not is_valid

    def test_low_risk_remote_valid(self):
        """LOW risk remote: 0.5-1 day acceptable (surveillance only)."""
        is_valid, msg = validate_audit_duration("LOW", "Remote", 0.5)
        assert is_valid

    def test_high_risk_remote_blocked(self):
        """HIGH risk remote: NOT ALLOWED per GSTC 8.5.12.8."""
        is_valid, msg = validate_audit_duration("HIGH", "Remote", 1.0)
        assert not is_valid
        assert "cannot be conducted remotely" in msg

    def test_missing_duration(self):
        """Missing duration rejected."""
        is_valid, msg = validate_audit_duration("LOW", "OnSite", None)
        assert not is_valid

    def test_missing_risk_level(self):
        """Missing risk level rejected."""
        is_valid, msg = validate_audit_duration(None, "OnSite", 1.0)
        assert not is_valid


class TestExtremelyLowRiskQualification:
    """GSTC 8.5.12.9: Extremely Low Risk Criteria"""

    def test_qualifies_all_criteria_met(self):
        """Qualifies when all 6 criteria are met."""
        is_qualified, reasons = validate_extremely_low_risk_qualification(
            guest_room_count=15,
            staff_count=10,
            has_event_spaces=False,
            has_function_spaces=False,
            has_meeting_spaces=False,
            is_local_ownership=True,
            has_internet_access=True,
            is_sensitive_area=False,
        )
        assert is_qualified
        assert len(reasons) == 0

    def test_fails_too_many_rooms(self):
        """Fails when guest rooms >= 20."""
        is_qualified, reasons = validate_extremely_low_risk_qualification(
            guest_room_count=20,
            staff_count=10,
            has_event_spaces=False,
            has_function_spaces=False,
            has_meeting_spaces=False,
            is_local_ownership=True,
            has_internet_access=True,
            is_sensitive_area=False,
        )
        assert not is_qualified
        assert any("rooms" in r for r in reasons)

    def test_fails_too_many_staff(self):
        """Fails when staff >= 15."""
        is_qualified, reasons = validate_extremely_low_risk_qualification(
            guest_room_count=15,
            staff_count=15,
            has_event_spaces=False,
            has_function_spaces=False,
            has_meeting_spaces=False,
            is_local_ownership=True,
            has_internet_access=True,
            is_sensitive_area=False,
        )
        assert not is_qualified
        assert any("Staff" in r for r in reasons)

    def test_fails_has_event_spaces(self):
        """Fails when has event spaces."""
        is_qualified, reasons = validate_extremely_low_risk_qualification(
            guest_room_count=15,
            staff_count=10,
            has_event_spaces=True,
            has_function_spaces=False,
            has_meeting_spaces=False,
            is_local_ownership=True,
            has_internet_access=True,
            is_sensitive_area=False,
        )
        assert not is_qualified
        assert any("event" in r.lower() for r in reasons)

    def test_fails_not_local_ownership(self):
        """Fails when not locally owned."""
        is_qualified, reasons = validate_extremely_low_risk_qualification(
            guest_room_count=15,
            staff_count=10,
            has_event_spaces=False,
            has_function_spaces=False,
            has_meeting_spaces=False,
            is_local_ownership=False,
            has_internet_access=True,
            is_sensitive_area=False,
        )
        assert not is_qualified
        assert any("local" in r.lower() for r in reasons)

    def test_fails_no_internet(self):
        """Fails when no internet access."""
        is_qualified, reasons = validate_extremely_low_risk_qualification(
            guest_room_count=15,
            staff_count=10,
            has_event_spaces=False,
            has_function_spaces=False,
            has_meeting_spaces=False,
            is_local_ownership=True,
            has_internet_access=False,
            is_sensitive_area=False,
        )
        assert not is_qualified
        assert any("internet" in r.lower() for r in reasons)

    def test_fails_sensitive_area(self):
        """Fails when in sensitive area."""
        is_qualified, reasons = validate_extremely_low_risk_qualification(
            guest_room_count=15,
            staff_count=10,
            has_event_spaces=False,
            has_function_spaces=False,
            has_meeting_spaces=False,
            is_local_ownership=True,
            has_internet_access=True,
            is_sensitive_area=True,
        )
        assert not is_qualified
        assert any("sensitive" in r.lower() for r in reasons)

    def test_multiple_failures(self):
        """Returns all failure reasons."""
        is_qualified, reasons = validate_extremely_low_risk_qualification(
            guest_room_count=25,
            staff_count=20,
            has_event_spaces=True,
            has_function_spaces=False,
            has_meeting_spaces=False,
            is_local_ownership=False,
            has_internet_access=False,
            is_sensitive_area=True,
        )
        assert not is_qualified
        assert len(reasons) >= 6


class TestSensitiveAreaAssignment:
    """GSTC 8.5.12.12-14: Sensitive Area Assessment"""

    def test_sensitive_area_requires_high_risk(self):
        """Sensitive area must be classified as HIGH RISK."""
        is_valid, msg = validate_sensitive_area_assignment(
            is_sensitive_area=True,
            sensitive_area_reason="UNESCO World Heritage Site",
            risk_level="HIGH"
        )
        assert is_valid

    def test_sensitive_area_not_high_risk_invalid(self):
        """Sensitive area assigned but risk level not HIGH - invalid."""
        is_valid, msg = validate_sensitive_area_assignment(
            is_sensitive_area=True,
            sensitive_area_reason="Ramsar Wetland",
            risk_level="LOW"
        )
        assert not is_valid
        assert "HIGH RISK" in msg

    def test_sensitive_area_requires_reason(self):
        """Sensitive area must have reason documented."""
        is_valid, msg = validate_sensitive_area_assignment(
            is_sensitive_area=True,
            sensitive_area_reason=None,
            risk_level="HIGH"
        )
        assert not is_valid
        assert "reason" in msg

    def test_sensitive_area_blank_reason_invalid(self):
        """Blank reason not acceptable."""
        is_valid, msg = validate_sensitive_area_assignment(
            is_sensitive_area=True,
            sensitive_area_reason="   ",
            risk_level="HIGH"
        )
        assert not is_valid

    def test_not_sensitive_area_any_risk(self):
        """Non-sensitive area can be any risk level."""
        is_valid, msg = validate_sensitive_area_assignment(
            is_sensitive_area=False,
            sensitive_area_reason=None,
            risk_level="LOW"
        )
        assert is_valid

    def test_not_sensitive_area_no_reason_required(self):
        """Non-sensitive area doesn't require reason."""
        is_valid, msg = validate_sensitive_area_assignment(
            is_sensitive_area=False,
            sensitive_area_reason=None,
            risk_level="EXTREMELY_LOW"
        )
        assert is_valid


class TestAuditSectionCoverage:
    """GSTC 8.5.19.5: Section Coverage Restrictions"""

    def test_remote_audit_allows_a(self):
        """Remote audit can cover section A."""
        is_valid, msg = validate_audit_section_coverage("Remote", ["A"])
        assert is_valid

    def test_remote_audit_allows_d1_d3(self):
        """Remote audit can cover D1 and D3."""
        is_valid, msg = validate_audit_section_coverage("Remote", ["A", "D1", "D3"])
        assert is_valid

    def test_remote_audit_blocks_b(self):
        """Remote audit cannot cover section B."""
        is_valid, msg = validate_audit_section_coverage("Remote", ["A", "B"])
        assert not is_valid
        assert "B" in msg

    def test_remote_audit_blocks_c(self):
        """Remote audit cannot cover section C."""
        is_valid, msg = validate_audit_section_coverage("Remote", ["A", "C"])
        assert not is_valid

    def test_onsite_audit_must_have_b_c_d3(self):
        """On-site audit must cover B, C, D3."""
        is_valid, msg = validate_audit_section_coverage("OnSite", ["A", "B", "C", "D3"])
        assert is_valid

    def test_onsite_audit_missing_b_invalid(self):
        """On-site audit missing section B - invalid."""
        is_valid, msg = validate_audit_section_coverage("OnSite", ["A", "C", "D3"])
        assert not is_valid
        assert "B" in msg

    def test_onsite_audit_missing_c_invalid(self):
        """On-site audit missing section C - invalid."""
        is_valid, msg = validate_audit_section_coverage("OnSite", ["A", "B", "D3"])
        assert not is_valid
        assert "C" in msg

    def test_onsite_audit_missing_d3_invalid(self):
        """On-site audit missing section D3 - invalid."""
        is_valid, msg = validate_audit_section_coverage("OnSite", ["A", "B", "C"])
        assert not is_valid
        assert "D3" in msg

    def test_no_sections_provided(self):
        """No sections provided - valid (optional)."""
        is_valid, msg = validate_audit_section_coverage("Remote", None)
        assert is_valid

    def test_empty_sections_list(self):
        """Empty sections list - valid (optional)."""
        is_valid, msg = validate_audit_section_coverage("OnSite", [])
        assert is_valid


class TestSurveillanceAuditDates:
    """GSTC 8.5.19.1: Surveillance Audit Timing"""

    def test_surveillance_within_12_months(self):
        """Surveillance audit within 12 months - valid."""
        today = date.today()
        last_audit = today - timedelta(days=300)  # ~10 months

        is_valid, reasons = validate_surveillance_audit_dates(
            "Surveillance",
            last_audit_date=last_audit,
            today=today
        )
        assert is_valid
        assert len(reasons) == 0

    def test_surveillance_exceeds_12_months(self):
        """Surveillance audit beyond 12 months - invalid."""
        today = date.today()
        last_audit = today - timedelta(days=400)  # ~13 months

        is_valid, reasons = validate_surveillance_audit_dates(
            "Surveillance",
            last_audit_date=last_audit,
            today=today
        )
        assert not is_valid
        assert any("12" in r for r in reasons)

    def test_onsite_within_24_months(self):
        """On-site audit within 24 months - valid."""
        today = date.today()
        last_onsite = today - timedelta(days=600)  # ~20 months

        is_valid, reasons = validate_surveillance_audit_dates(
            "Surveillance",
            last_on_site_audit_date=last_onsite,
            today=today
        )
        assert is_valid

    def test_onsite_exceeds_24_months(self):
        """On-site audit beyond 24 months - invalid."""
        today = date.today()
        last_onsite = today - timedelta(days=800)  # ~27 months

        is_valid, reasons = validate_surveillance_audit_dates(
            "Surveillance",
            last_on_site_audit_date=last_onsite,
            today=today
        )
        assert not is_valid
        assert any("24" in r for r in reasons)

    def test_both_windows_valid(self):
        """Both audit windows within limits - valid."""
        today = date.today()
        last_audit = today - timedelta(days=300)  # ~10 months
        last_onsite = today - timedelta(days=600)  # ~20 months

        is_valid, reasons = validate_surveillance_audit_dates(
            "Surveillance",
            last_on_site_audit_date=last_onsite,
            last_audit_date=last_audit,
            today=today
        )
        assert is_valid

    def test_no_previous_audit_dates(self):
        """No previous audit dates - valid (initial audit)."""
        is_valid, reasons = validate_surveillance_audit_dates(
            "Surveillance",
            last_on_site_audit_date=None,
            last_audit_date=None
        )
        assert is_valid

    def test_initial_audit_type_always_valid(self):
        """Initial audit type doesn't need surveillance windows."""
        today = date.today()
        old_date = today - timedelta(days=1000)  # Well beyond windows

        is_valid, reasons = validate_surveillance_audit_dates(
            "Initial",
            last_on_site_audit_date=old_date,
            last_audit_date=old_date,
            today=today
        )
        assert is_valid


class TestValidationIntegration:
    """Integration tests combining multiple validators."""

    def test_low_risk_hotel_scenario(self):
        """Complete scenario: LOW risk hotel with proper duration."""
        # Risk level validation
        risk_valid, _ = validate_risk_level("LOW", country_corruption_index=70, has_negative_impacts=False)
        assert risk_valid

        # Duration validation
        duration_valid, _ = validate_audit_duration("LOW", "OnSite", 1.0)
        assert duration_valid

        # Extremely low risk doesn't apply to LOW risk
        extremely_low_valid, reasons = validate_extremely_low_risk_qualification(
            guest_room_count=50,  # >20, so doesn't qualify
            staff_count=30,
            has_event_spaces=True,
            has_function_spaces=False,
            has_meeting_spaces=False,
            is_local_ownership=False,
            has_internet_access=True,
            is_sensitive_area=False,
        )
        assert not extremely_low_valid

    def test_extremely_low_risk_scenario(self):
        """Complete scenario: EXTREMELY_LOW risk hotel qualifies."""
        # All criteria met
        extremely_low_valid, reasons = validate_extremely_low_risk_qualification(
            guest_room_count=12,
            staff_count=8,
            has_event_spaces=False,
            has_function_spaces=False,
            has_meeting_spaces=False,
            is_local_ownership=True,
            has_internet_access=True,
            is_sensitive_area=False,
        )
        assert extremely_low_valid

        # Duration validation
        duration_valid, _ = validate_audit_duration("EXTREMELY_LOW", "OnSite", 0.5)
        assert duration_valid

        # Remote audit allowed for extremely low risk
        remote_valid, _ = validate_audit_duration("EXTREMELY_LOW", "Remote", 0.5)
        assert remote_valid

    def test_sensitive_area_scenario(self):
        """Complete scenario: Sensitive area assessment."""
        # Sensitive area identified
        sensitive_valid, _ = validate_sensitive_area_assignment(
            is_sensitive_area=True,
            sensitive_area_reason="IUCN Protected Area - Category II",
            risk_level="HIGH"
        )
        assert sensitive_valid

        # Must be HIGH risk
        duration_valid, _ = validate_audit_duration("HIGH", "OnSite", 2.5)
        assert duration_valid

        # Remote not allowed for HIGH risk
        remote_invalid, msg = validate_audit_duration("HIGH", "Remote", 1.0)
        assert not remote_invalid
