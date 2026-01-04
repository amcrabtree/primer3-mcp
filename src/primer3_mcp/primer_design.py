"""Primer3 integration for primer design."""

from typing import Dict, Any, Optional
import primer3

from .models import PrimerDesignInput, PrimerDesignOutput, PrimerPair, PrimerInfo
from .utils import parse_sequence_with_target, validate_dna_sequence


def design_primers_with_protocol(input_data: PrimerDesignInput) -> PrimerDesignOutput:
    """
    Design primers using Primer3 with lab protocol parameters.

    Args:
        input_data: Primer design input parameters

    Returns:
        PrimerDesignOutput with ranked primer pairs

    Raises:
        ValueError: If sequence is invalid or missing [n] placeholder
    """
    # Parse sequence and extract target region
    cleaned_sequence, (target_start, target_length) = parse_sequence_with_target(
        input_data.sequence
    )

    # Validate DNA sequence
    validate_dna_sequence(cleaned_sequence)

    # Build Primer3 sequence arguments
    # Use SEQUENCE_TARGET to mark the region to amplify
    seq_args = {
        "SEQUENCE_ID": "input_sequence",
        "SEQUENCE_TEMPLATE": cleaned_sequence,
        "SEQUENCE_TARGET": [target_start, target_length],
    }

    # Calculate product size range based on template length
    # Allow flexible product sizes from 100bp to full template
    min_product = 100
    max_product = min(len(cleaned_sequence), 1000)

    # Build Primer3 global arguments with protocol parameters
    global_args = {
        "PRIMER_OPT_SIZE": input_data.primer_size_opt,
        "PRIMER_MIN_SIZE": input_data.primer_size_min,
        "PRIMER_MAX_SIZE": input_data.primer_size_max,
        "PRIMER_OPT_TM": input_data.primer_tm_opt,
        "PRIMER_MIN_TM": input_data.primer_tm_min,
        "PRIMER_MAX_TM": input_data.primer_tm_max,
        "PRIMER_MIN_GC": 20.0,
        "PRIMER_MAX_GC": 80.0,
        "PRIMER_GC_CLAMP": input_data.gc_clamp,
        "PRIMER_NUM_RETURN": input_data.num_return,
        "PRIMER_PRODUCT_SIZE_RANGE": [[min_product, max_product]],
    }

    # Call Primer3
    results = primer3.bindings.design_primers(seq_args, global_args)

    # Parse results
    pairs = parse_primer3_results(results)

    return PrimerDesignOutput(
        pairs=pairs, num_returned=len(pairs), troubleshooting_applied=None
    )


def parse_primer3_results(results: Dict[str, Any]) -> list[PrimerPair]:
    """
    Parse Primer3 results into PrimerPair objects.

    Args:
        results: Raw Primer3 output dictionary

    Returns:
        List of PrimerPair objects, ranked by quality
    """
    num_returned = results.get("PRIMER_PAIR_NUM_RETURNED", 0)
    pairs = []

    for i in range(num_returned):
        # Extract left primer info
        left_start = results[f"PRIMER_LEFT_{i}"][0]
        left_length = results[f"PRIMER_LEFT_{i}"][1]
        left_tm = results[f"PRIMER_LEFT_{i}_TM"]
        left_gc = results[f"PRIMER_LEFT_{i}_GC_PERCENT"]
        left_self_any = results[f"PRIMER_LEFT_{i}_SELF_ANY_TH"]
        left_self_end = results[f"PRIMER_LEFT_{i}_SELF_END_TH"]
        left_seq = results[f"PRIMER_LEFT_{i}_SEQUENCE"]

        # Extract right primer info
        right_start = results[f"PRIMER_RIGHT_{i}"][0]
        right_length = results[f"PRIMER_RIGHT_{i}"][1]
        right_tm = results[f"PRIMER_RIGHT_{i}_TM"]
        right_gc = results[f"PRIMER_RIGHT_{i}_GC_PERCENT"]
        right_self_any = results[f"PRIMER_RIGHT_{i}_SELF_ANY_TH"]
        right_self_end = results[f"PRIMER_RIGHT_{i}_SELF_END_TH"]
        right_seq = results[f"PRIMER_RIGHT_{i}_SEQUENCE"]

        # Extract pair info
        product_size = results[f"PRIMER_PAIR_{i}_PRODUCT_SIZE"]
        penalty = results[f"PRIMER_PAIR_{i}_PENALTY"]

        # Note: rep (mispriming) may not always be present
        left_rep = results.get(f"PRIMER_LEFT_{i}_LIBRARY_MISPRIMING", 0.0)
        right_rep = results.get(f"PRIMER_RIGHT_{i}_LIBRARY_MISPRIMING", 0.0)

        # Build PrimerInfo objects
        left_primer = PrimerInfo(
            start=left_start,
            length=left_length,
            tm=left_tm,
            gc_percent=left_gc,
            self_any=left_self_any,
            self_end=left_self_end,
            rep=left_rep,
            sequence=left_seq,
        )

        right_primer = PrimerInfo(
            start=right_start,
            length=right_length,
            tm=right_tm,
            gc_percent=right_gc,
            self_any=right_self_any,
            self_end=right_self_end,
            rep=right_rep,
            sequence=right_seq,
        )

        # Build PrimerPair object
        pair = PrimerPair(
            pair_id=i,
            left_primer=left_primer,
            right_primer=right_primer,
            product_size=product_size,
            penalty=penalty,
        )

        pairs.append(pair)

    return pairs


def design_primers_with_retry(input_data: PrimerDesignInput) -> PrimerDesignOutput:
    """
    Design primers with automatic troubleshooting retry logic.

    Follows lab protocol step 7:
    1. Try with gc_clamp=2
    2. If no results, retry with gc_clamp=1
    3. If no results, retry with gc_clamp=0
    4. If no results, widen Tm by ±1°C

    Args:
        input_data: Primer design input parameters

    Returns:
        PrimerDesignOutput with troubleshooting information
    """
    troubleshooting_steps = []

    # Try with original gc_clamp
    result = design_primers_with_protocol(input_data)
    if result.num_returned > 0:
        return result

    # Retry with gc_clamp=1
    if input_data.gc_clamp > 1:
        troubleshooting_steps.append("Reduced GC clamp to 1")
        modified_input = input_data.model_copy(update={"gc_clamp": 1})
        result = design_primers_with_protocol(modified_input)
        if result.num_returned > 0:
            result.troubleshooting_applied = "; ".join(troubleshooting_steps)
            return result

    # Retry with gc_clamp=0
    if input_data.gc_clamp > 0:
        troubleshooting_steps.append("Reduced GC clamp to 0")
        modified_input = input_data.model_copy(update={"gc_clamp": 0})
        result = design_primers_with_protocol(modified_input)
        if result.num_returned > 0:
            result.troubleshooting_applied = "; ".join(troubleshooting_steps)
            return result

    # Retry with widened Tm (±1°C)
    troubleshooting_steps.append("Widened Tm range by ±1°C")
    modified_input = input_data.model_copy(
        update={
            "gc_clamp": 0,
            "primer_tm_min": input_data.primer_tm_min - 1.0,
            "primer_tm_max": input_data.primer_tm_max + 1.0,
        }
    )
    result = design_primers_with_protocol(modified_input)
    if result.num_returned > 0:
        result.troubleshooting_applied = "; ".join(troubleshooting_steps)
        return result

    # If still no results, return empty with troubleshooting info
    result.troubleshooting_applied = (
        "; ".join(troubleshooting_steps)
        + "; No primers found - consider wider sequence search area"
    )
    return result
