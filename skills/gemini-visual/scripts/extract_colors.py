#!/usr/bin/env python3
"""
Extract Colors - Extract color palettes from images using Google Gemini 3.

Generates color palettes in various formats including CSS, Tailwind, and SCSS.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional

# Exit codes
EXIT_SUCCESS = 0
EXIT_MISSING_API_KEY = 1
EXIT_INVALID_ARGS = 2
EXIT_FILE_NOT_FOUND = 3
EXIT_API_ERROR = 4
EXIT_SAVE_ERROR = 5

# Configuration
DEFAULT_MODEL = "gemini-3-pro-preview"
DEFAULT_COLOR_COUNT = 6
VALID_FORMATS = ["text", "json", "css", "tailwind", "scss"]


def get_api_key() -> str:
    """Get the Gemini API key from environment variable."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.", file=sys.stderr)
        print("\nTo get an API key:", file=sys.stderr)
        print("1. Go to https://aistudio.google.com/apikey", file=sys.stderr)
        print("2. Create or select a project", file=sys.stderr)
        print("3. Generate an API key", file=sys.stderr)
        print("\nThen set the environment variable:", file=sys.stderr)
        print("  export GEMINI_API_KEY='your-api-key'", file=sys.stderr)
        sys.exit(EXIT_MISSING_API_KEY)
    return api_key


def load_image(path: str) -> tuple[bytes, str]:
    """Load an image file and return bytes and mime type."""
    path = Path(path)
    if not path.exists():
        print(f"Error: Image file not found: {path}", file=sys.stderr)
        sys.exit(EXIT_FILE_NOT_FOUND)

    suffix = path.suffix.lower()
    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".heic": "image/heic",
        ".heif": "image/heif",
    }

    mime_type = mime_types.get(suffix)
    if not mime_type:
        print(f"Error: Unsupported image format: {suffix}", file=sys.stderr)
        print(f"Supported formats: {', '.join(mime_types.keys())}", file=sys.stderr)
        sys.exit(EXIT_INVALID_ARGS)

    return path.read_bytes(), mime_type


def build_extraction_prompt(
    count: int,
    include_named: bool,
    include_contrast: bool,
) -> str:
    """Build the color extraction prompt."""
    prompt = f"""Analyze this image and extract the {count} most prominent/important colors.

For each color, provide:
1. HEX code (e.g., #FF5733)
2. RGB values (e.g., rgb(255, 87, 51))
3. HSL values (e.g., hsl(11, 100%, 60%))
4. A semantic name/role (e.g., "primary", "background", "accent", "text")
5. Usage in the image (where this color appears)"""

    if include_named:
        prompt += """
6. Closest CSS named color (e.g., "coral", "steelblue")"""

    if include_contrast:
        prompt += """

Also calculate WCAG contrast ratios:
- Between each text-like color and potential background colors
- Note which combinations pass AA (4.5:1) and AAA (7:1) standards"""

    prompt += """

Return the colors ordered by visual importance/prominence.

IMPORTANT: Format your response as valid JSON with this structure:
{
  "colors": [
    {
      "hex": "#XXXXXX",
      "rgb": "rgb(R, G, B)",
      "hsl": "hsl(H, S%, L%)",
      "name": "semantic-name",
      "usage": "description of usage",
      "css_name": "closest-css-color" // if requested
    }
  ],
  "contrast_ratios": [ // if requested
    {
      "color1": "#XXXXXX",
      "color2": "#YYYYYY",
      "ratio": 4.5,
      "passes_aa": true,
      "passes_aaa": false
    }
  ],
  "palette_description": "Brief description of the overall color scheme"
}"""

    return prompt


def format_as_css(colors: list[dict]) -> str:
    """Format colors as CSS custom properties."""
    lines = [":root {"]
    for color in colors:
        name = color.get("name", "color").replace(" ", "-").lower()
        hex_val = color.get("hex", "#000000")
        lines.append(f"  --color-{name}: {hex_val};")
    lines.append("}")
    return "\n".join(lines)


