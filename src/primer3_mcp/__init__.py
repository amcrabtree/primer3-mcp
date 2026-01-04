"""
Primer3-MCP: PCR primer design with Primer3.

Can be used as:
1. Python library for Jupyter notebooks and scripts
2. MCP server for Claude Desktop integration

Examples:
    Basic library usage:
    >>> from primer3_mcp import design_primers
    >>> result = design_primers(sequence="ATGC...[n]...GCTA")
    >>> print(result.pairs[0].left_primer.sequence)

    With troubleshooting:
    >>> from primer3_mcp import troubleshoot_primers
    >>> result = troubleshoot_primers(sequence="ATGC...[n]...GCTA")
"""

__version__ = "0.1.0"

# Public API exports
from .api import design_primers, troubleshoot_primers
from .models import (
    PrimerDesignInput,
    PrimerDesignOutput,
    PrimerPair,
    PrimerInfo,
)

__all__ = [
    "design_primers",
    "troubleshoot_primers",
    "PrimerDesignInput",
    "PrimerDesignOutput",
    "PrimerPair",
    "PrimerInfo",
]
