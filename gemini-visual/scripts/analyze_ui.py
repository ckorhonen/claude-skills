#!/usr/bin/env python3
"""
Analyze UI - Analyze UI screenshots using Google Gemini 3's visual reasoning.

Provides comprehensive analysis of UI screenshots including layout, accessibility,
visual hierarchy, and UX patterns.
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Exit codes
EXIT_SUCCESS = 0
EXIT_MISSING_API_KEY = 1
EXIT_INVALID_ARGS = 2
EXIT_FILE_NOT_FOUND = 3
EXIT_API_ERROR = 4
EXIT_SAVE_ERROR = 5

# Configuration
DEFAULT_MODEL = "gemini-3-pro-preview"
VALID_MODES = ["comprehensive", "accessibility", "layout", "ux"]
VALID_RESOLUTIONS = ["low", "medium", "high", "ultra_high"]
VALID_FORMATS = ["text", "json", "markdown"]
VALID_THINKING = ["low", "high"]

RESOLUTION_MAP = {
    "low": "MEDIA_RESOLUTION_LOW",
    "medium": "MEDIA_RESOLUTION_MEDIUM",
    "high": "MEDIA_RESOLUTION_HIGH",
    "ultra_high": "MEDIA_RESOLUTION_HIGH",  # ultra_high maps to high (highest available)
}

# Analysis prompts for each mode
ANALYSIS_PROMPTS = {
    "comprehensive": """Analyze this UI screenshot comprehensively. Provide detailed analysis of:

1. **Layout & Structure**
   - Visual hierarchy and information architecture
   - Grid system and alignment
   - Spacing consistency (padding, margins)
   - Responsive design considerations

2. **Visual Design**
   - Color scheme and palette usage
   - Typography (fonts, sizes, hierarchy)
   - Iconography and imagery
   - Visual consistency

3. **Accessibility**
   - Estimated contrast ratios for text
   - Touch target sizes
   - Potential screen reader issues
   - Color blindness considerations

4. **UX Patterns**
   - Clear call-to-action elements
   - Navigation patterns
   - Feedback mechanisms
   - Cognitive load assessment

5. **Issues & Recommendations**
   - Specific problems identified
   - Priority-ranked improvements
   - Quick wins vs major changes

Provide actionable, specific feedback with references to exact elements in the UI.""",

    "accessibility": """Perform a detailed accessibility audit of this UI screenshot. Analyze:

1. **Color Contrast**
   - Estimate contrast ratios for all text elements
   - Identify any WCAG AA/AAA failures
   - Check non-text contrast (icons, borders, focus states)

2. **Text Readability**
   - Font sizes (minimum 16px for body recommended)
   - Line height and letter spacing
   - Text over images/gradients

3. **Interactive Elements**
   - Touch target sizes (minimum 44x44px recommended)
   - Clickable area clarity
   - Focus indicators visibility

4. **Screen Reader Compatibility**
   - Logical reading order
   - Image alt text requirements
   - Form label associations
   - Heading hierarchy

5. **Color Independence**
   - Information conveyed by color alone
   - Patterns for colorblind users
   - Status indicators

6. **Motion & Animation**
   - Potential vestibular triggers
   - Auto-playing content

Provide specific WCAG 2.1 guideline references for each issue found.""",

    "layout": """Analyze the layout and visual structure of this UI screenshot:

1. **Grid & Alignment**
   - Underlying grid system
   - Alignment consistency (left, center, right)
   - Element alignment issues

2. **Visual Hierarchy**
   - Primary, secondary, tertiary content levels
   - Size and weight relationships
   - Eye flow and F/Z patterns

3. **Spacing System**
   - Padding consistency
   - Margin patterns
   - Whitespace usage
   - Breathing room

4. **Component Structure**
   - Identifiable UI components
   - Component relationships
   - Grouping and proximity

5. **Responsive Considerations**
   - Flexible vs fixed elements
   - Potential breakpoint issues
   - Content reflow patterns

6. **Issues**
   - Misaligned elements
   - Inconsistent spacing
   - Hierarchy problems
   - Cramped or sparse areas

Provide pixel-level specifics where possible.""",

    "ux": """Analyze the user experience patterns in this UI screenshot:

1. **Usability Heuristics**
   - Visibility of system status
   - Match with real world
   - User control and freedom
   - Consistency and standards
   - Error prevention
   - Recognition over recall
   - Flexibility and efficiency
   - Aesthetic and minimal design
   - Error recovery
   - Help and documentation

2. **Interaction Design**
   - Clear affordances
   - Feedback mechanisms
   - Progressive disclosure
   - Direct manipulation

