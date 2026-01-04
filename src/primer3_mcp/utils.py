"""Utility functions for sequence processing."""

import re
from typing import Tuple


def parse_sequence_with_target(sequence: str) -> Tuple[str, Tuple[int, int]]:
    """
    Parse DNA sequence containing [n] placeholder for target region.

    Args:
        sequence: DNA sequence with [n] placeholder marking target region

    Returns:
        Tuple of (cleaned_sequence, (target_start, target_length))
        - cleaned_sequence: Sequence with [n] removed
        - target_start: 0-indexed position where [n] was located
        - target_length: Set to 1 (single base placeholder)

    Raises:
        ValueError: If [n] placeholder not found
    """
    # Case-insensitive search for [n]
    match = re.search(r"\[n\]", sequence, re.IGNORECASE)
    if not match:
        raise ValueError("Sequence must contain [n] placeholder for target region")

    # Get position of [n]
    target_start = match.start()

    # Remove [n] from sequence
    cleaned_sequence = sequence[: match.start()] + sequence[match.end() :]

    # Target length is 1 (placeholder for single position)
    target_length = 1

    return cleaned_sequence, (target_start, target_length)


def validate_dna_sequence(sequence: str) -> None:
    """
    Validate that sequence contains only valid DNA bases.

    Args:
        sequence: DNA sequence to validate

    Raises:
        ValueError: If sequence contains invalid characters
    """
    # Allow ATGCN characters (N is ambiguous base)
    valid_pattern = re.compile(r"^[ATGCNatgcn]+$")

    if not valid_pattern.match(sequence):
        invalid_chars = set(sequence) - set("ATGCNatgcn")
        raise ValueError(
            f"Sequence contains invalid characters: {', '.join(sorted(invalid_chars))}. "
            f"Only ATGCN bases are allowed."
        )
