#!/usr/bin/env python3
"""
TUI Color Palette Generator

Generates complete retro/cyberpunk color palettes from a base color.
Outputs CSS variables, Tailwind config, and SwiftUI Color extensions.

Usage:
    python generate_palette.py "#00ff00" --name phosphor
    python generate_palette.py "#00ffff" --name cyber --format css
    python generate_palette.py "#ffb000" --name amber --format all

Requirements:
    Python 3.7+ (no external dependencies)
"""

import argparse
import colorsys
import json
import sys
from typing import Tuple, Dict, List


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB to hex string."""
    return f"#{r:02x}{g:02x}{b:02x}"


def rgb_to_hsl(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """Convert RGB to HSL."""
    h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
    return (h * 360, s * 100, l * 100)


def hsl_to_rgb(h: float, s: float, l: float) -> Tuple[int, int, int]:
    """Convert HSL to RGB."""
    r, g, b = colorsys.hls_to_rgb(h/360, l/100, s/100)
    return (int(r * 255), int(g * 255), int(b * 255))


def adjust_lightness(hex_color: str, factor: float) -> str:
    """Adjust the lightness of a color."""
    r, g, b = hex_to_rgb(hex_color)
    h, s, l = rgb_to_hsl(r, g, b)
    new_l = max(0, min(100, l * factor))
    new_r, new_g, new_b = hsl_to_rgb(h, s, new_l)
    return rgb_to_hex(new_r, new_g, new_b)


def generate_tui_palette(base_hex: str, name: str) -> Dict:
    """
    Generate a complete TUI palette from a base color.

    Creates:
    - bright: Original color (100% lightness factor)
    - medium: 80% lightness
    - dim: 60% lightness
    - muted: 40% lightness
    - bg: Very dark version for backgrounds
    - bg-deep: Even darker for nested backgrounds
    """
    r, g, b = hex_to_rgb(base_hex)
    h, s, l = rgb_to_hsl(r, g, b)

    palette = {
        'name': name,
        'base': base_hex,
        'colors': {
            'bright': base_hex,
            'medium': adjust_lightness(base_hex, 0.8),
            'dim': adjust_lightness(base_hex, 0.6),
            'muted': adjust_lightness(base_hex, 0.4),
            'bg': rgb_to_hex(*hsl_to_rgb(h, s * 0.8, 5)),
            'bg-deep': rgb_to_hex(*hsl_to_rgb(h, s * 0.6, 2)),
        },
        'accents': generate_complementary_colors(base_hex)
    }

    return palette


def generate_complementary_colors(base_hex: str) -> Dict:
    """Generate complementary accent colors."""
    r, g, b = hex_to_rgb(base_hex)
    h, s, l = rgb_to_hsl(r, g, b)

    return {
        'complement': rgb_to_hex(*hsl_to_rgb((h + 180) % 360, s, l)),
        'triadic1': rgb_to_hex(*hsl_to_rgb((h + 120) % 360, s, l)),
        'triadic2': rgb_to_hex(*hsl_to_rgb((h + 240) % 360, s, l)),
        'analogous1': rgb_to_hex(*hsl_to_rgb((h + 30) % 360, s, l)),
        'analogous2': rgb_to_hex(*hsl_to_rgb((h - 30) % 360, s, l)),
    }


def format_css(palette: Dict) -> str:
    """Format palette as CSS custom properties."""
    name = palette['name']
    colors = palette['colors']
    accents = palette['accents']

    lines = [
        f"/* {name.title()} Palette */",
        f"/* Generated from base: {palette['base']} */",
        "",
        ":root {",
        f"  /* Primary colors */",
    ]

    for key, value in colors.items():
        css_key = key.replace('_', '-')
        lines.append(f"  --{name}-{css_key}: {value};")

    lines.append("")
    lines.append("  /* Accent colors */")

    for key, value in accents.items():
        css_key = key.replace('_', '-')
        lines.append(f"  --{name}-{css_key}: {value};")

    lines.append("}")
    lines.append("")

    # Add utility classes
    lines.extend([
        f"/* Utility classes */",
        f".bg-{name} {{ background-color: var(--{name}-bg); }}",
        f".bg-{name}-deep {{ background-color: var(--{name}-bg-deep); }}",
        f".text-{name} {{ color: var(--{name}-bright); }}",
        f".text-{name}-dim {{ color: var(--{name}-dim); }}",
        f".border-{name} {{ border-color: var(--{name}-bright); }}",
        "",
        f"/* Neon glow effect */",
        f".neon-{name} {{",
        f"  color: var(--{name}-bright);",
        f"  text-shadow:",
        f"    0 0 5px #fff,",
        f"    0 0 10px #fff,",
        f"    0 0 20px var(--{name}-bright),",
        f"    0 0 40px var(--{name}-bright),",
        f"    0 0 80px var(--{name}-bright);",
        f"}}",
    ])

    return "\n".join(lines)


def format_tailwind(palette: Dict) -> str:
    """Format palette as Tailwind config."""
    name = palette['name']
    colors = palette['colors']
    accents = palette['accents']

    config = {
        name: {
            **{k.replace('-', ''): v for k, v in colors.items()},
            'accent': accents
        }
    }

    lines = [
        f"// {name.title()} Palette for Tailwind CSS",
        f"// Generated from base: {palette['base']}",
        "",
        "// Add to tailwind.config.js:",
        "module.exports = {",
        "  theme: {",
        "    extend: {",
        "      colors: " + json.dumps(config, indent=8).replace('"', "'"),
        "    }",
        "  }",
        "}",
    ]

    return "\n".join(lines)


def format_swift(palette: Dict) -> str:
    """Format palette as SwiftUI Color extension."""
    name = palette['name']
    colors = palette['colors']
    accents = palette['accents']

    lines = [
        f"// {name.title()} Palette for SwiftUI",
        f"// Generated from base: {palette['base']}",
        "",
        "import SwiftUI",
        "",
        "extension Color {",
    ]

    # Add primary colors
    for key, value in colors.items():
        swift_key = name + key.title().replace('-', '').replace('_', '')
        r, g, b = hex_to_rgb(value)
        lines.append(
            f"    static let {swift_key} = Color("
            f"red: {r/255:.3f}, green: {g/255:.3f}, blue: {b/255:.3f})"
        )

    lines.append("")
    lines.append("    // Accent colors")

    # Add accent colors
    for key, value in accents.items():
        swift_key = name + key.title().replace('-', '').replace('_', '')
        r, g, b = hex_to_rgb(value)
        lines.append(
            f"    static let {swift_key} = Color("
            f"red: {r/255:.3f}, green: {g/255:.3f}, blue: {b/255:.3f})"
        )

    lines.append("}")

    return "\n".join(lines)


def format_json(palette: Dict) -> str:
    """Format palette as JSON."""
    output = {
        'name': palette['name'],
        'base': palette['base'],
        'colors': {},
        'accents': palette['accents']
    }

    for key, value in palette['colors'].items():
        r, g, b = hex_to_rgb(value)
        h, s, l = rgb_to_hsl(r, g, b)
        output['colors'][key] = {
            'hex': value,
            'rgb': f"rgb({r}, {g}, {b})",
            'hsl': f"hsl({h:.0f}, {s:.0f}%, {l:.0f}%)",
        }

    return json.dumps(output, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description='Generate TUI color palettes from a base color.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "#00ff00" --name phosphor
  %(prog)s "#00ffff" --name cyber --format css
  %(prog)s "#ffb000" --name amber --format all --output palette

Preset colors:
  Phosphor Green: #00ff00
  Cyberpunk Cyan: #00ffff
  Cyberpunk Magenta: #ff00ff
  Amber CRT: #ffb000
  Synthwave Purple: #9d4edd
        """
    )

    parser.add_argument(
        'color',
        help='Base color in hex format (e.g., "#00ff00" or "00ff00")'
    )
    parser.add_argument(
        '--name', '-n',
        default='palette',
        help='Name for the palette (default: palette)'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['css', 'tailwind', 'swift', 'json', 'all'],
        default='all',
        help='Output format (default: all)'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file prefix (prints to stdout if not specified)'
    )

    args = parser.parse_args()

    # Validate color
    color = args.color.lstrip('#')
    if len(color) != 6:
        print(f"Error: Invalid color format '{args.color}'. Use hex format like '#00ff00'", file=sys.stderr)
        sys.exit(1)

    try:
        hex_to_rgb(color)
    except ValueError:
        print(f"Error: Invalid hex color '{args.color}'", file=sys.stderr)
        sys.exit(1)

    # Generate palette
    palette = generate_tui_palette(f"#{color}", args.name)

    # Format output
    outputs = {}
    if args.format in ['css', 'all']:
        outputs['css'] = format_css(palette)
    if args.format in ['tailwind', 'all']:
        outputs['tailwind'] = format_tailwind(palette)
    if args.format in ['swift', 'all']:
        outputs['swift'] = format_swift(palette)
    if args.format in ['json', 'all']:
        outputs['json'] = format_json(palette)

    # Output
    if args.output:
        extensions = {
            'css': '.css',
            'tailwind': '.tailwind.js',
            'swift': '.swift',
            'json': '.json'
        }
        for fmt, content in outputs.items():
            filename = f"{args.output}{extensions[fmt]}"
            with open(filename, 'w') as f:
                f.write(content)
            print(f"Written: {filename}")
    else:
        for fmt, content in outputs.items():
            print(f"\n{'='*60}")
            print(f" {fmt.upper()} OUTPUT")
            print(f"{'='*60}\n")
            print(content)


if __name__ == '__main__':
    main()
