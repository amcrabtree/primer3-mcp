"""Data models for Primer3 primer design."""

from typing import Optional
from pydantic import BaseModel, Field, field_validator


class PrimerDesignInput(BaseModel):
    """Input parameters for primer design following lab protocol."""

    sequence: str = Field(..., description="DNA sequence with [n] placeholder for target region")
    primer_size_min: int = Field(20, description="Minimum primer size in base pairs")
    primer_size_opt: int = Field(25, description="Optimal primer size in base pairs")
    primer_size_max: int = Field(30, description="Maximum primer size in base pairs")
    primer_tm_min: float = Field(64.0, description="Minimum melting temperature in °C")
    primer_tm_opt: float = Field(65.0, description="Optimal melting temperature in °C")
    primer_tm_max: float = Field(66.0, description="Maximum melting temperature in °C")
    gc_clamp: int = Field(2, description="Number of G/C bases at 3' end")
    num_return: int = Field(5, description="Number of primer pairs to return")

    @field_validator("sequence")
    @classmethod
    def validate_sequence_has_placeholder(cls, v: str) -> str:
        """Ensure sequence contains [n] placeholder."""
        if "[n]" not in v.lower():
            raise ValueError("Sequence must contain [n] placeholder for target region")
        return v

    @field_validator("primer_size_max")
    @classmethod
    def validate_size_range(cls, v: int, info) -> int:
        """Ensure size max > opt > min."""
        if "primer_size_min" in info.data and v <= info.data["primer_size_min"]:
            raise ValueError("primer_size_max must be greater than primer_size_min")
        if "primer_size_opt" in info.data and v < info.data["primer_size_opt"]:
            raise ValueError("primer_size_max must be >= primer_size_opt")
        return v

    @field_validator("primer_tm_max")
    @classmethod
    def validate_tm_range(cls, v: float, info) -> float:
        """Ensure Tm max > opt > min."""
        if "primer_tm_min" in info.data and v <= info.data["primer_tm_min"]:
            raise ValueError("primer_tm_max must be greater than primer_tm_min")
        if "primer_tm_opt" in info.data and v < info.data["primer_tm_opt"]:
            raise ValueError("primer_tm_max must be >= primer_tm_opt")
        return v


class PrimerInfo(BaseModel):
    """Information about a single primer (10 features per protocol)."""

    start: int = Field(..., description="Position of 5' base")
    length: int = Field(..., description="Oligonucleotide length")
    tm: float = Field(..., description="Melting temperature in °C")
    gc_percent: float = Field(..., description="GC content percentage")
    self_any: float = Field(..., description="Self-complementarity score")
    self_end: float = Field(..., description="3' self-complementarity (primer-dimer tendency)")
    rep: float = Field(..., description="Mispriming/Mishyb library similarity")
    sequence: str = Field(..., description="Primer sequence (5'→3')")

    def __str__(self) -> str:
        """Human-readable primer summary for notebooks."""
        return (
            f"Primer: {self.sequence} | "
            f"Tm: {self.tm:.1f}°C | "
            f"GC: {self.gc_percent:.1f}% | "
            f"Length: {self.length}bp"
        )


class PrimerPair(BaseModel):
    """A pair of left and right primers."""

    pair_id: int = Field(..., description="Pair rank (0-indexed, 0 is best)")
    left_primer: PrimerInfo = Field(..., description="Left primer information")
    right_primer: PrimerInfo = Field(..., description="Right primer information")
    product_size: int = Field(..., description="Amplicon size in base pairs")
    penalty: float = Field(..., description="Primer pair penalty score (lower is better)")

    def __str__(self) -> str:
        """Human-readable pair summary for notebooks."""
        return (
            f"Pair {self.pair_id}: {self.product_size}bp product | "
            f"Penalty: {self.penalty:.2f}\n"
            f"  Left:  {self.left_primer.sequence} (Tm: {self.left_primer.tm:.1f}°C)\n"
            f"  Right: {self.right_primer.sequence} (Tm: {self.right_primer.tm:.1f}°C)"
        )


class PrimerDesignOutput(BaseModel):
    """Output from primer design process."""

    pairs: list[PrimerPair] = Field(default_factory=list, description="Ranked primer pairs")
    num_returned: int = Field(..., description="Number of primer pairs returned")
    troubleshooting_applied: Optional[str] = Field(
        None, description="Troubleshooting steps applied (if any)"
    )

    def __str__(self) -> str:
        """Human-readable output summary for notebooks."""
        summary = f"Primer Design Results: {self.num_returned} pairs found"
        if self.troubleshooting_applied:
            summary += f"\nTroubleshooting: {self.troubleshooting_applied}"
        return summary

    def to_dataframe(self):
        """
        Convert primer pairs to pandas DataFrame for analysis.

        Returns:
            pandas.DataFrame with one row per primer pair

        Raises:
            ImportError: If pandas is not installed

        Example:
            >>> result = design_primers(sequence=seq)
            >>> df = result.to_dataframe()
            >>> df[['product_size', 'penalty']].sort_values('penalty')
        """
        try:
            import pandas as pd
        except ImportError as e:
            raise ImportError(
                "pandas is required for to_dataframe(). "
                "Install with: pip install primer3-mcp[analysis]"
            ) from e

        rows = []
        for pair in self.pairs:
            rows.append({
                'pair_id': pair.pair_id,
                'product_size': pair.product_size,
                'penalty': pair.penalty,
                'left_start': pair.left_primer.start,
                'left_length': pair.left_primer.length,
                'left_tm': pair.left_primer.tm,
                'left_gc': pair.left_primer.gc_percent,
                'left_self_any': pair.left_primer.self_any,
                'left_self_end': pair.left_primer.self_end,
                'left_sequence': pair.left_primer.sequence,
                'right_start': pair.right_primer.start,
                'right_length': pair.right_primer.length,
                'right_tm': pair.right_primer.tm,
                'right_gc': pair.right_primer.gc_percent,
                'right_self_any': pair.right_primer.self_any,
                'right_self_end': pair.right_primer.self_end,
                'right_sequence': pair.right_primer.sequence,
            })

        return pd.DataFrame(rows)
