#!/usr/bin/env python3
"""
Traveller RPG Sub-Sector Generator
Generates worlds following the Traveller Core Rulebook rules
Outputs in legacy-sec-format compatible with travellermap.com
"""

import random
import argparse
from typing import List, Tuple, Optional


def roll_dice(num_dice: int, modifier: int = 0) -> int:
    """Roll dice and apply modifier."""
    return sum(random.randint(1, 6) for _ in range(num_dice)) + modifier


def to_hex(value: int) -> str:
    """Convert integer to hexadecimal character (0-9, A-Z)."""
    if value < 0:
        return '0'
    elif value <= 9:
        return str(value)
    elif value <= 35:
        return chr(ord('A') + value - 10)
    else:
        return 'Z'


class World:
    """Represents a Traveller world with all its characteristics."""

    def __init__(self, hex_loc: str, name: str = ""):
        self.hex_loc = hex_loc
        self.name = name or f"World-{hex_loc}"
        self.size = 0
        self.atmosphere = 0
        self.hydrographics = 0
        self.population = 0
        self.government = 0
        self.law_level = 0
        self.starport = 'X'
        self.tech_level = 0
        self.naval_base = False
        self.scout_base = False
        self.gas_giants = 0
        self.planetoid_belts = 0
        self.pop_multiplier = 0
        self.trade_codes = []
        self.travel_zone = ''
        self.allegiance = 'Na'  # Default to Non-aligned

    def generate(self):
        """Generate all world characteristics following Traveller rules."""
        # Size: 2D-2
        self.size = max(0, roll_dice(2, -2))

        # Atmosphere: 2D-7 + Size
        if self.size == 0:
            self.atmosphere = 0
        else:
            self.atmosphere = max(0, min(15, roll_dice(2, -7) + self.size))

        # Hydrographics: 2D-7 + Atmosphere (with modifiers)
        if self.size <= 1:
            self.hydrographics = 0
        else:
            hydro_dm = 0
            if self.atmosphere in [0, 1] or self.atmosphere >= 10:
                hydro_dm = -4
            self.hydrographics = max(0, min(10, roll_dice(2, -7) + self.atmosphere + hydro_dm))

        # Population: 2D-2
        self.population = max(0, roll_dice(2, -2))

        # Government: 2D-7 + Population
        if self.population == 0:
            self.government = 0
        else:
            self.government = max(0, min(15, roll_dice(2, -7) + self.population))

        # Law Level: 2D-7 + Government
        if self.population == 0:
            self.law_level = 0
        else:
            self.law_level = max(0, min(10, roll_dice(2, -7) + self.government))

        # Starport
        self.generate_starport()

        # Tech Level
        self.generate_tech_level()

        # Bases
        self.generate_bases()

        # Gas Giants: Roll 10+ for NO gas giant
        if roll_dice(2) < 10:
            self.gas_giants = random.randint(1, 6)

        # Planetoid Belts
        self.planetoid_belts = max(0, roll_dice(1, -3))

        # Population Multiplier
        self.pop_multiplier = random.randint(1, 9)

        # Trade Codes
        self.determine_trade_codes()

        # Travel Zone (mostly safe, occasionally amber/red)
        self.determine_travel_zone()

    def generate_starport(self):
        """Generate starport class based on population."""
        dm = 0
        if self.population >= 10:
            dm = 2
        elif self.population >= 8:
            dm = 1
        elif self.population >= 3:
            dm = 0
        elif self.population >= 2:
            dm = -1
        else:
            dm = -2

        roll = roll_dice(2, dm)
        if roll <= 2:
            self.starport = 'X'
        elif roll <= 4:
            self.starport = 'E'
        elif roll <= 6:
            self.starport = 'D'
        elif roll <= 8:
            self.starport = 'C'
        elif roll <= 10:
            self.starport = 'B'
        else:
            self.starport = 'A'

    def generate_tech_level(self):
        """Generate tech level with modifiers."""
        if self.population == 0:
            self.tech_level = 0
            return

        tl = roll_dice(1)

        # Starport modifiers
        starport_mods = {'A': 6, 'B': 4, 'C': 2, 'D': 0, 'E': 0, 'X': -4}
        tl += starport_mods.get(self.starport, 0)

        # Size modifiers
        if self.size <= 1:
            tl += 2
        elif self.size <= 4:
            tl += 1

        # Atmosphere modifiers
        if self.atmosphere <= 3:
            tl += 1
        elif self.atmosphere >= 10:
            tl += 1

        # Hydrographics modifiers
        if self.hydrographics == 0:
            tl += 1
        elif self.hydrographics == 9:
            tl += 1
        elif self.hydrographics == 10:
            tl += 2

        # Population modifiers
        if self.population >= 1 and self.population <= 5:
            tl += 1
        elif self.population == 8:
            tl += 1
        elif self.population == 9:
            tl += 2
        elif self.population >= 10:
            tl += 4

        # Government modifiers
        if self.government == 0 or self.government == 5:
            tl += 1
        elif self.government == 7:
            tl += 2
        elif self.government in [13, 14]:
            tl -= 2

        self.tech_level = max(0, tl)

        if self.tech_level > 15:
            self.tech_level = 15

    def generate_bases(self):
        """Generate naval and scout bases."""
        base_chance = {
            'A': {'naval': 8, 'scout': 10},
            'B': {'naval': 8, 'scout': 9},
            'C': {'naval': 0, 'scout': 9},
            'D': {'naval': 0, 'scout': 8},
            'E': {'naval': 0, 'scout': 0},
            'X': {'naval': 0, 'scout': 0}
        }

        chances = base_chance.get(self.starport, {'naval': 0, 'scout': 0})

        if chances['naval'] > 0 and roll_dice(2) >= chances['naval']:
            self.naval_base = True

        if chances['scout'] > 0 and roll_dice(2) >= chances['scout']:
            self.scout_base = True

    def determine_trade_codes(self):
        """Determine trade codes based on world characteristics."""
        codes = []

        # Agricultural
        if (self.atmosphere >= 4 and self.atmosphere <= 9 and
            self.hydrographics >= 4 and self.hydrographics <= 8 and
            self.population >= 5 and self.population <= 7):
            codes.append('Ag')

        # Asteroid
        if self.size == 0 and self.atmosphere == 0 and self.hydrographics == 0:
            codes.append('As')

        # Barren
        if (self.population == 0 and self.government == 0 and
            self.law_level == 0 and self.atmosphere > 0):
            codes.append('Ba')

        # Desert
        if self.atmosphere >= 2 and self.hydrographics == 0:
            codes.append('De')

        # Fluid Oceans
        if self.atmosphere >= 10 and self.hydrographics >= 1:
            codes.append('Fl')

        # Garden
        if (self.size >= 6 and self.size <= 8 and
            self.atmosphere in [5, 6, 8] and
            self.hydrographics >= 5 and self.hydrographics <= 7):
            codes.append('Ga')

        # High Population
        if self.population >= 9:
            codes.append('Hi')

        # High Tech
        if self.tech_level >= 12:
            codes.append('Ht')

        # Ice-Capped
        if self.atmosphere <= 1 and self.hydrographics >= 1:
            codes.append('Ic')

        # Industrial
        if (self.atmosphere in [0, 1, 2, 4, 7, 9, 10, 11, 12] and
            self.population >= 9):
            codes.append('In')

        # Low Population
        if self.population >= 1 and self.population <= 3:
            codes.append('Lo')

        # Low Tech
        if self.population >= 1 and self.tech_level <= 5:
            codes.append('Lt')

        # Non-Agricultural
        if (self.atmosphere <= 3 and self.hydrographics <= 3 and
            self.population >= 6):
            codes.append('Na')

        # Non-Industrial
        if self.population >= 4 and self.population <= 6:
            codes.append('Ni')

        # Poor
        if (self.atmosphere >= 2 and self.atmosphere <= 5 and
            self.hydrographics <= 3):
            codes.append('Po')

        # Rich
        if (self.atmosphere in [6, 8] and self.population >= 6 and
            self.population <= 8 and self.government >= 4 and
            self.government <= 9):
            codes.append('Ri')

        # Vacuum
        if self.atmosphere == 0:
            codes.append('Va')

        # Water World
        if (((self.atmosphere >= 3 and self.atmosphere <= 9) or self.atmosphere >= 13) and self.hydrographics >= 10):
            codes.append('Wa')

        self.trade_codes = codes

    def determine_travel_zone(self):
        """Determine travel zone (mostly safe)."""
        # Amber zone conditions
        if (self.atmosphere >= 10 or self.government in [0, 7, 10] or
            self.law_level in [0] or self.law_level >= 9):
                if roll_dice(2) >= 9: # ~28% chance of amber zone
                    self.travel_zone = 'A'

        # Red zones are rare, at referee discretion
        if roll_dice(2) >= 13:  # Very rare
            self.travel_zone = 'R'

    def get_uwp(self) -> str:
        """Get Universal World Profile string."""
        return (f"{self.starport}"
                f"{to_hex(self.size)}"
                f"{to_hex(self.atmosphere)}"
                f"{to_hex(self.hydrographics)}"
                f"{to_hex(self.population)}"
                f"{to_hex(self.government)}"
                f"{to_hex(self.law_level)}-"
                f"{to_hex(self.tech_level)}")

    def get_bases(self) -> str:
        """Get base codes."""
        if self.naval_base and self.scout_base:
            return 'A'  # Both bases present
        elif self.naval_base:
            return 'N'
        elif self.scout_base:
            return 'S'
        else:
            return ' '

    def get_pbg(self) -> str:
        """Get PBG (Population multiplier, Belts, Gas giants)."""
        return f"{self.pop_multiplier}{self.planetoid_belts}{self.gas_giants}"

    def to_sec_format(self) -> str:
        """Format world data in legacy SEC format."""
        # Fixed-width columns for proper alignment
        name = self.name[:25].ljust(25)
        hex_loc = self.hex_loc.ljust(4)
        uwp = self.get_uwp().ljust(9)
        bases = self.get_bases()  # Single character

        # Trade codes - maximum 25 characters
        trade = ' '.join(self.trade_codes).ljust(25)

        zone = self.travel_zone if self.travel_zone else ' '
        pbg = self.get_pbg()  # 3 characters
        allegiance = self.allegiance  # 2 characters

        return f"{name} {hex_loc} {uwp}  {bases} {trade} {zone}  {pbg} {allegiance}"


