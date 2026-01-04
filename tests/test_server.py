"""Tests for MCP server tools."""

import pytest
from primer3_mcp.models import PrimerDesignInput
from primer3_mcp.primer_design import design_primers_with_protocol, design_primers_with_retry
from tests.fixtures.test_sequences import LAB_PROTOCOL_SEQUENCE


def test_design_primers_tool():
    """Test design_primers tool with valid input."""
    input_data = PrimerDesignInput(sequence=LAB_PROTOCOL_SEQUENCE)
    result = design_primers_with_protocol(input_data)

    assert hasattr(result, "pairs")
    assert hasattr(result, "num_returned")
    assert result.num_returned > 0


def test_design_primers_with_custom_parameters():
    """Test design_primers with custom parameters."""
    input_data = PrimerDesignInput(
        sequence=LAB_PROTOCOL_SEQUENCE,
        primer_size_min=22,
        primer_size_opt=27,
        primer_size_max=32,
        gc_clamp=1,
        num_return=3,
    )
    result = design_primers_with_protocol(input_data)

    assert result.num_returned <= 3  # Should respect num_return limit


def test_design_primers_invalid_sequence():
    """Test design_primers with invalid sequence (no placeholder)."""
    with pytest.raises(ValueError, match="must contain \\[n\\] placeholder"):
        PrimerDesignInput(sequence="ATGCATGC")


def test_troubleshoot_design_tool():
    """Test troubleshoot_design tool."""
    input_data = PrimerDesignInput(sequence=LAB_PROTOCOL_SEQUENCE)
    result = design_primers_with_retry(input_data)

    assert hasattr(result, "pairs")
    assert hasattr(result, "num_returned")
    assert hasattr(result, "troubleshooting_applied")


def test_troubleshoot_design_difficult_sequence():
    """Test troubleshoot_design with a sequence that may need relaxed constraints."""
    # Longer sequence but with challenging characteristics for primer design
    # Repetitive, low complexity - difficult for primer design
    difficult_seq = "AAAAAAAAAA" * 5 + "[n]" + "TTTTTTTTTT" * 5
    input_data = PrimerDesignInput(sequence=difficult_seq)

    result = design_primers_with_retry(input_data)

    # Even if no primers found, should return structure with troubleshooting info
    assert hasattr(result, "troubleshooting_applied")
