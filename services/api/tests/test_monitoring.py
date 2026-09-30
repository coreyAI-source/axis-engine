"""Tests for the monitoring engine service."""
import pytest
from datetime import date
from dateutil.relativedelta import relativedelta

from app.services.monitoring import calculate_next_due_date


def test_next_due_date_annual():
    base = date(2026, 1, 15)
    result = calculate_next_due_date(base, 12)
    assert result == date(2027, 1, 15)


def test_next_due_date_quarterly():
    base = date(2026, 1, 15)
    result = calculate_next_due_date(base, 3)
    assert result == date(2026, 4, 15)


def test_next_due_date_monthly():
    base = date(2026, 1, 31)
    result = calculate_next_due_date(base, 1)
    # Feb doesn't have 31 days — relativedelta handles this correctly
    assert result == date(2026, 2, 28)


def test_next_due_date_biannual():
    base = date(2026, 6, 30)
    result = calculate_next_due_date(base, 6)
    assert result == date(2026, 12, 30)
