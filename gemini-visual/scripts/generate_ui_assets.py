#!/usr/bin/env python3
"""
Generate UI Assets - Create UI assets using Google Gemini 3 Pro Image.

Generate icons, backgrounds, patterns, illustrations, and badges for UI development.
"""

import argparse
import os
import re
import sys
from datetime import datetime
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
DEFAULT_MODEL = "gemini-3-pro-image-preview"
FALLBACK_MODEL = "gemini-2.5-flash-image"

VALID_ASSET_TYPES = ["icon", "background", "pattern", "illustration", "badge"]
VALID_STYLES = [
    "modern", "minimal", "flat", "gradient", "glassmorphism",
    "neumorphism", "material", "ios", "outlined", "filled"
]
VALID_ASPECT_RATIOS = [
    "1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"
]
VALID_SIZES = ["1K", "2K", "4K"]

# Asset type prompts
ASSET_PROMPTS = {
    "icon": "Create a UI icon: {prompt}. Style: {style}. The icon should be clean, scalable, and suitable for app interfaces. Centered composition with appropriate padding. {color_instruction}",

    "background": "Create a UI background: {prompt}. Style: {style}. The background should be visually appealing but not distracting, suitable as a backdrop for UI elements. {color_instruction}",

    "pattern": "Create a seamless pattern: {prompt}. Style: {style}. The pattern should tile seamlessly and work well as a subtle background or texture for UI components. {color_instruction}",

    "illustration": "Create a UI illustration: {prompt}. Style: {style}. The illustration should be clean, modern, and suitable for onboarding screens, empty states, or feature highlights. {color_instruction}",

    "badge": "Create a UI badge or label: {prompt}. Style: {style}. The badge should be compact, readable, and suitable for status indicators or labels. {color_instruction}",
}

# Style modifiers
STYLE_MODIFIERS = {
    "modern": "clean lines, contemporary aesthetic, subtle shadows",
    "minimal": "extremely simple, essential elements only, lots of whitespace",
    "flat": "no gradients, no shadows, solid colors, 2D appearance",
    "gradient": "smooth color gradients, vibrant transitions, depth through color",
    "glassmorphism": "frosted glass effect, transparency, blur, subtle borders",
    "neumorphism": "soft shadows, extruded appearance, subtle 3D effect",
    "material": "Material Design style, bold colors, clear shadows, rounded corners",
    "ios": "iOS style, SF Symbols aesthetic, thin lines, subtle gradients",
    "outlined": "line-based, stroke only, no fill, clean outlines",
    "filled": "solid filled shapes, no outlines, bold appearance",
}


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
    }

    mime_type = mime_types.get(suffix)
    if not mime_type:
        print(f"Error: Unsupported image format: {suffix}", file=sys.stderr)
        print(f"Supported formats: {', '.join(mime_types.keys())}", file=sys.stderr)
        sys.exit(EXIT_INVALID_ARGS)

    return path.read_bytes(), mime_type


