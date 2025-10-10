#!/usr/bin/env python3
"""
Traveller Trade Code Validator
Validates and corrects trade codes in subsector files based on UWP codes
"""

import argparse
import sys
from typing import List, Tuple, Set


def from_hex(value: str) -> int:
    """Convert hexadecimal character to integer."""
    if value.isdigit():
        return int(value)
    else:
        return ord(value.upper()) - ord('A') + 10


def determine_trade_codes(size: int, atmosphere: int, hydrographics: int,
                         population: int, government: int, law_level: int,
                         starport: str, tech_level: int) -> List[str]:
    """
    Determine trade codes based on world characteristics.
    Uses the same logic as traveller_subsector_gen.py
    """
    codes = []

    # Agricultural
    if (atmosphere >= 4 and atmosphere <= 9 and
        hydrographics >= 4 and hydrographics <= 8 and
        population >= 5 and population <= 7):
        codes.append('Ag')

    # Asteroid
    if size == 0 and atmosphere == 0 and hydrographics == 0:
        codes.append('As')

    # Barren
    if (population == 0 and government == 0 and
        law_level == 0 and atmosphere > 0):
        codes.append('Ba')

    # Desert
    if atmosphere >= 2 and hydrographics == 0:
        codes.append('De')

    # Fluid Oceans
    if atmosphere >= 10 and hydrographics >= 1:
        codes.append('Fl')

    # Garden
    if (size >= 6 and size <= 8 and
        atmosphere in [5, 6, 8] and
        hydrographics >= 5 and hydrographics <= 7):
        codes.append('Ga')

    # High Population
    if population >= 9:
        codes.append('Hi')

    # High Tech
    if tech_level >= 12:
        codes.append('Ht')

    # Ice-Capped
    if atmosphere <= 1 and hydrographics >= 1:
        codes.append('Ic')

    # Industrial
    if (atmosphere in [0, 1, 2, 4, 7, 9, 10, 11, 12] and
        population >= 9):
        codes.append('In')

    # Low Population
    if population >= 1 and population <= 3:
        codes.append('Lo')

    # Low Tech
    if population >= 1 and tech_level <= 5:
        codes.append('Lt')

    # Non-Agricultural
    if (atmosphere <= 3 and hydrographics <= 3 and
        population >= 6):
        codes.append('Na')

    # Non-Industrial
    if population >= 4 and population <= 6:
        codes.append('Ni')

    # Poor
    if (atmosphere >= 2 and atmosphere <= 5 and
        hydrographics <= 3):
        codes.append('Po')

    # Rich
    if (atmosphere in [6, 8] and population >= 6 and
        population <= 8 and government >= 4 and
        government <= 9):
        codes.append('Ri')

    # Vacuum
    if atmosphere == 0:
        codes.append('Va')

    # Water World
    if (((atmosphere >= 3 and atmosphere <= 9) or atmosphere >= 13) and hydrographics >= 10):
        codes.append('Wa')

    return codes


def parse_uwp(uwp: str) -> Tuple[str, int, int, int, int, int, int, int]:
    """
    Parse UWP string into individual components.

    Returns:
        Tuple of (starport, size, atmosphere, hydrographics, population,
                 government, law_level, tech_level)
    """
    if len(uwp) < 9:
        raise ValueError(f"Invalid UWP format: {uwp}")

    starport = uwp[0]
    size = from_hex(uwp[1])
    atmosphere = from_hex(uwp[2])
    hydrographics = from_hex(uwp[3])
    population = from_hex(uwp[4])
    government = from_hex(uwp[5])
    law_level = from_hex(uwp[6])
    # uwp[7] is the dash '-'
    tech_level = from_hex(uwp[8])

    return (starport, size, atmosphere, hydrographics, population,
            government, law_level, tech_level)


def parse_sec_line(line: str) -> dict:
    """
    Parse a single line from a SEC format file using fixed-width columns.

    Format:
    Name (25 chars) + space + Hex (4 chars) + space + UWP (9 chars) +
    2 spaces + Base (1 char) + space + Trade codes (25 chars) + space +
    Zone (1 char) + 2 spaces + PBG (3 chars) + space + Allegiance (2 chars)
    """
    if len(line) < 40:
        return None

    # Fixed-width parsing
    name = line[0:25].strip()
    hex_loc = line[26:30].strip()
    uwp = line[31:40].strip()

    # Base is at position 42 (after 2 spaces)
    base = line[42] if len(line) > 42 else ' '

    # Trade codes section: 25 chars starting at position 44
    trade_section = line[44:69].strip() if len(line) > 44 else ''
    trade_codes = trade_section.split() if trade_section else []

    # Zone at position 70
    zone = line[70] if len(line) > 70 else ' '

    # PBG at position 73-75 (after 2 spaces)
    pbg = line[73:76].strip() if len(line) > 73 else ''

    # Allegiance at position 77-78 (after space)
    allegiance = line[77:79].strip() if len(line) > 77 else ''

    return {
        'name': name,
        'hex': hex_loc,
        'uwp': uwp,
        'base': base,
        'trade_codes': trade_codes,
        'zone': zone,
        'pbg': pbg,
        'allegiance': allegiance,
        'raw_line': line
    }


