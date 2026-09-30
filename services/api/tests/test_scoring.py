"""Tests for the severity scoring engine."""
import pytest
from app.utils.scoring import calculate_severity_score, score_to_colour, ACTION_DUE_DAYS


def test_excellent_low():
    assert calculate_severity_score("Excellent", "Low") == 1


def test_excellent_critical():
    assert calculate_severity_score("Excellent", "Critical") == 4


def test_good_high():
    assert calculate_severity_score("Good", "High") == 6


def test_ok_critical():
    assert calculate_severity_score("OK", "Critical") == 12


def test_poor_critical():
    assert calculate_severity_score("Poor", "Critical") == 16


def test_colour_green():
    assert score_to_colour(1) == "green"
    assert score_to_colour(2) == "green"


def test_colour_yellow():
    assert score_to_colour(4) == "yellow"


def test_colour_orange():
    assert score_to_colour(9) == "orange"


def test_colour_red():
    assert score_to_colour(16) == "red"


def test_major_nc_due_days():
    assert ACTION_DUE_DAYS["MajorNC"] == 90


def test_minor_nc_due_days():
    assert ACTION_DUE_DAYS["MinorNC"] == 30
