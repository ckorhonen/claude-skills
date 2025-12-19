#!/usr/bin/env python3
"""
Compare Designs - Compare two UI designs using Google Gemini 3.

Analyze differences between design versions, A/B variants, or before/after screenshots.
"""

import argparse
import json
import os
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
VALID_MODES = ["full", "visual", "content", "accessibility"]
VALID_RESOLUTIONS = ["low", "medium", "high", "ultra_high"]
VALID_FORMATS = ["text", "json", "markdown"]

RESOLUTION_MAP = {
    "low": "MEDIA_RESOLUTION_LOW",
    "medium": "MEDIA_RESOLUTION_MEDIUM",
    "high": "MEDIA_RESOLUTION_HIGH",
    "ultra_high": "MEDIA_RESOLUTION_HIGH",  # ultra_high maps to high (highest available)
}

# Comparison prompts
COMPARISON_PROMPTS = {
    "full": """Compare these two UI designs comprehensively. The first image is the "before" or "version A", and the second is the "after" or "version B".

Analyze and compare:

1. **Visual Changes**
   - Color scheme differences
   - Typography changes
   - Spacing and layout modifications
   - Icon/imagery updates

2. **Layout & Structure**
   - Component arrangement
   - Visual hierarchy shifts
   - Grid/alignment changes
   - Whitespace usage

3. **Content Changes**
   - Text/copy differences
   - Information architecture
   - New/removed elements
   - Navigation changes

4. **UX Impact**
   - Usability improvements or regressions
   - Clarity changes
   - User flow modifications
   - Cognitive load comparison

5. **Accessibility Impact**
   - Contrast changes
   - Readability differences
   - Touch target modifications
   - Screen reader considerations

6. **Overall Assessment**
   - Key improvements
   - Potential concerns
   - Recommendation (which is better and why)

Be specific about exact differences with element locations.""",

    "visual": """Compare the visual design of these two UI screenshots. First is "before/A", second is "after/B".

Focus on:

1. **Color Palette**
   - Primary, secondary, accent color changes
   - Background color differences
   - Text color modifications
   - Brand color consistency

2. **Typography**
   - Font family changes
   - Size hierarchy differences
   - Weight/style modifications
   - Line height/spacing

3. **Spacing & Layout**
   - Padding/margin changes
   - Component spacing
   - Grid alignment
   - Whitespace distribution

4. **Visual Elements**
   - Icon style changes
   - Image treatment differences
   - Border/shadow modifications
   - Decorative element updates

5. **Visual Hierarchy**
   - Emphasis changes
   - Focal point shifts
   - Contrast differences

Provide specific observations with element references.""",

    "content": """Compare the content and information architecture of these two UI designs. First is "before/A", second is "after/B".

Analyze:

1. **Text Content**
   - Headlines/titles changed
   - Body copy differences
   - Labels and microcopy
   - Call-to-action text

2. **Information Structure**
   - Content organization
   - Grouping changes
   - Section ordering
   - Navigation structure

3. **Elements Added/Removed**
   - New components
   - Removed elements
   - Modified sections
   - Feature additions

4. **Data Presentation**
   - Data visualization changes
   - Table/list modifications
   - Chart/graph updates
   - Metric displays

5. **User Journey**
   - Flow changes
   - Step modifications
   - Entry/exit points
   - Path clarity

Highlight what users will notice most.""",

    "accessibility": """Compare the accessibility of these two UI designs. First is "before/A", second is "after/B".

Evaluate changes in:

1. **Color Contrast**
   - Text contrast improvements/regressions
   - UI element contrast
   - Focus indicator visibility
   - WCAG level changes

2. **Text Readability**
   - Font size changes
   - Line height modifications
   - Text spacing
   - Reading ease

3. **Interactive Elements**
   - Touch target size changes
   - Button/link clarity
   - Focus states
   - Clickable area modifications

4. **Visual Accessibility**
   - Color-only information
   - Pattern/texture usage
   - Icon clarity
   - Alternative indicators

5. **Screen Reader Considerations**
   - Heading structure
   - Reading order
   - Label clarity
   - Alternative text needs

6. **Overall A11y Impact**
   - WCAG compliance changes
   - Improvement areas
   - Regression concerns
   - Recommendations

Rate each design's accessibility and indicate which is more accessible."""
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
        ".heic": "image/heic",
        ".heif": "image/heif",
    }

    mime_type = mime_types.get(suffix)
    if not mime_type:
        print(f"Error: Unsupported image format: {suffix}", file=sys.stderr)
        print(f"Supported formats: {', '.join(mime_types.keys())}", file=sys.stderr)
        sys.exit(EXIT_INVALID_ARGS)

    return path.read_bytes(), mime_type