def format_as_tailwind(colors: list[dict]) -> str:
    """Format colors as Tailwind config."""
    color_obj = {}
    for color in colors:
        name = color.get("name", "color").replace(" ", "-").lower()
        hex_val = color.get("hex", "#000000")
        color_obj[name] = hex_val

    config = {
        "theme": {
            "extend": {
                "colors": color_obj
            }
        }
    }

    return f"// tailwind.config.js\nmodule.exports = {json.dumps(config, indent=2)}"


def format_as_scss(colors: list[dict]) -> str:
    """Format colors as SCSS variables."""
    lines = ["// Color palette variables"]
    for color in colors:
        name = color.get("name", "color").replace(" ", "-").lower()
        hex_val = color.get("hex", "#000000")
        lines.append(f"${name}: {hex_val};")

    lines.append("")
    lines.append("// Color map for programmatic access")
    lines.append("$colors: (")
    for color in colors:
        name = color.get("name", "color").replace(" ", "-").lower()
        hex_val = color.get("hex", "#000000")
        lines.append(f"  '{name}': {hex_val},")
    lines.append(");")

    return "\n".join(lines)


def format_as_text(data: dict, include_contrast: bool) -> str:
    """Format colors as human-readable text."""
    lines = ["Color Palette", "=" * 50, ""]

    colors = data.get("colors", [])
    for i, color in enumerate(colors, 1):
        lines.append(f"{i}. {color.get('name', 'Color').title()}")
        lines.append(f"   HEX: {color.get('hex', 'N/A')}")
        lines.append(f"   RGB: {color.get('rgb', 'N/A')}")
        lines.append(f"   HSL: {color.get('hsl', 'N/A')}")
        if color.get("css_name"):
            lines.append(f"   CSS: {color.get('css_name')}")
        lines.append(f"   Usage: {color.get('usage', 'N/A')}")
        lines.append("")

    if include_contrast and data.get("contrast_ratios"):
        lines.append("Contrast Ratios")
        lines.append("-" * 30)
        for cr in data.get("contrast_ratios", []):
            status = "AAA" if cr.get("passes_aaa") else ("AA" if cr.get("passes_aa") else "FAIL")
            lines.append(
                f"{cr.get('color1')} / {cr.get('color2')}: "
                f"{cr.get('ratio', 'N/A')}:1 [{status}]"
            )
        lines.append("")

    if data.get("palette_description"):
        lines.append("Overall: " + data.get("palette_description"))

    return "\n".join(lines)