def validate_file(filepath: str, fix: bool = False) -> None:
    """
    Validate trade codes in a subsector file.

    Args:
        filepath: Path to SEC format file
        fix: If True, write corrected file; if False, only report issues
    """
    print(f"Reading subsector file: {filepath}")

    # Read file
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    # Process lines
    header_lines = []
    world_data = []
    issues_found = 0

    for line_num, line in enumerate(lines, 1):
        # Preserve header and comment lines
        if line.startswith('#') or line.startswith('@') or not line.strip():
            header_lines.append((line_num, line))
            continue

        # Parse world line
        world = parse_sec_line(line)
        if not world:
            header_lines.append((line_num, line))
            continue

        # Parse UWP and determine correct trade codes
        try:
            (starport, size, atmosphere, hydrographics, population,
             government, law_level, tech_level) = parse_uwp(world['uwp'])

            correct_codes = determine_trade_codes(
                size, atmosphere, hydrographics, population,
                government, law_level, starport, tech_level
            )

            # Compare with actual codes
            actual_codes = set(world['trade_codes'])
            correct_codes_set = set(correct_codes)

            if actual_codes != correct_codes_set:
                issues_found += 1
                missing = correct_codes_set - actual_codes
                extra = actual_codes - correct_codes_set

                print(f"\n{world['name']} ({world['hex']}) - UWP: {world['uwp']}")
                if missing:
                    print(f"  Missing codes: {', '.join(sorted(missing))}")
                if extra:
                    print(f"  Extra codes: {', '.join(sorted(extra))}")
                print(f"  Current: {' '.join(world['trade_codes']) if world['trade_codes'] else '(none)'}")
                print(f"  Correct: {' '.join(correct_codes) if correct_codes else '(none)'}")

                # Update for fixing
                world['trade_codes'] = correct_codes
                world['needs_fix'] = True
            else:
                world['needs_fix'] = False

            world_data.append((line_num, world))

        except Exception as e:
            print(f"Warning: Could not parse line {line_num}: {e}", file=sys.stderr)
            header_lines.append((line_num, line))

    # Summary
    print(f"\n{'='*60}")
    print(f"Validation complete: {issues_found} world(s) with incorrect trade codes")

    # Fix file if requested
    if fix and issues_found > 0:
        output_lines = []

        # Add headers
        for line_num, line in header_lines:
            output_lines.append(line.rstrip('\n'))

        # Add world lines (either corrected or original)
        for line_num, world in world_data:
            if world['needs_fix']:
                # Reconstruct line with corrected trade codes
                name = world['name'].ljust(25)
                hex_loc = world['hex'].ljust(4)
                uwp = world['uwp'].ljust(9)
                base = world['base']
                trade = ' '.join(world['trade_codes']).ljust(25)
                zone = world['zone'] if world['zone'] else ' '
                pbg = world['pbg']
                allegiance = world['allegiance']

                new_line = f"{name} {hex_loc} {uwp}  {base} {trade} {zone}  {pbg} {allegiance}"
                output_lines.append(new_line.rstrip())
            else:
                # Use original line
                output_lines.append(world['raw_line'].rstrip('\n'))

        # Write corrected file
        backup_path = filepath + '.bak'
        try:
            # Create backup
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(f"\nBackup created: {backup_path}")

            # Write corrected file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(output_lines) + '\n')
            print(f"Corrected file written: {filepath}")
            print(f"✓ {issues_found} world(s) updated")

        except Exception as e:
            print(f"Error writing file: {e}", file=sys.stderr)
            sys.exit(1)

    elif issues_found > 0:
        print(f"\nTo fix these issues, run with --fix flag")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Validate and correct trade codes in Traveller subsector files'
    )
    parser.add_argument('input_file',
                       help='Input subsector file in SEC format')
    parser.add_argument('--fix', action='store_true',
                       help='Fix trade codes in place (creates .bak backup)')

    args = parser.parse_args()

    validate_file(args.input_file, args.fix)


if __name__ == '__main__':
    main()
