#!/usr/bin/env python3
"""
Screenshot to Code - Convert UI screenshots to HTML/CSS using Google Gemini 3.

Generates code from design screenshots with support for multiple CSS frameworks.
"""

import argparse
import json
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
DEFAULT_MODEL = "gemini-3-pro-preview"
VALID_FRAMEWORKS = ["tailwind", "css", "bootstrap", "vanilla"]
VALID_RESOLUTIONS = ["low", "medium", "high", "ultra_high"]
VALID_THINKING = ["low", "high"]

RESOLUTION_MAP = {
    "low": "MEDIA_RESOLUTION_LOW",
    "medium": "MEDIA_RESOLUTION_MEDIUM",
    "high": "MEDIA_RESOLUTION_HIGH",
    "ultra_high": "MEDIA_RESOLUTION_HIGH",  # ultra_high maps to high (highest available)
}

# Framework-specific prompts
FRAMEWORK_PROMPTS = {
    "tailwind": """Convert this UI screenshot to HTML with Tailwind CSS classes.

Requirements:
- Use semantic HTML5 elements
- Use Tailwind CSS utility classes for all styling
- Match the visual design as closely as possible
- Use appropriate color classes (or custom colors if needed)
- Ensure responsive design with Tailwind breakpoints
- Use Flexbox/Grid utilities for layout
- Include proper spacing (p-*, m-*)
- Match typography (text-*, font-*)

Output format:
```html
<!-- Your HTML with Tailwind classes here -->
```

If custom colors are needed, include a Tailwind config snippet:
```javascript
// tailwind.config.js colors
```""",

    "css": """Convert this UI screenshot to HTML with custom CSS.

Requirements:
- Use semantic HTML5 elements
- Write clean, organized CSS with comments
- Use CSS custom properties (variables) for colors
- Match the visual design as closely as possible
- Use Flexbox or Grid for layout
- Ensure proper spacing and typography
- Add meaningful class names (BEM or similar)

Output format:
```html
<!-- Your HTML here -->
```

```css
/* Your CSS here */
```""",

    "bootstrap": """Convert this UI screenshot to HTML with Bootstrap 5.

Requirements:
- Use Bootstrap 5 components and utilities
- Use semantic HTML5 elements
- Leverage Bootstrap's grid system
- Match the visual design using Bootstrap classes
- Use Bootstrap spacing utilities (m-*, p-*)
- Include custom CSS only when Bootstrap doesn't cover it
- Use Bootstrap components where applicable (cards, buttons, navs)

Output format:
```html
<!-- Your HTML with Bootstrap classes here -->
```

If custom CSS is needed:
```css
/* Additional custom CSS */
```""",

    "vanilla": """Convert this UI screenshot to plain HTML and CSS.

Requirements:
- Use semantic HTML5 elements only
- Write vanilla CSS (no frameworks)
- Match the visual design as closely as possible
- Use CSS Flexbox or Grid for layout
- Ensure the code is clean and well-organized
- Use meaningful class names
- Include comments for clarity
- Make it responsive with media queries

Output format:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Title</title>
    <style>
        /* Your CSS here */
    </style>
</head>
<body>
    <!-- Your HTML here -->
</body>
</html>
```"""
}

COMPONENT_ADDITION = """

Additionally, structure the code as reusable components:
- Identify distinct UI components (header, card, button, form, etc.)
- Separate each component clearly with comments
- Make components self-contained and reusable
- Provide usage examples for each component"""

RESPONSIVE_ADDITION = """

Ensure full responsiveness:
- Mobile-first approach
- Include breakpoints for tablet and desktop
- Adjust layout and spacing for each breakpoint
- Handle text scaling appropriately
- Consider touch targets on mobile"""


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


def extract_code_blocks(response: str) -> dict:
    """Extract code blocks from response."""
    result = {
        "html": "",
        "css": "",
        "js": "",
        "config": "",
        "full": response,
    }

    # Extract HTML blocks
    html_matches = re.findall(r'```html\n([\s\S]*?)```', response)
    if html_matches:
        result["html"] = "\n\n".join(html_matches)

    # Extract CSS blocks
    css_matches = re.findall(r'```css\n([\s\S]*?)```', response)
    if css_matches:
        result["css"] = "\n\n".join(css_matches)

    # Extract JS/config blocks
    js_matches = re.findall(r'```(?:javascript|js)\n([\s\S]*?)```', response)
    if js_matches:
        result["js"] = "\n\n".join(js_matches)

    return result