def generate_filename(prompt: str, asset_type: str) -> str:
    """Generate a descriptive filename from the prompt."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:18]
    slug = re.sub(r"[^a-zA-Z0-9\s]", "", prompt)[:25].strip()
    slug = re.sub(r"\s+", "_", slug).lower()
    return f"{asset_type}_{timestamp}_{slug}.png"


def build_prompt(
    prompt: str,
    asset_type: str,
    style: str,
    colors: Optional[str] = None,
) -> str:
    """Build the full generation prompt."""
    # Get base template
    template = ASSET_PROMPTS[asset_type]

    # Build color instruction
    if colors:
        color_instruction = f"Use these colors: {colors}."
    else:
        color_instruction = ""

    # Get style modifier
    style_mod = STYLE_MODIFIERS.get(style, style)

    # Build full prompt
    full_prompt = template.format(
        prompt=prompt,
        style=style_mod,
        color_instruction=color_instruction,
    )

    return full_prompt


def generate_asset(
    prompt: str,
    asset_type: str = "icon",
    style: str = "modern",
    colors: Optional[str] = None,
    aspect_ratio: str = "1:1",
    size: str = "1K",
    reference_image: Optional[str] = None,
    verbose: bool = False,
) -> bytes:
    """Generate a UI asset using Gemini 3 Pro Image."""
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("Error: google-genai package not installed.", file=sys.stderr)
        print("Install it with: pip install google-genai", file=sys.stderr)
        sys.exit(EXIT_INVALID_ARGS)

    api_key = get_api_key()

    if verbose:
        print(f"[*] Asset type: {asset_type}")
        print(f"[*] Style: {style}")
        print(f"[*] Aspect ratio: {aspect_ratio}")
        print(f"[*] Size: {size}")
        if colors:
            print(f"[*] Colors: {colors}")

    # Initialize client
    client = genai.Client(api_key=api_key)

    # Build content
    contents = []

    # Add reference image if provided
    if reference_image:
        if verbose:
            print(f"[*] Loading reference image: {reference_image}")
        img_data, mime_type = load_image(reference_image)
        contents.append(
            types.Part.from_bytes(data=img_data, mime_type=mime_type)
        )

    # Build and add prompt
    full_prompt = build_prompt(prompt, asset_type, style, colors)

    # Add aspect ratio instruction
    if aspect_ratio != "1:1":
        full_prompt = f"{full_prompt} (generate with {aspect_ratio} aspect ratio)"

    # Add size instruction
    if size != "1K":
        resolution_map = {"2K": "2048", "4K": "4096"}
        full_prompt = f"{full_prompt} (high resolution: {resolution_map.get(size, '1024')}px)"

    contents.append(full_prompt)

    if verbose:
        print(f"[*] Generating asset...")

    # Configure for image output
    config = types.GenerateContentConfig(
        response_modalities=["IMAGE", "TEXT"],
    )

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
        elif "content" in error_msg.lower() or "policy" in error_msg.lower():
            print("Error: Content policy violation. Try modifying your prompt.", file=sys.stderr)
        else:
            print(f"Error: API request failed: {error_msg}", file=sys.stderr)
        sys.exit(EXIT_API_ERROR)

    # Extract image from response
    if not response.candidates:
        print("Error: No candidates in API response.", file=sys.stderr)
        sys.exit(EXIT_API_ERROR)

    candidate = response.candidates[0]
    if not hasattr(candidate, "content") or not hasattr(candidate.content, "parts"):
        print("Error: Unexpected response structure from API.", file=sys.stderr)
        sys.exit(EXIT_API_ERROR)

    for part in candidate.content.parts:
        if part.inline_data is not None:
            if verbose:
                print(f"[*] Asset generated successfully")
            return part.inline_data.data

    print("Error: No image in response. The model may have returned text only.", file=sys.stderr)
    try:
        if response.text:
            print(f"Model response: {response.text}", file=sys.stderr)
    except Exception:
        pass
    sys.exit(EXIT_API_ERROR)


def save_image(image_data: bytes, output_path: str, verbose: bool = False) -> str:
    """Save image data to file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        path.write_bytes(image_data)
        if verbose:
            print(f"[*] Saved to: {path}")
        return str(path)
    except Exception as e:
        print(f"Error: Failed to save image: {e}", file=sys.stderr)
        sys.exit(EXIT_SAVE_ERROR)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate UI assets using Google Gemini 3 Pro Image",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate app icon
  %(prog)s -p "Weather app icon with sun and clouds" -t icon

  # Create gradient background
  %(prog)s -p "Soft gradient for login screen" -t background \\
    -c "#667eea,#764ba2" -a 9:16 -o login_bg.png

  # Generate pattern
  %(prog)s -p "Subtle geometric pattern" -t pattern -s minimal

  # Create illustration with reference
  %(prog)s -p "Onboarding illustration" -t illustration -r brand_style.png

Asset Types:
  icon          App icons, toolbar icons, navigation icons
  background    Screen backgrounds, card backgrounds, gradients
  pattern       Seamless patterns, textures, repeating designs
  illustration  Feature illustrations, empty states, onboarding
  badge         Status badges, labels, tags

Styles:
  modern        Clean, contemporary
  minimal       Simple, essential
  flat          No gradients or shadows
  gradient      Smooth color transitions
  glassmorphism Frosted glass effect
  neumorphism   Soft 3D shadows
  material      Material Design
  ios           Apple iOS style
  outlined      Line-based, no fill
  filled        Solid shapes

Environment:
  GEMINI_API_KEY  Required. Get from https://aistudio.google.com/apikey
        """
    )

    parser.add_argument(
        "-p", "--prompt",
        required=True,
        help="Description of the asset to generate"
    )
    parser.add_argument(
        "-t", "--type",
        default="icon",
        choices=VALID_ASSET_TYPES,
        dest="asset_type",
        help="Asset type (default: icon)"
    )
    parser.add_argument(
        "-s", "--style",
        default="modern",
        choices=VALID_STYLES,
        help="Design style (default: modern)"
    )
    parser.add_argument(
        "-c", "--colors",
        help="Color palette (comma-separated HEX codes or color names)"
    )
    parser.add_argument(
        "-a", "--aspect-ratio",
        default="1:1",
        choices=VALID_ASPECT_RATIOS,
        help="Aspect ratio (default: 1:1)"
    )
    parser.add_argument(
        "--size",
        default="1K",
        choices=VALID_SIZES,
        help="Resolution: 1K, 2K, 4K (default: 1K)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: auto-generated)"
    )
    parser.add_argument(
        "-r", "--reference",
        help="Reference image for style guidance"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed progress"
    )

    args = parser.parse_args()

    # Validate reference image if provided
    if args.reference and not Path(args.reference).exists():
        print(f"Error: Reference image not found: {args.reference}", file=sys.stderr)
        sys.exit(EXIT_FILE_NOT_FOUND)

    # Generate asset
    image_data = generate_asset(
        prompt=args.prompt,
        asset_type=args.asset_type,
        style=args.style,
        colors=args.colors,
        aspect_ratio=args.aspect_ratio,
        size=args.size,
        reference_image=args.reference,
        verbose=args.verbose,
    )

    # Determine output path
    output_path = args.output or generate_filename(args.prompt, args.asset_type)

    # Save image
    saved_path = save_image(image_data, output_path, args.verbose)

    print(f"Asset saved to: {saved_path}")
    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
