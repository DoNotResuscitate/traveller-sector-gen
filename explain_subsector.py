#!/usr/bin/env python3
"""
Traveller Sub-Sector Explainer
Translates UWP codes and trade data into human-readable descriptions
"""

import argparse
import sys
from typing import Dict, List


# Lookup tables from Traveller Core Rulebook

STARPORT_DESCRIPTIONS = {
    'A': 'an excellent quality starport with shipyard capable of building all types of vessels, refined fuel, and repair facilities',
    'B': 'a good quality starport with spacecraft shipyard, refined fuel, and repair facilities',
    'C': 'a routine quality starport with small craft shipyard, unrefined fuel, and repair facilities',
    'D': 'a poor quality starport with limited repair facilities and unrefined fuel',
    'E': 'a frontier installation - a bare spot of bedrock with a beacon',
    'X': 'no starport - no facilities whatsoever'
}

SIZE_DATA = {
    '0': {'diameter': 'less than 1,000', 'gravity': 'negligible'},
    '1': {'diameter': '1,600', 'gravity': '0.05G'},
    '2': {'diameter': '3,200', 'gravity': '0.15G'},
    '3': {'diameter': '4,800', 'gravity': '0.25G'},
    '4': {'diameter': '6,400', 'gravity': '0.35G'},
    '5': {'diameter': '8,000', 'gravity': '0.45G'},
    '6': {'diameter': '9,600', 'gravity': '0.7G'},
    '7': {'diameter': '11,200', 'gravity': '0.9G'},
    '8': {'diameter': '12,800', 'gravity': '1.0G'},
    '9': {'diameter': '14,400', 'gravity': '1.25G'},
    'A': {'diameter': '16,000', 'gravity': '1.4G'}
}

ATMOSPHERE_DESCRIPTIONS = {
    '0': 'no atmosphere (vacuum)',
    '1': 'trace atmosphere',
    '2': 'very thin, tainted atmosphere requiring a respirator and filter',
    '3': 'very thin atmosphere requiring a respirator',
    '4': 'thin, tainted atmosphere requiring a filter',
    '5': 'thin but breathable atmosphere',
    '6': 'standard breathable atmosphere similar to Earth',
    '7': 'standard atmosphere but tainted, requiring a filter',
    '8': 'dense atmosphere',
    '9': 'dense, tainted atmosphere requiring a filter',
    'A': 'exotic atmosphere requiring an air supply',
    'B': 'corrosive atmosphere requiring a vacc suit',
    'C': 'insidious atmosphere that attacks equipment',
    'D': 'very dense atmosphere',
    'E': 'low atmosphere',
    'F': 'unusual atmosphere with strange properties'
}

HYDROGRAPHICS_DESCRIPTIONS = {
    '0': 'desert world (0-5% water)',
    '1': 'dry world (6-15% water)',
    '2': 'world with few small seas (16-25% water)',
    '3': 'world with small seas and oceans (26-35% water)',
    '4': 'wet world (36-45% water)',
    '5': 'world with large ocean covering roughly half the surface (46-55% water)',
    '6': 'world with large oceans (56-65% water)',
    '7': 'Earth-like world (66-75% water)',
    '8': 'wet world with only a few islands and archipelagos (76-85% water)',
    '9': 'world almost entirely made of water (86-95% water)',
    'A': 'waterworld with 96-100% water coverage'
}

POPULATION_BASE_VALUES = {
    '0': 0,
    '1': 10,
    '2': 100,
    '3': 1000,
    '4': 10000,
    '5': 100000,
    '6': 1000000,
    '7': 10000000,
    '8': 100000000,
    '9': 1000000000,
    'A': 10000000000,
    'B': 100000000000,
    'C': 1000000000000
}

