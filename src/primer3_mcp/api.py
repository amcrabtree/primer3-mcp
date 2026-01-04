"""Public API for primer3-mcp library usage."""

from .models import PrimerDesignInput, PrimerDesignOutput
from .primer_design import (
    design_primers_with_protocol,
    design_primers_with_retry,
)


def design_primers(
    sequence: str,
    primer_size_min: int = 20,
    primer_size_opt: int = 25,
    primer_size_max: int = 30,
    primer_tm_min: float = 64.0,
    primer_tm_opt: float = 65.0,
    primer_tm_max: float = 66.0,
    gc_clamp: int = 2,
    num_return: int = 5,
) -> PrimerDesignOutput:
    """
    Design PCR primers following lab protocol.

    Input sequence must contain [n] placeholder marking the target region.
    Returns ranked primer pairs with complete primer information.

    Args:
        sequence: DNA sequence with [n] placeholder for target region
        primer_size_min: Minimum primer size in bp (default: 20)
        primer_size_opt: Optimal primer size in bp (default: 25)
        primer_size_max: Maximum primer size in bp (default: 30)
        primer_tm_min: Minimum melting temperature in °C (default: 64)
        primer_tm_opt: Optimal melting temperature in °C (default: 65)
        primer_tm_max: Maximum melting temperature in °C (default: 66)
        gc_clamp: Number of G/C bases at 3' end (default: 2)
        num_return: Number of primer pairs to return (default: 5)

    Returns:
        PrimerDesignOutput with ranked primer pairs. Access via:
        - result.pairs: List of PrimerPair objects
        - result.num_returned: Number of pairs found
        - result.pairs[0].left_primer.sequence: Top primer sequence

    Raises:
        ValueError: If sequence is invalid or missing [n] placeholder

    Example:
        >>> from primer3_mcp import design_primers
        >>> seq = "GGGTCAGG...ATCT[n]ACTAGT...GAGGT"
        >>> result = design_primers(sequence=seq, num_return=3)
        >>> for pair in result.pairs:
        ...     print(f"Pair {pair.pair_id}: {pair.product_size}bp")
        ...     print(f"  Left:  {pair.left_primer.sequence}")
        ...     print(f"  Right: {pair.right_primer.sequence}")
    """
    input_data = PrimerDesignInput(
        sequence=sequence,
        primer_size_min=primer_size_min,
        primer_size_opt=primer_size_opt,
        primer_size_max=primer_size_max,
        primer_tm_min=primer_tm_min,
        primer_tm_opt=primer_tm_opt,
        primer_tm_max=primer_tm_max,
        gc_clamp=gc_clamp,
        num_return=num_return,
    )

    return design_primers_with_protocol(input_data)


def troubleshoot_primers(
    sequence: str,
    num_return: int = 5,
) -> PrimerDesignOutput:
    """
    Auto-retry primer design with progressively relaxed constraints.

    Follows lab protocol troubleshooting steps:
    1. Try with GC clamp = 2 (default)
    2. If no results, reduce GC clamp to 1
    3. If no results, reduce GC clamp to 0
    4. If no results, widen Tm range by ±1°C

    Returns detailed feedback on which troubleshooting steps were applied.

    Args:
        sequence: DNA sequence with [n] placeholder for target region
        num_return: Number of primer pairs to return (default: 5)

    Returns:
        PrimerDesignOutput with primer pairs and troubleshooting info.
        Access result.troubleshooting_applied for steps taken.

    Raises:
        ValueError: If sequence is invalid or missing [n] placeholder

    Example:
        >>> from primer3_mcp import troubleshoot_primers
        >>> difficult_seq = "ATATATAT...[n]...GCGCGCGC"
        >>> result = troubleshoot_primers(sequence=difficult_seq)
        >>> if result.num_returned > 0:
        ...     print(f"Found {result.num_returned} pairs")
        ...     if result.troubleshooting_applied:
        ...         print(f"Applied: {result.troubleshooting_applied}")
    """
    input_data = PrimerDesignInput(
        sequence=sequence,
        num_return=num_return,
    )

    return design_primers_with_retry(input_data)
