# primer3-mcp

Design PCR primers with Primer3, following lab protocols for optimal primer design.

Can be used as:
1. **Python library** for Jupyter notebooks and scripts
2. **MCP server** for Claude Desktop integration

## Features

- **Design Primers**: Design PCR primers with protocol-validated parameters
- **Auto-Troubleshooting**: Automatically retry with relaxed constraints if no primers found
- **10-Feature Output**: Complete primer information including Tm, GC%, self-complementarity, and more
- **Lab Protocol Compliant**: Follows established PCR primer design best practices
- **Data Analysis Ready**: Export to pandas DataFrame for analysis

## Installation

```bash
# Basic installation
pip install -e .

# With Jupyter notebook support
pip install -e ".[analysis]"

# With development dependencies
pip install -e ".[dev]"
```

## Usage

### As Python Library

Perfect for Jupyter notebooks, data analysis, and automation scripts.

**See [examples/primer_design_demo.ipynb](examples/primer_design_demo.ipynb) for a complete interactive tutorial!**

#### Quick Start

```python
from primer3_mcp import design_primers

# Your sequence with [n] marking target region
sequence = "GGGTCAGGTAGGAACGCGTGCCAGATCT[n]ACTAGTGATCAACCTCTGAAGAGGT"

# Design primers
result = design_primers(sequence=sequence, num_return=5)

# Access results
print(f"Found {result.num_returned} primer pairs")
best_pair = result.pairs[0]
print(f"Best product size: {best_pair.product_size}bp")
print(f"Left primer:  {best_pair.left_primer.sequence}")
print(f"Right primer: {best_pair.right_primer.sequence}")
```

#### Data Analysis with Pandas

```python
from primer3_mcp import design_primers

# Design primers
result = design_primers(sequence=sequence)

# Convert to pandas DataFrame
df = result.to_dataframe()

# Analyze primer characteristics
print(df[['pair_id', 'product_size', 'penalty', 'left_tm', 'right_tm']])

# Filter by criteria
good_primers = df[
    (df['penalty'] < 1.0) &
    (df['product_size'] > 200) &
    (df['left_tm'].between(64, 66))
]
```

#### Troubleshooting Difficult Sequences

```python
from primer3_mcp import troubleshoot_primers

# Auto-retry with relaxed constraints
result = troubleshoot_primers(sequence=difficult_sequence)

if result.num_returned > 0:
    print(f"Success! Found {result.num_returned} pairs")
    if result.troubleshooting_applied:
        print(f"Applied: {result.troubleshooting_applied}")
else:
    print("No primers found even with relaxed constraints")
```

#### Customizing Parameters

```python
from primer3_mcp import design_primers

result = design_primers(
    sequence=sequence,
    primer_size_min=18,
    primer_size_opt=22,
    primer_size_max=27,
    primer_tm_min=60.0,
    primer_tm_opt=62.0,
    primer_tm_max=64.0,
    gc_clamp=1,
    num_return=10
)
```

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

**Example (via Claude Desktop):**
```
Design primers for this sequence:
GGGTCAGGTAGGAACGCGTGCCAGATCT...[n]...ACTAGTGATCAACCTCTGAAGAGGT
```

Claude will call the `design_primers` tool and return ranked primer pairs.

#### `troubleshoot_primers`

Auto-retry primer design with progressively relaxed constraints following lab protocol troubleshooting:
1. Try GC clamp = 2
2. Reduce to GC clamp = 1
3. Reduce to GC clamp = 0
4. Widen Tm range by ±1°C

**Parameters:**
- `sequence` (required): DNA sequence with `[n]` placeholder
- `num_return`: Number of primer pairs to return (default: 5)

**Example (via Claude Desktop):**
```
I need primers for this difficult sequence, please troubleshoot if needed:
GGGTCAGGTAGGAACGCGTGCCAGATCT...[n]...ACTAGTGATCAACCTCTGAAGAGGT
```

Claude will call `troubleshoot_primers` and report which constraint relaxations were applied.

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

## Examples

See the [examples/](examples/) directory for complete tutorials:

- **[primer_design_demo.ipynb](examples/primer_design_demo.ipynb)** - Complete walkthrough covering:
  - Basic primer design
  - Custom parameters
  - Pandas integration and data analysis
  - Troubleshooting difficult sequences
  - Batch processing multiple genes
  - Exporting results for ordering

## Development

### Setup

```bash
# Install package with dev dependencies
uv pip install -e ".[dev]"
```

### Running Tests

```bash
uv run pytest -v
```

### Project Structure

```
primer3-mcp/
├── src/primer3_mcp/
│   ├── __init__.py        # Public API exports
│   ├── api.py             # Library functions
│   ├── server.py          # FastMCP server & tools
│   ├── primer_design.py   # Primer3 integration
│   ├── models.py          # Pydantic models
│   └── utils.py           # Sequence parsing
└── tests/                 # Test suite
```

## License

MIT