GOVERNMENT_DESCRIPTIONS = {
    '0': 'no government structure - family bonds or anarchy',
    '1': 'company or corporation - ruled by a managerial elite',
    '2': 'participating democracy - direct citizen consensus',
    '3': 'self-perpetuating oligarchy',
    '4': 'representative democracy with elected officials',
    '5': 'feudal technocracy - ruled by those with advanced technology',
    '6': 'captive government - colony or conquered area',
    '7': 'balkanization - multiple competing governments',
    '8': 'civil service bureaucracy',
    '9': 'impersonal bureaucracy insulated from citizens',
    'A': 'charismatic dictator with overwhelming support',
    'B': 'non-charismatic leader - military dictatorship or hereditary rule',
    'C': 'charismatic oligarchy',
    'D': 'religious dictatorship',
    'E': 'religious autocracy',
    'F': 'totalitarian oligarchy'
}

LAW_LEVEL_DESCRIPTIONS = {
    '0': 'no law - heavy weapons recommended',
    '1': 'low law - WMD and poison gas banned, battle dress banned',
    '2': 'low law - portable energy weapons banned, combat armor banned',
    '3': 'moderate law - military weapons banned, flak armor banned',
    '4': 'moderate law - light assault weapons banned, cloth armor banned',
    '5': 'moderate law - personal concealable weapons banned, mesh armor banned',
    '6': 'high law - all firearms except shotguns banned',
    '7': 'high law - all firearms banned',
    '8': 'high law - all weapons including blades banned, all visible armor banned',
    '9': 'extreme law - all weapons and armor banned',
    'A': 'totalitarian law - all weapons and armor banned'
}

TECH_LEVEL_DESCRIPTIONS = {
    '0': 'TL0 (Primitive) - no technology, only the simplest tools and principles, Stone Age',
    '1': 'TL1 (Primitive) - Bronze or Iron age technology, can manufacture weapons and work metals',
    '2': 'TL2 (Primitive) - Renaissance technology with scientific method, greater understanding of chemistry and physics',
    '3': 'TL3 (Primitive) - industrial revolution and steam power, primitive firearms, comparable to early 19th Century',
    '4': 'TL4 (Industrial) - complete industrial revolution bringing plastics and radio, comparable to late 19th/early 20th Century',
    '5': 'TL5 (Industrial) - widespread electrification, telecommunications, internal combustion, atomics and primitive computing, comparable to mid-20th Century',
    '6': 'TL6 (Industrial) - fission power, advanced computing, materials technology and rocketry bring the dawn of the space age',
    '7': 'TL7 (Pre-Stellar) - can reach orbit reliably with telecommunications satellites, computers and integrated circuits ubiquitous',
    '8': 'TL8 (Pre-Stellar) - can reach other worlds in same star system, permanent space habitats possible, fusion power commercially viable',
    '9': 'TL9 (Pre-Stellar) - gravity manipulation development makes space travel safer, void drive research leads to breakthrough near end of this level',
    'A': 'TL10 (Early Stellar) - commonly available void drives open up nearby systems, orbital habitats and factories common, interstellar trade leads to economic boom',
    'B': 'TL11 (Early Stellar) - first true weak artificial intelligences, grav-supported structures reach to the heavens, Void-2 travel possible',
    'C': 'TL12 (Average Stellar) - planetwide weather control revolutionizes terraforming, portable plasma weapons, Void-3 travel',
    'D': 'TL13 (Average Stellar) - battle dress appears, cloning of body parts becomes easy, Void-4 travel',
    'E': 'TL14 (Average Stellar) - fusion weapons become portable, flying cities appear, Void-5 drives built',
    'F': 'TL15 (High Stellar) - black globe generators, synthetic anagathics vastly increase human lifespan',
    'G': 'TL16+ (Higher Stellar) - technology beyond the highest known levels in Charted Space'
}

TRADE_CODE_DESCRIPTIONS = {
    'Ag': 'agricultural world dedicated to farming',
    'As': 'asteroid belt',
    'Ba': 'barren and uncolonized',
    'De': 'desert world',
    'Fl': 'fluid oceans (non-water liquid)',
    'Ga': 'garden world - Earth-like',
    'Hi': 'high population in the billions',
    'Ht': 'high tech - among the most advanced',
    'Ic': 'ice-capped world',
    'In': 'industrial world',
    'Lo': 'low population',
    'Lt': 'low tech - pre-industrial',
    'Na': 'non-agricultural',
    'Ni': 'non-industrial',
    'Po': 'poor - lacking resources',
    'Ri': 'rich economic powerhouse',
    'Va': 'vacuum - no atmosphere',
    'Wa': 'water world - almost entirely ocean'
}