def convert_screenshot(
    image_path: str,
    framework: str = "tailwind",
    components: bool = False,
    responsive: bool = False,
    resolution: str = "ultra_high",
    thinking_level: str = "high",
    verbose: bool = False,
) -> dict:
    """Convert a screenshot to code using Gemini 3."""
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
        print(f"[*] Framework: {framework}")
        print(f"[*] Components: {components}")
        print(f"[*] Responsive: {responsive}")
        print(f"[*] Resolution: {resolution}")

    # Load image
    image_data, mime_type = load_image(image_path)

    if verbose:
        print(f"[*] Image loaded ({len(image_data)} bytes)")
        print(f"[*] Initializing Gemini client...")

    # Initialize client
    client = genai.Client(api_key=api_key)

    # Build prompt
    prompt = FRAMEWORK_PROMPTS[framework]
    if components:
        prompt += COMPONENT_ADDITION
    if responsive:
        prompt += RESPONSIVE_ADDITION

    # Build content
    contents = [
        types.Part.from_bytes(data=image_data, mime_type=mime_type),
        prompt,
    ]

    # Configure generation with media resolution
    config = types.GenerateContentConfig(
        temperature=0.7,  # Slightly creative for code generation
        media_resolution=getattr(types.MediaResolution, RESOLUTION_MAP[resolution]),
    )

    if verbose:
        print(f"[*] Generating code...")

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
        print(f"[*] Code generation complete")

    # Extract response
    if not response.candidates:
        print("Error: No response from API.", file=sys.stderr)
        sys.exit(EXIT_API_ERROR)

    try:
        response_text = response.text
    except Exception:
        print("Error: Could not extract text from response.", file=sys.stderr)
        sys.exit(EXIT_API_ERROR)

    return extract_code_blocks(response_text)


def save_output(
    code: dict,
    output_dir: str,
    framework: str,
    verbose: bool = False,
) -> list[str]:
    """Save generated code to files."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    saved_files = []

    # Determine file names based on framework
    if framework == "vanilla":
        # Single HTML file with embedded CSS
        if code["html"]:
            file_path = output_path / "index.html"
            file_path.write_text(code["html"])
            saved_files.append(str(file_path))
            if verbose:
                print(f"[*] Saved: {file_path}")
    else:
        # Separate files
        if code["html"]:
            file_path = output_path / "index.html"
            file_path.write_text(code["html"])
            saved_files.append(str(file_path))
            if verbose:
                print(f"[*] Saved: {file_path}")

        if code["css"]:
            file_path = output_path / "styles.css"
            file_path.write_text(code["css"])
            saved_files.append(str(file_path))
            if verbose:
                print(f"[*] Saved: {file_path}")

        if code["js"]:
            if framework == "tailwind":
                file_path = output_path / "tailwind.config.js"
            else:
                file_path = output_path / "script.js"
            file_path.write_text(code["js"])
            saved_files.append(str(file_path))
            if verbose:
                print(f"[*] Saved: {file_path}")

    # Always save full response
    full_path = output_path / "full_response.md"
    full_path.write_text(code["full"])
    saved_files.append(str(full_path))
    if verbose:
        print(f"[*] Saved: {full_path}")

    return saved_files


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Convert UI screenshots to HTML/CSS using Google Gemini 3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert to Tailwind HTML
  %(prog)s landing_page.png

  # Generate vanilla HTML/CSS
  %(prog)s -f vanilla mockup.png

  # Create responsive Bootstrap components
  %(prog)s -f bootstrap -c --responsive card.png -o ./output

  # Full page with all options
  %(prog)s -f tailwind -c --responsive -o ./components page.png

Frameworks:
  tailwind   Tailwind CSS utility classes
  css        Custom CSS with variables
  bootstrap  Bootstrap 5 components and utilities
  vanilla    Plain HTML/CSS, no frameworks

Environment:
  GEMINI_API_KEY  Required. Get from https://aistudio.google.com/apikey
        """
    )

    parser.add_argument(
        "image",
        help="UI screenshot to convert"
    )
    parser.add_argument(
        "-f", "--framework",
        default="tailwind",
        choices=VALID_FRAMEWORKS,
        help="CSS framework (default: tailwind)"
    )
    parser.add_argument(
        "-c", "--components",
        action="store_true",
        help="Extract as reusable components"
    )
    parser.add_argument(
        "--responsive",
        action="store_true",
        help="Generate responsive code"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output directory for files"
    )
    parser.add_argument(
        "-r", "--resolution",
        default="ultra_high",
        choices=VALID_RESOLUTIONS,
        help="Media resolution (default: ultra_high)"
    )
    parser.add_argument(
        "--thinking",
        default="high",
        choices=VALID_THINKING,
        help="Thinking level (default: high)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed progress"
    )

    args = parser.parse_args()

    # Convert screenshot
    code = convert_screenshot(
        image_path=args.image,
        framework=args.framework,
        components=args.components,
        responsive=args.responsive,
        resolution=args.resolution,
        thinking_level=args.thinking,
        verbose=args.verbose,
    )

    # Save or print output
    if args.output:
        saved_files = save_output(
            code,
            args.output,
            args.framework,
            args.verbose,
        )
        print(f"Files saved to: {args.output}")
        for f in saved_files:
            print(f"  - {Path(f).name}")
    else:
        # Print to stdout
        print(code["full"])

    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
