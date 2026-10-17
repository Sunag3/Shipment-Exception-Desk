"""
pytest test file for the Shipment Exception & Triage Desk pipeline.
Run with:  pytest test_triage_check.py -v
"""

import pytest
from pipeline import process_exception
from session import DAILY_LOG


@pytest.fixture(autouse=True)
def clear_log():
    """Clear the daily log before every test."""
    DAILY_LOG.clear()
    yield
    DAILY_LOG.clear()


def test_force_majeure_delay():
    """
    Delay caused by weather + customs → delayed, compensation = $0, no approval needed
    """
    result = process_exception(
        report_text="The shipment was delayed by 4 days due to severe winter storms and a regional customs hold at the port terminal",
        shipment_value=500.0,
        customer_tier="standard"
    )

    assert result["category"] == "delayed"
    assert result["compensation"] == 0.0
    assert result["needs_approval"] is False          # ← changed
    assert any(word in result["compensation_reason"].lower() 
               for word in ["force majeure", "weather", "customs", "exempt"])


def test_normal_delay_compensation():
    """
    Normal carrier delay (3 days) on $800 shipment → 3% compensation = $24
    """
    result = process_exception(
        report_text="The package was delayed by 3 days due to carrier operational issues",
        shipment_value=800.0,
        customer_tier="standard"
    )

    assert result["category"] == "delayed"
    assert result["compensation"] == 24.0          # 3 days * 1%
    assert result["needs_approval"] is False


def test_severe_damage():
    """
    Total loss / destroyed → 100% compensation
    """
    result = process_exception(
        report_text="The box arrived crushed and the contents are completely destroyed and unusable",
        shipment_value=1200.0,
        customer_tier="premier"
    )

    assert result["category"] == "damaged"
    assert result["compensation"] == 1200.0
    assert result["needs_approval"] is True         # > premier threshold ($100)


def test_lost_shipment():
    """
    Confirmed lost → full value compensation
    """
    result = process_exception(
        report_text="The shipment is missing and has been marked as lost by the carrier. It was never delivered.",
        shipment_value=450.0,
        customer_tier="standard"
    )

    assert result["category"] == "lost"
    assert result["compensation"] == 450.0
    assert result["needs_approval"] is True         # > standard threshold ($200)


def test_unknown_vague_report():
    """
    Vague report → should fall into unknown and escalate
    """
    result = process_exception(
        report_text="Something went wrong with my delivery last week",
        shipment_value=300.0,
        customer_tier="standard"
    )

    assert result["category"] == "unknown"
    assert result["compensation"] == 0.0
    assert result["needs_approval"] is True