class SubSector:
    """Represents a Traveller sub-sector (8x10 hexes)."""

    def __init__(self, name: str = "Sub-Sector A", sector_name: str = "Sector",
                 density_dm: int = 0, allegiance: str = 'Na', subsector_letter: str = 'A'):
        self.name = name
        self.sector_name = sector_name
        self.density_dm = density_dm
        self.allegiance = allegiance
        self.subsector_letter = subsector_letter.upper()
        self.worlds: List[World] = []

        # Calculate hex offset based on subsector position
        self.col_offset, self.row_offset = self._calculate_offsets()

    def _calculate_offsets(self) -> Tuple[int, int]:
        """
        Calculate hex coordinate offsets based on subsector letter.

        Subsector layout in a sector:
        A B C D    (columns: 01-08, 09-16, 17-24, 25-32)
        E F G H    (rows: 01-10, 11-20, 21-30, 31-40)
        I J K L
        M N O P

        Returns:
            Tuple of (column_offset, row_offset)
        """
        # Convert letter A-P to index 0-15
        subsector_index = ord(self.subsector_letter) - ord('A')
        if subsector_index < 0 or subsector_index > 15:
            print(f"Warning: Invalid subsector '{self.subsector_letter}', using A")
            subsector_index = 0

        # Calculate row and column in the 4x4 grid
        subsector_row = subsector_index // 4  # 0-3
        subsector_col = subsector_index % 4   # 0-3

        # Each subsector is 8 wide and 10 tall
        col_offset = subsector_col * 8
        row_offset = subsector_row * 10

        return col_offset, row_offset

    def generate(self):
        """Generate all worlds in the sub-sector."""
        # Sub-sector is 8 columns by 10 rows, offset by subsector position
        for col in range(1, 9):
            for row in range(1, 11):
                # World occurrence: 1D, 4-6 with density modifier
                if roll_dice(1, self.density_dm) >= 4:
                    # Apply subsector offset to hex coordinates
                    actual_col = col + self.col_offset
                    actual_row = row + self.row_offset
                    hex_loc = f"{actual_col:02d}{actual_row:02d}"
                    world = World(hex_loc)
                    world.allegiance = self.allegiance
                    world.generate()
                    self.worlds.append(world)

    def to_sec_format(self) -> str:
        """Generate complete SEC format output."""
        output = []
        output.append(f"@SUB_SECTOR: {self.name} SECTOR: {self.sector_name}")
        output.append("#")
        output.append("#1------------------------2----3----------4-5-------------------------6--7---8-")
        output.append("#PlanetName               Loc. UWP Code   B Notes                     Z  PBG Al")
        output.append("#------------------------ ---- ---------  - ------------------------- -  --- --")

        # Sort worlds by hex location
        for world in sorted(self.worlds, key=lambda w: w.hex_loc):
            output.append(world.to_sec_format())

        return '\n'.join(output)


