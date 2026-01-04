# primer3-mcp

An MCP server for designing PCR primers with Primer3, following lab protocols for optimal primer design.

## Features

- **Design Primers**: Design PCR primers with protocol-validated parameters
- **Auto-Troubleshooting**: Automatically retry with relaxed constraints if no primers found
- **10-Feature Output**: Complete primer information including Tm, GC%, self-complementarity, and more
- **Lab Protocol Compliant**: Follows established PCR primer design best practices

## Installation

```bash
# Using uv
uv venv
uv pip install -e .

# Or with pip
pip install -e .
```

## Usage

### As MCP Server with Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "primer3": {
      "command": "uv",
      "args": ["run", "primer3-mcp"]
    }
  }
}
```

### Available Tools

#### `design_primers`

Design PCR primers with customizable parameters.

**Parameters:**
- `sequence` (required): DNA sequence with `[n]` placeholder marking target region
- `primer_size_min`: Minimum primer size in bp (default: 20)
- `primer_size_opt`: Optimal primer size in bp (default: 25)
- `primer_size_max`: Maximum primer size in bp (default: 30)
- `primer_tm_min`: Minimum melting temperature in °C (default: 64)
- `primer_tm_opt`: Optimal melting temperature in °C (default: 65)
- `primer_tm_max`: Maximum melting temperature in °C (default: 66)
- `gc_clamp`: Number of G/C bases at 3' end (default: 2)
- `num_return`: Number of primer pairs to return (default: 5)

**Example:**
```python
sequence = "GGGTCAGGTAGGAACGCGTGCCAGATCT...[n]...ACTAGTGATCAACCTCTGAAGAGGT"
result = design_primers(sequence=sequence)
```

#### `troubleshoot_design`

Auto-retry primer design with progressively relaxed constraints following lab protocol troubleshooting:
1. Try GC clamp = 2
2. Reduce to GC clamp = 1
3. Reduce to GC clamp = 0
4. Widen Tm range by ±1°C

**Parameters:**
- `sequence` (required): DNA sequence with `[n]` placeholder
- `num_return`: Number of primer pairs to return (default: 5)

**Example:**
```python
result = troubleshoot_design(sequence=sequence)
# Returns primers with troubleshooting_applied field showing which relaxation worked
```

### Output Format

Each primer pair includes:

**Left & Right Primer (10 features each):**
- `start`: Position of 5' base
- `length`: Oligonucleotide length
- `tm`: Melting temperature (°C)
- `gc_percent`: GC content percentage
- `self_any`: Self-complementarity score
- `self_end`: 3' self-complementarity (primer-dimer tendency)
- `rep`: Mispriming/Mishyb library similarity
- `sequence`: Primer sequence (5'→3', right primer is reverse complement)

**Pair Info:**
- `pair_id`: Rank (0 = best quality)
- `product_size`: Amplicon size in bp
- `penalty`: Primer pair penalty score

## Protocol Details

Based on lab protocol for gene amplification:
- Input sequence must contain `[n]` placeholder for target region
- Default parameters optimized for PCR performance
- Primers ranked by quality (first = best)
- Right primer sequence is reverse complement (ready for ordering)

## Development

### Running Tests

```bash
uv run pytest -v
```

### Project Structure

```
primer3-mcp/
├── src/primer3_mcp/
│   ├── server.py          # FastMCP server & tools
│   ├── primer_design.py   # Primer3 integration
│   ├── models.py          # Pydantic models
│   └── utils.py           # Sequence parsing
└── tests/                 # Test suite
```

## License

MIT