BASE_DESCRIPTIONS = {
    'N': 'a Naval base',
    'S': 'a Scout base',
    'A': 'both Naval and Scout bases present',
    ' ': 'no bases'
}

TRAVEL_ZONE_DESCRIPTIONS = {
    'A': 'Amber Zone - caution advised due to danger or instability',
    'R': 'Red Zone - interdicted, travel forbidden',
    ' ': 'safe for travel'
}


def from_hex(value: str) -> int:
    """Convert hexadecimal character to integer."""
    if value.isdigit():
        return int(value)
    else:
        return ord(value.upper()) - ord('A') + 10


def format_population(pop_code: str, pbg: str) -> str:
    """
    Format population using the population code and PBG multiplier.

    Args:
        pop_code: Population code (0-C)
        pbg: PBG string (first digit is population multiplier)

    Returns:
        Formatted population string
    """
    if pop_code == '0' or not pbg:
        return 'uninhabited'

    base_value = POPULATION_BASE_VALUES.get(pop_code, 0)
    if base_value == 0:
        return 'unknown population'

    # Get population multiplier from PBG (first digit)
    try:
        multiplier = int(pbg[0]) if pbg else 1
    except (ValueError, IndexError):
        multiplier = 1

    actual_population = base_value * multiplier

    # Format the number with appropriate units
    if actual_population == 0:
        return 'uninhabited'
    elif actual_population < 1000:
        return f'{actual_population:,}'
    elif actual_population < 1000000:
        thousands = actual_population / 1000
        if thousands == int(thousands):
            return f'{int(thousands):,} thousand'
        else:
            return f'{thousands:,.1f} thousand'
    elif actual_population < 1000000000:
        millions = actual_population / 1000000
        if millions == int(millions):
            return f'{int(millions):,} million'
        else:
            return f'{millions:,.1f} million'
    elif actual_population < 1000000000000:
        billions = actual_population / 1000000000
        if billions == int(billions):
            return f'{int(billions):,} billion'
        else:
            return f'{billions:,.1f} billion'
    else:
        trillions = actual_population / 1000000000000
        if trillions == int(trillions):
            return f'{int(trillions):,} trillion'
        else:
            return f'{trillions:,.1f} trillion'


def parse_sec_file(filepath: str) -> List[Dict]:
    """
    Parse a SEC format file and extract world data using fixed-width columns.

    Format:
    Name (25 chars) + space + Hex (4 chars) + space + UWP (9 chars) +
    2 spaces + Base (1 char) + space + Trade codes (25 chars) + space +
    Zone (1 char) + 2 spaces + PBG (3 chars) + space + Allegiance (2 chars)
    """
    worlds = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                # Skip comment and header lines
                if line.startswith('#') or line.startswith('@') or not line.strip():
                    continue

                # Require minimum length for valid world line
                if len(line) < 40:
                    continue

                # Fixed-width parsing
                name = line[0:25].strip()
                hex_loc = line[26:30].strip()
                uwp = line[31:40].strip()

                # Validate we have at least name, hex, and UWP
                if not name or not hex_loc or not uwp:
                    continue

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

                world = {
                    'name': name,
                    'hex': hex_loc,
                    'uwp': uwp,
                    'starport': uwp[0] if len(uwp) > 0 else '?',
                    'size': uwp[1] if len(uwp) > 1 else '?',
                    'atmosphere': uwp[2] if len(uwp) > 2 else '?',
                    'hydrographics': uwp[3] if len(uwp) > 3 else '?',
                    'population': uwp[4] if len(uwp) > 4 else '?',
                    'government': uwp[5] if len(uwp) > 5 else '?',
                    'law_level': uwp[6] if len(uwp) > 6 else '?',
                    'tech_level': uwp[8] if len(uwp) > 8 else '?',
                    'bases': base,
                    'trade_codes': trade_codes,
                    'zone': zone,
                    'pbg': pbg,
                    'allegiance': allegiance
                }

                worlds.append(world)

    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    return worlds