def generate_random_name() -> str:
    """Generate a random world name."""
    prefixes = ['Gaz', 'Tar', 'Vel', 'Kur', 'Zeb', 'Mar', 'Kel', 'Dor',
                'Reg', 'Sab', 'Nal', 'Fer', 'Kor', 'Pel', 'Dra']
    middles = ['ul', 'ar', 'en', 'on', 'in', 'an', 'or', 'er', 'is', 'us']
    suffixes = ['ini', 'ion', 'eth', 'oth', 'an', 'is', 'us', 'ix', 'ax', 'on']

    return random.choice(prefixes) + random.choice(middles) + random.choice(suffixes)


def main():
    """Main function to run the generator."""
    parser = argparse.ArgumentParser(
        description='Generate a Traveller RPG sub-sector in legacy SEC format'
    )
    parser.add_argument('--name',
                       help='Sub-sector name (default: auto-generated from subsector letter)')
    parser.add_argument('--sector', default='Generated',
                       help='Sector name (default: Generated)')
    parser.add_argument('--subsector', default='A',
                       help='Subsector letter A-P (default: A). Determines hex coordinate offsets.')
    parser.add_argument('--density', type=int, choices=[-2, -1, 0, 1], default=0,
                       help='Density modifier: -2 (rift), -1 (sparse), 0 (normal), 1 (dense)')
    parser.add_argument('--allegiance', default='Na',
                       help='Allegiance code (default: Na for Non-aligned)')
    parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    parser.add_argument('--seed', type=int, help='Random seed for reproducibility')
    parser.add_argument('--names', action='store_true',
                       help='Generate random names for worlds')

    args = parser.parse_args()

    # Set random seed if provided
    if args.seed:
        random.seed(args.seed)

    # Auto-generate name from subsector if not provided
    subsector_letter = args.subsector.upper()
    subsector_name = args.name if args.name else f'Sub-Sector {subsector_letter}'

    # Generate sub-sector
    subsector = SubSector(subsector_name, args.sector, args.density,
                         args.allegiance, subsector_letter)
    subsector.generate()

    # Optionally add random names
    if args.names:
        for world in subsector.worlds:
            world.name = generate_random_name()

    # Output
    output_text = subsector.to_sec_format()

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_text)
        print(f"Sub-sector generated and saved to {args.output}")
    else:
        print(output_text)


if __name__ == '__main__':
    main()
