"""Tests for primer design functionality."""

import pytest
from primer3_mcp.models import PrimerDesignInput
from primer3_mcp.utils import parse_sequence_with_target, validate_dna_sequence
from primer3_mcp.primer_design import design_primers_with_protocol
from tests.fixtures.test_sequences import LAB_PROTOCOL_SEQUENCE


def test_parse_sequence_with_target():
    """Test parsing sequence with [n] placeholder."""
    sequence = "ATGC[n]GCTA"
    cleaned, (start, length) = parse_sequence_with_target(sequence)

    assert cleaned == "ATGCGCTA"
    assert start == 4
    assert length == 1


def test_parse_sequence_case_insensitive():
    """Test [n] placeholder is case-insensitive."""
    sequence = "ATGC[N]GCTA"
    cleaned, (start, length) = parse_sequence_with_target(sequence)

    assert cleaned == "ATGCGCTA"
    assert start == 4


def test_parse_sequence_missing_placeholder():
    """Test error when [n] placeholder is missing."""
    sequence = "ATGCGCTA"
    with pytest.raises(ValueError, match="must contain \\[n\\] placeholder"):
        parse_sequence_with_target(sequence)


def test_validate_dna_sequence_valid():
    """Test validation of valid DNA sequence."""
    validate_dna_sequence("ATGCATGCN")  # Should not raise


def test_validate_dna_sequence_invalid():
    """Test validation rejects invalid characters."""
    with pytest.raises(ValueError, match="invalid characters"):
        validate_dna_sequence("ATGCXYZ")


def test_primer_design_input_validation():
    """Test PrimerDesignInput model validation."""
    # Valid input
    input_data = PrimerDesignInput(sequence="ATGC[n]GCTA")
    assert input_data.primer_size_opt == 25  # Default value

    # Missing placeholder
    with pytest.raises(ValueError, match="must contain \\[n\\] placeholder"):
        PrimerDesignInput(sequence="ATGCGCTA")


def test_primer_design_with_lab_protocol_sequence():
    """Test primer design with the lab protocol example sequence."""
    input_data = PrimerDesignInput(sequence=LAB_PROTOCOL_SEQUENCE)

    result = design_primers_with_protocol(input_data)

    # Should return at least one primer pair
    assert result.num_returned > 0
    assert len(result.pairs) > 0

    # Check first pair structure
    first_pair = result.pairs[0]
    assert first_pair.pair_id == 0
    assert first_pair.left_primer.sequence != ""
    assert first_pair.right_primer.sequence != ""
    assert first_pair.product_size > 0

    # Verify 10 features are present for left primer
    assert hasattr(first_pair.left_primer, "start")
    assert hasattr(first_pair.left_primer, "length")
    assert hasattr(first_pair.left_primer, "tm")
    assert hasattr(first_pair.left_primer, "gc_percent")
    assert hasattr(first_pair.left_primer, "self_any")
    assert hasattr(first_pair.left_primer, "self_end")
    assert hasattr(first_pair.left_primer, "rep")
    assert hasattr(first_pair.left_primer, "sequence")
