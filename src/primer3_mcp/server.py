"""FastMCP server for Primer3 primer design."""

from fastmcp import FastMCP

from .api import design_primers as design_primers_lib
from .api import troubleshoot_primers as troubleshoot_primers_lib

mcp = FastMCP(name="primer3-mcp", version="0.1.0")


@mcp.tool()
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
) -> dict:
    """
    Design PCR primers following lab protocol.

    Input sequence must contain [n] placeholder marking the target region.
    Returns ranked primer pairs with 10 features per primer:
    - start: Position of 5' base
    - length: Oligonucleotide length
    - tm: Melting temperature (°C)
    - gc_percent: GC content percentage
    - self_any: Self-complementarity score
    - self_end: 3' self-complementarity (primer-dimer tendency)
    - rep: Mispriming/Mishyb library similarity
    - sequence: Primer sequence (5'→3', right primer is reverse complement)

    Args:
        sequence: DNA sequence with [n] placeholder for target region
        primer_size_min: Minimum primer size (default: 20 bp)
        primer_size_opt: Optimal primer size (default: 25 bp)
        primer_size_max: Maximum primer size (default: 30 bp)
        primer_tm_min: Minimum melting temperature (default: 64°C)
        primer_tm_opt: Optimal melting temperature (default: 65°C)
        primer_tm_max: Maximum melting temperature (default: 66°C)
        gc_clamp: Number of G/C bases at 3' end (default: 2)
        num_return: Number of primer pairs to return (default: 5)

    Returns:
        Dictionary with primer pairs and design information
    """
    result = design_primers_lib(
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
    return result.model_dump()


@mcp.tool()
def troubleshoot_primers(sequence: str, num_return: int = 5) -> dict:
    """
    Auto-retry primer design with progressively relaxed constraints.

    Follows lab protocol troubleshooting (step 7):
    1. Try with GC clamp = 2
    2. If no results, reduce GC clamp to 1
    3. If no results, reduce GC clamp to 0
    4. If no results, widen Tm range by ±1°C

    Returns detailed troubleshooting feedback on which relaxation succeeded.

    Args:
        sequence: DNA sequence with [n] placeholder for target region
        num_return: Number of primer pairs to return (default: 5)

    Returns:
        Dictionary with primer pairs and troubleshooting information
    """
    result = troubleshoot_primers_lib(
        sequence=sequence,
        num_return=num_return,
    )
    return result.model_dump()


def main():
    """Main entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