def extract_colors(
    image_path: str,
    count: int = DEFAULT_COLOR_COUNT,
    output_format: str = "text",
    include_named: bool = False,
    include_contrast: bool = False,
    verbose: bool = False,
) -> str:
    """Extract colors from an image using Gemini 3."""
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("Error: google-genai package not installed.", file=sys.stderr)
        print("Install it with: pip install google-genai", file=sys.stderr)
        sys.exit(EXIT_INVALID_ARGS)

    api_key = get_api_key()

    if verbose:
        print(f"[*] Loading image: {image_path}")
        print(f"[*] Extracting {count} colors")

    # Load image
    image_data, mime_type = load_image(image_path)

    if verbose:
        print(f"[*] Image loaded ({len(image_data)} bytes)")
        print(f"[*] Initializing Gemini client...")

    # Initialize client
    client = genai.Client(api_key=api_key)

    # Build prompt
    prompt = build_extraction_prompt(count, include_named, include_contrast)

    # Build content
    contents = [
        types.Part.from_bytes(data=image_data, mime_type=mime_type),
        prompt,
    ]

    # Configure generation
    config = types.GenerateContentConfig(
        temperature=0.5,  # Lower temperature for more consistent color extraction
    )

    if verbose:
        print(f"[*] Extracting colors...")

    try:
        response = client.models.generate_content(
            model=DEFAULT_MODEL,
            contents=contents,
            config=config,
        )
    except Exception as e:
        error_msg = str(e)
        if "rate" in error_msg.lower() or "quota" in error_msg.lower():
            print("Error: Rate limit exceeded. Please wait and try again.", file=sys.stderr)
        else:
            print(f"Error: API request failed: {error_msg}", file=sys.stderr)
        sys.exit(EXIT_API_ERROR)

    if verbose:
        print(f"[*] Extraction complete")

    # Extract response
    if not response.candidates:
        print("Error: No response from API.", file=sys.stderr)
        sys.exit(EXIT_API_ERROR)

    try:
        response_text = response.text
    except Exception:
        print("Error: Could not extract text from response.", file=sys.stderr)
        sys.exit(EXIT_API_ERROR)

    # Parse JSON from response
    try:
        # Try to extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            data = json.loads(json_match.group())
        else:
            print("Error: Could not parse JSON from response.", file=sys.stderr)
            print("Raw response:", response_text, file=sys.stderr)
            sys.exit(EXIT_API_ERROR)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in response: {e}", file=sys.stderr)
        print("Raw response:", response_text, file=sys.stderr)
        sys.exit(EXIT_API_ERROR)

    colors = data.get("colors", [])

    # Format output
    if output_format == "json":
        return json.dumps(data, indent=2)
    elif output_format == "css":
        return format_as_css(colors)
    elif output_format == "tailwind":
        return format_as_tailwind(colors)
    elif output_format == "scss":
        return format_as_scss(colors)
    else:
        return format_as_text(data, include_contrast)


def save_output(content: str, output_path: str, verbose: bool = False) -> None:
    """Save output to file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        path.write_text(content)
        if verbose:
            print(f"[*] Palette saved to: {path}")
    except Exception as e:
        print(f"Error: Failed to save output: {e}", file=sys.stderr)
        sys.exit(EXIT_SAVE_ERROR)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Extract color palettes from images using Google Gemini 3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract 6 main colors
  %(prog)s screenshot.png

  # Extract as CSS variables
  %(prog)s -f css -o colors.css brand_image.png

  # Get Tailwind config
  %(prog)s -f tailwind -o tailwind.config.js design.png

  # Detailed palette with contrast info
  %(prog)s -n 8 --named --contrast hero_image.jpg

  # SCSS variables
  %(prog)s -f scss -o _colors.scss mockup.png

Output Formats:
  text      Human-readable text output
  json      JSON object with full color data
  css       CSS custom properties (:root variables)
  tailwind  Tailwind config.js extend colors
  scss      SCSS variables and color map

Environment:
  GEMINI_API_KEY  Required. Get from https://aistudio.google.com/apikey
        """
    )

    parser.add_argument(
        "image",
        help="Image to extract colors from"
    )
    parser.add_argument(
        "-n", "--count",
        type=int,
        default=DEFAULT_COLOR_COUNT,
        help=f"Number of colors to extract (default: {DEFAULT_COLOR_COUNT})"
    )
    parser.add_argument(
        "-f", "--format",
        default="text",
        choices=VALID_FORMATS,
        dest="output_format",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Save palette to file"
    )
    parser.add_argument(
        "--named",
        action="store_true",
        help="Include closest CSS color names"
    )
    parser.add_argument(
        "--contrast",
        action="store_true",
        help="Calculate contrast ratios between colors"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed progress"
    )

    args = parser.parse_args()

    # Validate count
    if args.count < 1 or args.count > 20:
        print("Error: Color count must be between 1 and 20", file=sys.stderr)
        sys.exit(EXIT_INVALID_ARGS)

    # Extract colors
    result = extract_colors(
        image_path=args.image,
        count=args.count,
        output_format=args.output_format,
        include_named=args.named,
        include_contrast=args.contrast,
        verbose=args.verbose,
    )

    # Save or print output
    if args.output:
        save_output(result, args.output, args.verbose)
        print(f"Palette saved to: {args.output}")
    else:
        print(result)

    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