3. **Information Architecture**
   - Content organization
   - Navigation clarity
   - Findability
   - Labeling

4. **Cognitive Load**
   - Complexity level
   - Decision points
   - Memory requirements
   - Learning curve

5. **Emotional Design**
   - First impression
   - Trust signals
   - Delight factors
   - Brand personality

6. **Conversion/Goals**
   - Primary CTA visibility
   - Friction points
   - User journey clarity

Provide specific, actionable UX improvements."""
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


def analyze_ui(
    image_path: str,
    mode: str = "comprehensive",
    resolution: str = "high",
    thinking_level: str = "high",
    output_format: str = "text",
    verbose: bool = False,
) -> str:
    """Analyze a UI screenshot using Gemini 3."""
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
        print(f"[*] Analysis mode: {mode}")
        print(f"[*] Resolution: {resolution}")
        print(f"[*] Thinking level: {thinking_level}")

    # Load image
    image_data, mime_type = load_image(image_path)

    if verbose:
        print(f"[*] Image loaded ({len(image_data)} bytes, {mime_type})")
        print(f"[*] Initializing Gemini client...")

    # Initialize client
    client = genai.Client(api_key=api_key)

    # Build prompt based on mode and format
    base_prompt = ANALYSIS_PROMPTS[mode]

    if output_format == "json":
        format_instruction = "\n\nProvide your analysis as a valid JSON object with appropriate keys for each section."
    elif output_format == "markdown":
        format_instruction = "\n\nFormat your analysis using Markdown with headers, lists, and emphasis."
    else:
        format_instruction = ""

    full_prompt = base_prompt + format_instruction

    # Build content with image and prompt
    contents = [
        types.Part.from_bytes(
            data=image_data,
            mime_type=mime_type,
        ),
        full_prompt,
    ]

    # Configure generation with media resolution
    config = types.GenerateContentConfig(
        temperature=1.0,  # Recommended default for Gemini 3
        media_resolution=getattr(types.MediaResolution, RESOLUTION_MAP[resolution]),
    )

    if verbose:
        print(f"[*] Sending request to Gemini 3...")

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
        print(f"[*] Analysis complete")

    # Extract text response
    if not response.candidates:
        print("Error: No response from API.", file=sys.stderr)
        sys.exit(EXIT_API_ERROR)

    try:
        return response.text
    except Exception:
        print("Error: Could not extract text from response.", file=sys.stderr)
        sys.exit(EXIT_API_ERROR)


def save_output(content: str, output_path: str, verbose: bool = False) -> None:
    """Save analysis output to file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        path.write_text(content)
        if verbose:
            print(f"[*] Analysis saved to: {path}")
    except Exception as e:
        print(f"Error: Failed to save output: {e}", file=sys.stderr)
        sys.exit(EXIT_SAVE_ERROR)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze UI screenshots using Google Gemini 3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Comprehensive analysis
  %(prog)s screenshot.png

  # Accessibility audit
  %(prog)s -m accessibility app_screen.png

  # Layout analysis with JSON output
  %(prog)s -m layout -f json -o report.json mockup.png

  # Quick UX review
  %(prog)s -m ux --thinking low mobile_app.png

Modes:
  comprehensive  Full analysis (layout, colors, typography, a11y, UX)
  accessibility  WCAG compliance, contrast, readability, screen readers
  layout         Visual hierarchy, spacing, alignment, grid
  ux             Usability heuristics, interaction patterns, flow

Environment:
  GEMINI_API_KEY  Required. Get from https://aistudio.google.com/apikey
        """
    )

    parser.add_argument(
        "image",
        help="Path to UI screenshot to analyze"
    )
    parser.add_argument(
        "-m", "--mode",
        default="comprehensive",
        choices=VALID_MODES,
        help=f"Analysis mode (default: comprehensive)"
    )
    parser.add_argument(
        "-r", "--resolution",
        default="high",
        choices=VALID_RESOLUTIONS,
        help="Media resolution for image processing (default: high)"
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
        help="Save analysis to file"
    )
    parser.add_argument(
        "--thinking",
        default="high",
        choices=VALID_THINKING,
        help="Thinking level - high for complex analysis (default: high)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed progress"
    )

    args = parser.parse_args()

    # Run analysis
    result = analyze_ui(
        image_path=args.image,
        mode=args.mode,
        resolution=args.resolution,
        thinking_level=args.thinking,
        output_format=args.output_format,
        verbose=args.verbose,
    )

    # Save or print output
    if args.output:
        save_output(result, args.output, args.verbose)
        print(f"Analysis saved to: {args.output}")
    else:
        print(result)

    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
