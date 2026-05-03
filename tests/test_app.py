"""
tests/test_app.py
Unit tests for VoteWise core logic functions.
Run with: python -m pytest tests/ -v
"""

import sys
import os

# Make project root importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import (
    calculate_timeline_gap,
    generate_reasons,
    calculate_voting_status,
    REGISTRATION_DAYS,
    ELECTION_DAYS_REMAINING,
    AREA_DATA,
)


# ------------------------------------------------------------------
# calculate_timeline_gap
# ------------------------------------------------------------------

def test_timeline_gap_positive():
    """Registration takes longer than days remaining → positive gap (at risk)."""
    assert calculate_timeline_gap(5, 3) == 2


def test_timeline_gap_zero():
    """Equal days → gap is 0."""
    assert calculate_timeline_gap(5, 5) == 0


def test_timeline_gap_negative():
    """More days remaining than registration takes → user still has time."""
    assert calculate_timeline_gap(3, 5) == -2


# ------------------------------------------------------------------
# generate_reasons (no Gemini, use_gemini=False)
# ------------------------------------------------------------------

def test_reasons_underage():
    """Age < 18 should produce 'not eligible' reasons."""
    gap = calculate_timeline_gap(REGISTRATION_DAYS, ELECTION_DAYS_REMAINING)
    reasons = generate_reasons(16, False, gap, REGISTRATION_DAYS, ELECTION_DAYS_REMAINING, use_gemini=False)
    assert any("18" in r for r in reasons), "Should mention the 18-year threshold"


def test_reasons_registered_voter():
    """Registered adult → positive confirmation reasons."""
    gap = calculate_timeline_gap(REGISTRATION_DAYS, ELECTION_DAYS_REMAINING)
    reasons = generate_reasons(25, True, gap, REGISTRATION_DAYS, ELECTION_DAYS_REMAINING, use_gemini=False)
    assert any("registered" in r.lower() for r in reasons)


def test_reasons_unregistered_high_gap():
    """Unregistered adult with gap > 0 → at-risk reasons."""
    gap = calculate_timeline_gap(5, 3)  # gap = 2
    reasons = generate_reasons(30, False, gap, 5, 3, use_gemini=False)
    assert any("short" in r.lower() or "days" in r.lower() for r in reasons)


# ------------------------------------------------------------------
# calculate_voting_status
# ------------------------------------------------------------------

def _first_state():
    """Helper: returns the first valid state and its first district."""
    state = list(AREA_DATA.keys())[0]
    district = list(AREA_DATA[state].keys())[0]
    return state, district


def test_status_underage():
    """Age < 18 → Not Eligible verdict."""
    state, district = _first_state()
    result = calculate_voting_status(15, False, state, district)
    assert result["is_ready"] is False
    assert "Not Eligible" in result["tag"]
    assert result["verdict_class"] == "red"


def test_status_registered_adult():
    """Registered adult → Can Vote verdict."""
    state, district = _first_state()
    result = calculate_voting_status(30, True, state, district)
    assert result["is_ready"] is True
    assert "Ready Voter" in result["tag"]
    assert result["verdict_class"] == "green"


def test_status_unregistered_low_time():
    """Unregistered adult with REGISTRATION_DAYS > ELECTION_DAYS_REMAINING → At Risk."""
    state, district = _first_state()
    result = calculate_voting_status(25, False, state, district)
    assert result["is_ready"] is False
    assert result["gap"] > 0
    assert result["timeline_mismatch"] is True


def test_status_gap_calculation():
    """Gap in result matches constants."""
    state, district = _first_state()
    result = calculate_voting_status(22, False, state, district)
    expected_gap = REGISTRATION_DAYS - ELECTION_DAYS_REMAINING
    assert result["gap"] == expected_gap


def test_status_area_info_included():
    """Result should carry correct area info."""
    state, district = _first_state()
    result = calculate_voting_status(20, True, state, district)
    assert result["area_info"]["State"] == state
    assert result["area_info"]["District"] == district


def test_status_reasons_not_empty():
    """Reasons list must always be non-empty."""
    state, district = _first_state()
    for age, registered in [(10, False), (25, True), (25, False)]:
        result = calculate_voting_status(age, registered, state, district)
        assert len(result["reasons"]) > 0, f"Empty reasons for age={age}, registered={registered}"


# ------------------------------------------------------------------
# Input-validation edge cases (via calculate_voting_status directly)
# ------------------------------------------------------------------

def test_unknown_state_fallback():
    """Unknown state → area_info shows Unknown MLA/MP."""
    result = calculate_voting_status(25, True, "Fake State", "Fake District")
    assert result["area_info"]["MLA"] == "Unknown"
    assert result["area_info"]["MP"] == "Unknown"
