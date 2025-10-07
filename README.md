# Traveller RPG Sub-Sector Generator

A Python-based command-line tool for generating Traveller RPG sub-sectors following the official Traveller Core Rulebook rules. Outputs data in the legacy-sec-format compatible with [TravellerMap.com](https://travellermap.com). Includes a poster generator to create beautiful map visualizations.

## Features

- **Complete World Generation**: Generates all UWP (Universal World Profile) characteristics:
  - Size, Atmosphere, Hydrographics
  - Population, Government, Law Level
  - Starport class, Tech Level
  - Bases (Naval, Scout)
  - Gas Giants and Planetoid Belts
  - Trade Codes
  - Travel Zones

- **Follows Official Rules**: Implements world generation rules from the Traveller Core Rulebook Update 2022
- **Legacy SEC Format**: Outputs in the standard format used by TravellerMap.com
- **Customizable**: Options for density, allegiance, and random naming
- **Reproducible**: Optional seed for generating the same sub-sector
- **Poster Generation**: Create beautiful PDF/SVG/PNG maps using the TravellerMap API

## Installation

### Basic Setup

The sub-sector generator has no external dependencies:

```bash
chmod +x traveller_subsector_gen.py
```

### Poster Generator Setup

For the poster generator, create a virtual environment and install dependencies:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Sub-Sector Generation

#### Basic Usage

Generate a sub-sector with default settings:

```bash
python3 traveller_subsector_gen.py
```

#### Generate with Random Names

```bash
python3 traveller_subsector_gen.py --names
```

#### Save to File

```bash
python3 traveller_subsector_gen.py --names --output my_subsector.md
```

#### Advanced Options

```bash
# Generate Subsector C with custom name
python3 traveller_subsector_gen.py \
  --name "Spinward Reaches" \
  --sector "Deneb" \
  --subsector C \
  --density 1 \
  --allegiance "Im" \
  --names \
  --seed 12345 \
  --output spinward_reaches.md
```

#### Generate Different Subsectors

```bash
# Subsector A (default) - hex coordinates 01-08 x 01-10
python3 traveller_subsector_gen.py --names --output subsector_a.md

# Subsector B - hex coordinates 09-16 x 01-10
python3 traveller_subsector_gen.py --subsector B --names --output subsector_b.md

# Subsector P (last) - hex coordinates 25-32 x 31-40
python3 traveller_subsector_gen.py --subsector P --names --output subsector_p.md
```

### Poster Generation

After generating a sub-sector file, create a poster visualization:

#### Basic Poster Generation

```bash
source venv/bin/activate  # Activate virtual environment first
python3 generate_poster.py example_subsector.md my_poster.pdf
```

#### Custom Options

```bash
# Generate PNG with larger scale
python3 generate_poster.py \
  --format png \
  --scale 256 \
  example_subsector.md my_poster.png

# Use terminal style (retro-futuristic)
python3 generate_poster.py \
  --style terminal \
  --format svg \
  example_subsector.md my_poster.svg
```

## Command-Line Options

### Sub-Sector Generator

| Option | Description | Default |
|--------|-------------|---------|
| `--name` | Sub-sector name | Auto-generated from subsector letter |
| `--sector` | Sector name | "Generated" |
| `--subsector` | Subsector letter (A-P) - determines hex coordinate offsets | A |
| `--density` | Density modifier: -2 (rift), -1 (sparse), 0 (normal), 1 (dense) | 0 |
| `--allegiance` | Allegiance code (Im=Imperium, Na=Non-aligned, etc.) | "Na" |
| `--names` | Generate random world names | False |
| `--output`, `-o` | Output file path (if not specified, prints to stdout) | stdout |
| `--seed` | Random seed for reproducibility | Random |

**Subsector Positioning**: Each subsector occupies a specific position in the 4x4 sector grid, affecting hex coordinates:

```
A(01-08,01-10)  B(09-16,01-10)  C(17-24,01-10)  D(25-32,01-10)
E(01-08,11-20)  F(09-16,11-20)  G(17-24,11-20)  H(25-32,11-20)
I(01-08,21-30)  J(09-16,21-30)  K(17-24,21-30)  L(25-32,21-30)
M(01-08,31-40)  N(09-16,31-40)  O(17-24,31-40)  P(25-32,31-40)
```

### Poster Generator

| Option | Description | Default |
|--------|-------------|---------|
| `input_file` | Input sub-sector file (.md) in SEC format | Required |
| `output_file` | Output poster file path | Required |
| `--scale` | Pixels per parsec (higher = larger image) | 128 |
| `--style` | Rendering style (poster, print, atlas, candy, draft, FASA, terminal, mongoose) | poster |
| `--format` | Output format (pdf, svg, png) | pdf |
| `--subsector` | Subsector letter (A-P) to render | Auto-detected from hex codes |

**Note**: The subsector is automatically detected from the hex coordinates in your file. A sector contains 16 subsectors (A-P) arranged in a 4x4 grid:

```
A B C D    (columns: 01-08, 09-16, 17-24, 25-32)
E F G H    (rows: 01-10, 11-20, 21-30, 31-40)
I J K L
M N O P
```

The generator creates subsectors with coordinates 01-08 x 01-10, which is always Subsector A.

#### Available Styles

- **poster**: Color-on-black style (recommended for black background)
- **print**: Print-friendly black-on-white
- **atlas**: Atlas-style rendering
- **terminal**: Retro-futuristic computer terminal style
- **candy**: Colorful rendering
- **draft**: Simple draft style
- **FASA**: FASA-style rendering
- **mongoose**: Mongoose Publishing style

## Output Format

The generator outputs data in the legacy-sec-format:

```
@SUB_SECTOR: Sub-Sector A SECTOR: Generated
#
#--------1---------2---------3---------4---------5-------
#PlanetName   Loc. UPP Code   B   Notes         Z  PBG Al
#----------   ---- ---------  - --------------- -  --- --
Gazulini      0109 A7A65A8-9  N Fl Ni              501 Im
```

### Field Breakdown

- **PlanetName**: World name
- **Loc.**: Hex location (XXYY format)
- **UPP Code**: Universal World Profile
  - Starport (A-E, X)
  - Size (0-A)
  - Atmosphere (0-F)
  - Hydrographics (0-A)
  - Population (0-C+)
  - Government (0-F)
  - Law Level (0-9+)
  - Tech Level (0-F+)
- **B**: Bases (N=Naval, S=Scout)
- **Notes**: Trade codes (Ag, In, Ni, etc.)
- **Z**: Travel Zone (A=Amber, R=Red, blank=Safe)
- **PBG**: Population multiplier, Belts, Gas giants
- **Al**: Allegiance code

## Trade Codes

The generator automatically assigns trade codes based on world characteristics:

- **Ag**: Agricultural
- **As**: Asteroid
- **Ba**: Barren
- **De**: Desert
- **Fl**: Fluid Oceans
- **Ga**: Garden
- **Hi**: High Population
- **Ht**: High Tech
- **Ic**: Ice-Capped
- **In**: Industrial
- **Lo**: Low Population
- **Lt**: Low Tech
- **Na**: Non-Agricultural
- **Ni**: Non-Industrial
- **Po**: Poor
- **Ri**: Rich
- **Va**: Vacuum
- **Wa**: Water World

## Examples

### Complete Workflow: Generate Sub-Sector and Poster

```bash
# 1. Generate subsector H (Spinward Marches style)
python3 traveller_subsector_gen.py \
  --name "Mora" \
  --sector "Spinward Marches" \
  --subsector H \
  --density 1 \
  --allegiance "Im" \
  --names \
  --seed 42 \
  --output mora_subsector.md

# 2. Activate virtual environment
source venv/bin/activate

# 3. Generate poster (subsector auto-detected as H)
python3 generate_poster.py \
  --scale 128 \
  --style poster \
  --format pdf \
  mora_subsector.md mora_poster.pdf
```

### Generate a dense Imperial sub-sector

```bash
python3 traveller_subsector_gen.py \
  --name "Mora" \
  --sector "Spinward Marches" \
  --density 1 \
  --allegiance "Im" \
  --names \
  --output mora_subsector.md
```

### Generate a sparse frontier region

```bash
python3 traveller_subsector_gen.py \
  --name "Rift Outpost" \
  --density -1 \
  --allegiance "Na" \
  --names
```

### Generate reproducible results

```bash
python3 traveller_subsector_gen.py --seed 42 --names
```

### Create high-resolution PNG poster

```bash
source venv/bin/activate
python3 generate_poster.py \
  --format png \
  --scale 256 \
  --style poster \
  example_subsector.md high_res_poster.png
```

## World Generation Rules

The generator follows the Traveller Core Rulebook rules:

1. **World Occurrence**: 50% base chance (modified by density)
2. **Size**: 2D-2
3. **Atmosphere**: 2D-7 + Size
4. **Hydrographics**: 2D-7 + Atmosphere (with modifiers)
5. **Population**: 2D-2
6. **Government**: 2D-7 + Population
7. **Law Level**: 2D-7 + Government
8. **Starport**: 2D with Population modifiers
9. **Tech Level**: 1D + various DMs
10. **Bases**: Based on starport class
11. **Gas Giants**: Roll 10+ for none present

## License

This generator is a fan-created tool for the Traveller RPG system. Traveller is a registered trademark of Far Future Enterprises.

## References

- [TravellerMap.com File Formats](https://travellermap.com/doc/fileformats)
- Traveller Core Rulebook Update 2022