def compare_designs(
    image1_path: str,
    image2_path: str,
    mode: str = "full",
    resolution: str = "high",
    output_format: str = "text",
    verbose: bool = False,
) -> str:
    """Compare two design images using Gemini 3."""
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("Error: google-genai package not installed.", file=sys.stderr)
        print("Install it with: pip install google-genai", file=sys.stderr)
        sys.exit(EXIT_INVALID_ARGS)

    api_key = get_api_key()

    if verbose:
        print(f"[*] Loading image 1: {image1_path}")
        print(f"[*] Loading image 2: {image2_path}")
        print(f"[*] Comparison mode: {mode}")
        print(f"[*] Resolution: {resolution}")

    # Load images
    image1_data, mime1 = load_image(image1_path)
    image2_data, mime2 = load_image(image2_path)

    if verbose:
        print(f"[*] Image 1: {len(image1_data)} bytes, {mime1}")
        print(f"[*] Image 2: {len(image2_data)} bytes, {mime2}")
        print(f"[*] Initializing Gemini client...")

    # Initialize client
    client = genai.Client(api_key=api_key)

    # Build prompt
    base_prompt = COMPARISON_PROMPTS[mode]

    if output_format == "json":
        format_instruction = "\n\nProvide your comparison as a valid JSON object with appropriate keys for each section."
    elif output_format == "markdown":
        format_instruction = "\n\nFormat your comparison using Markdown with headers, lists, and emphasis."
    else:
        format_instruction = ""

    full_prompt = base_prompt + format_instruction

    # Build content with both images
    contents = [
        types.Part.from_bytes(data=image1_data, mime_type=mime1),
        types.Part.from_bytes(data=image2_data, mime_type=mime2),
        full_prompt,
    ]

    # Configure generation with media resolution
    config = types.GenerateContentConfig(
        temperature=1.0,
        media_resolution=getattr(types.MediaResolution, RESOLUTION_MAP[resolution]),
    )

    if verbose:
        print(f"[*] Sending comparison request...")

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
        print(f"[*] Comparison complete")

    # Extract response
    if not response.candidates:
        print("Error: No response from API.", file=sys.stderr)
        sys.exit(EXIT_API_ERROR)

    try:
        return response.text
    except Exception:
        print("Error: Could not extract text from response.", file=sys.stderr)
        sys.exit(EXIT_API_ERROR)


def save_output(content: str, output_path: str, verbose: bool = False) -> None:
    """Save comparison output to file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        path.write_text(content)
        if verbose:
            print(f"[*] Comparison saved to: {path}")
    except Exception as e:
        print(f"Error: Failed to save output: {e}", file=sys.stderr)
        sys.exit(EXIT_SAVE_ERROR)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Compare two UI designs using Google Gemini 3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full comparison
  %(prog)s before.png after.png

  # Visual-only comparison
  %(prog)s -m visual old_design.png new_design.png

  # Accessibility comparison with markdown output
  %(prog)s -m accessibility v1.png v2.png -f markdown -o report.md

  # A/B test comparison as JSON
  %(prog)s -m full variant_a.png variant_b.png -f json

Modes:
  full           Comprehensive comparison (visual, content, UX, a11y)
  visual         Colors, typography, spacing, visual hierarchy
  content        Text, information architecture, elements
  accessibility  Contrast, readability, touch targets, WCAG

Environment:
  GEMINI_API_KEY  Required. Get from https://aistudio.google.com/apikey
        """
    )

    parser.add_argument(
        "image1",
        help="First design image (before/version A)"
    )
    parser.add_argument(
        "image2",
        help="Second design image (after/version B)"
    )
    parser.add_argument(
        "-m", "--mode",
        default="full",
        choices=VALID_MODES,
        help="Comparison mode (default: full)"
    )
    parser.add_argument(
        "-r", "--resolution",
        default="high",
        choices=VALID_RESOLUTIONS,
        help="Media resolution (default: high)"
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
        help="Save comparison to file"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed progress"
    )

    args = parser.parse_args()

    # Run comparison
    result = compare_designs(
        image1_path=args.image1,
        image2_path=args.image2,
        mode=args.mode,
        resolution=args.resolution,
        output_format=args.output_format,
        verbose=args.verbose,
    )

    # Save or print output
    if args.output:
        save_output(result, args.output, args.verbose)
        print(f"Comparison saved to: {args.output}")
    else:
        print(result)

    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