def explain_world(world: Dict) -> str:
    """Generate a human-readable explanation of a world."""
    lines = []

    # Header
    lines.append(f"# {world['name']}")
    lines.append(f"**Location:** {world['hex']} | **UWP:** {world['uwp']}")
    lines.append("")

    # Build description paragraph
    desc_parts = []

    # Basic description with size, gravity, and population
    name = world['name']
    size_data = SIZE_DATA.get(world['size'], {'diameter': 'unknown', 'gravity': 'unknown'})
    diameter = size_data['diameter']
    gravity = size_data['gravity']
    pop_formatted = format_population(world['population'], world.get('pbg', ''))

    if world['population'] == '0':
        desc_parts.append(f"{name} is roughly {diameter} kilometers in diameter, with a gravity of {gravity}, and is uninhabited.")
    else:
        desc_parts.append(f"{name} is roughly {diameter} kilometers in diameter, with a gravity of {gravity}, and a population of {pop_formatted}.")

    # Atmosphere and hydrographics
    atmo_desc = ATMOSPHERE_DESCRIPTIONS.get(world['atmosphere'], 'unknown atmosphere')
    hydro_desc = HYDROGRAPHICS_DESCRIPTIONS.get(world['hydrographics'], 'unknown hydrographics')
    desc_parts.append(f"The world has a {atmo_desc}, and is a {hydro_desc}.")

    # Government and law
    if world['population'] != '0':
        gov_desc = GOVERNMENT_DESCRIPTIONS.get(world['government'], 'unknown government')
        law_desc = LAW_LEVEL_DESCRIPTIONS.get(world['law_level'], 'unknown law level')
        desc_parts.append(f"The population is governed by a {gov_desc}, with {law_desc}.")

    # Technology
    tech_desc = TECH_LEVEL_DESCRIPTIONS.get(world['tech_level'], 'unknown tech level')
    desc_parts.append(f"The world has {tech_desc}.")

    # Starport
    starport_desc = STARPORT_DESCRIPTIONS.get(world['starport'], 'unknown starport quality')
    desc_parts.append(f"It has {starport_desc}.")

    # Bases
    base_desc = BASE_DESCRIPTIONS.get(world['bases'].strip(), 'no bases')
    if world['bases'].strip():
        desc_parts.append(f"The system has {base_desc}.")

    # Trade codes
    if world['trade_codes']:
        trade_descs = []
        for code in world['trade_codes']:
            if code in TRADE_CODE_DESCRIPTIONS:
                trade_descs.append(TRADE_CODE_DESCRIPTIONS[code])

        if trade_descs:
            desc_parts.append(f"Notable characteristics: {', '.join(trade_descs)}.")

    # Travel zone
    zone_desc = TRAVEL_ZONE_DESCRIPTIONS.get(world['zone'], 'safe for travel')
    if world['zone'] in ['A', 'R']:
        desc_parts.append(f"**Travel Advisory:** {zone_desc}.")

    # Combine all parts
    lines.append(' '.join(desc_parts))
    lines.append("")

    return '\n'.join(lines)


def generate_explanation(input_file: str, output_file: str) -> None:
    """Generate explanation document from subsector file."""
    print(f"Parsing subsector file: {input_file}")
    worlds = parse_sec_file(input_file)

    print(f"Found {len(worlds)} worlds")

    # Generate markdown
    output_lines = []
    output_lines.append("# Sub-Sector World Guide")
    output_lines.append("")
    output_lines.append("This guide provides human-readable descriptions of each world in the sub-sector, ")
    output_lines.append("translating the Universal World Profile (UWP) codes into plain language.")
    output_lines.append("")
    output_lines.append("---")
    output_lines.append("")

    for world in worlds:
        output_lines.append(explain_world(world))

    # Write output
    output_text = '\n'.join(output_lines)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output_text)

    print(f"✓ Explanation saved to: {output_file}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Generate human-readable explanations of Traveller subsector worlds'
    )
    parser.add_argument('input_file',
                       help='Input subsector file in SEC format')
    parser.add_argument('output_file',
                       help='Output markdown file with explanations')

    args = parser.parse_args()

    generate_explanation(args.input_file, args.output_file)


if __name__ == '__main__':
    main()
