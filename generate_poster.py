#!/usr/bin/env python3
"""
Traveller Sub-Sector Poster Generator
Reads a generated sub-sector .md file and generates a poster image using TravellerMap API
"""

import argparse
import sys
import requests
from pathlib import Path


def read_sector_file(filepath: str) -> str:
    """Read the sector data file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)


def determine_subsector(sector_data: str) -> str:
    """
    Determine the subsector letter (A-P) from hex coordinates in the data.

    Subsector layout in a sector (32x40 hexes, 4x4 subsectors):
    A B C D
    E F G H
    I J K L
    M N O P

    Each subsector is 8x10 hexes.
    """
    # Parse hex coordinates from the data
    hex_coords = []
    for line in sector_data.split('\n'):
        if line.startswith('#') or line.startswith('@') or not line.strip():
            continue

        # Extract hex location (format: XXYY where XX=01-32, YY=01-40)
        parts = line.split()
        if len(parts) >= 2:
            hex_loc = parts[1]
            if len(hex_loc) == 4 and hex_loc.isdigit():
                x = int(hex_loc[:2])
                y = int(hex_loc[2:])
                hex_coords.append((x, y))

    if not hex_coords:
        # Default to subsector A if no valid coordinates found
        return 'A'

    # Use the first coordinate to determine subsector
    # (assuming all worlds are in the same subsector)
    x, y = hex_coords[0]

    # Determine column (0-3) and row (0-3)
    col = (x - 1) // 8  # 01-08=0, 09-16=1, 17-24=2, 25-32=3
    row = (y - 1) // 10  # 01-10=0, 11-20=1, 21-30=2, 31-40=3

    # Subsector index (0-15)
    subsector_index = row * 4 + col

    # Convert to letter A-P
    subsector_letter = chr(ord('A') + subsector_index)

    return subsector_letter


def generate_poster(sector_data: str, output_file: str, scale: int = 128,
                   style: str = 'poster', accept: str = 'application/pdf',
                   subsector: str = None) -> None:
    """
    Generate a poster using the TravellerMap API.

    Args:
        sector_data: The sector data in SEC format
        output_file: Path to save the output file
        scale: Pixels per parsec (default 128)
        style: Rendering style (default 'poster' for black background)
        accept: Output format MIME type (default 'application/pdf')
        subsector: Subsector letter (A-P) or None for auto-detect
    """
    api_url = 'https://travellermap.com/api/poster'

    # Auto-detect subsector if not specified
    if subsector is None:
        subsector = determine_subsector(sector_data)

    # Prepare the request parameters
    params = {
        'scale': scale,
        'style': style,
        'accept': accept,
        'subsector': subsector
    }

    # Prepare the data payload
    # POST the sector data as plain text
    headers = {
        'Content-Type': 'text/plain',
        'Accept': accept
    }

    print(f"Generating poster from TravellerMap API...")
    print(f"  Subsector: {subsector}")
    print(f"  Style: {style}")
    print(f"  Scale: {scale} pixels per parsec")
    print(f"  Format: {accept}")

    try:
        # Make POST request with sector data
        response = requests.post(
            api_url,
            params=params,
            data=sector_data.encode('utf-8'),
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        # Determine file extension from accept type
        ext_map = {
            'application/pdf': 'pdf',
            'image/svg+xml': 'svg',
            'image/png': 'png',
            'image/jpeg': 'jpg'
        }

        # Ensure output file has correct extension
        output_path = Path(output_file)
        expected_ext = ext_map.get(accept, 'pdf')
        if output_path.suffix.lower() != f'.{expected_ext}':
            output_path = output_path.with_suffix(f'.{expected_ext}')

        # Save the response
        with open(output_path, 'wb') as f:
            f.write(response.content)

        print(f"✓ Poster saved to: {output_path}")
        print(f"  File size: {len(response.content):,} bytes")

    except requests.exceptions.Timeout:
        print("Error: Request timed out. The API might be slow or unavailable.", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"Error: HTTP {e.response.status_code} - {e.response.reason}", file=sys.stderr)
        if e.response.text:
            print(f"Details: {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main function to run the poster generator."""
    parser = argparse.ArgumentParser(
        description='Generate a poster image from a Traveller sub-sector file using TravellerMap API'
    )
    parser.add_argument('input_file',
                       help='Input sub-sector file (.md) in SEC format')
    parser.add_argument('output_file',
                       help='Output poster file path')
    parser.add_argument('--scale', type=int, default=128,
                       help='Pixels per parsec (default: 128)')
    parser.add_argument('--style', default='poster',
                       choices=['poster', 'print', 'atlas', 'candy', 'draft',
                               'FASA', 'terminal', 'mongoose'],
                       help='Rendering style (default: poster - black background)')
    parser.add_argument('--format', default='pdf',
                       choices=['pdf', 'svg', 'png'],
                       help='Output format (default: pdf)')
    parser.add_argument('--subsector',
                       help='Subsector letter (A-P) - auto-detected if not specified')

    args = parser.parse_args()

    # Map format choice to MIME type
    format_map = {
        'pdf': 'application/pdf',
        'svg': 'image/svg+xml',
        'png': 'image/png'
    }

    accept = format_map[args.format]

    # Read the sector data
    sector_data = read_sector_file(args.input_file)

    # Generate the poster
    generate_poster(
        sector_data=sector_data,
        output_file=args.output_file,
        scale=args.scale,
        style=args.style,
        accept=accept,
        subsector=args.subsector
    )


if __name__ == '__main__':
    main()
