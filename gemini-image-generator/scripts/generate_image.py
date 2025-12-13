#!/usr/bin/env python3
"""
Gemini Image Generator - Generate images using Google's Gemini API.

Supports text-to-image generation, image editing, and multi-image reference inputs.
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

# Valid configurations
VALID_MODELS = [
    "gemini-2.5-flash-image",
    "gemini-3-pro-image-preview",
]
DEFAULT_MODEL = "gemini-3-pro-image-preview"

VALID_ASPECT_RATIOS = [
    "1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"
]
DEFAULT_ASPECT_RATIO = "1:1"

VALID_SIZES = ["1K", "2K", "4K"]
DEFAULT_SIZE = "1K"

MAX_REFERENCE_IMAGES = 14


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


def generate_filename(prompt: str) -> str:
    """Generate a descriptive filename from the prompt."""
    # Include microseconds to avoid collisions in rapid successive calls
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:18]
    # Create slug from prompt (first 30 chars, alphanumeric and spaces only)
    slug = re.sub(r"[^a-zA-Z0-9\s]", "", prompt)[:30].strip()
    slug = re.sub(r"\s+", "_", slug).lower()
    return f"gemini_{timestamp}_{slug}.png"


def validate_args(args: argparse.Namespace) -> None:
    """Validate command-line arguments."""
    # Check model
    if args.model not in VALID_MODELS:
        print(f"Error: Invalid model '{args.model}'", file=sys.stderr)
        print(f"Valid models: {', '.join(VALID_MODELS)}", file=sys.stderr)
        sys.exit(EXIT_INVALID_ARGS)

    # Check aspect ratio
    if args.aspect_ratio not in VALID_ASPECT_RATIOS:
        print(f"Error: Invalid aspect ratio '{args.aspect_ratio}'", file=sys.stderr)
        print(f"Valid ratios: {', '.join(VALID_ASPECT_RATIOS)}", file=sys.stderr)
        sys.exit(EXIT_INVALID_ARGS)

    # Check size
    if args.size not in VALID_SIZES:
        print(f"Error: Invalid size '{args.size}'", file=sys.stderr)
        print(f"Valid sizes: {', '.join(VALID_SIZES)}", file=sys.stderr)
        sys.exit(EXIT_INVALID_ARGS)

    # Check size compatibility with model
    if args.size != "1K" and args.model == "gemini-2.5-flash-image":
        print(f"Warning: Size '{args.size}' only supported by gemini-3-pro-image-preview", file=sys.stderr)
        print("Using 1K for gemini-2.5-flash-image", file=sys.stderr)
        args.size = "1K"

    # Check reference images limit
    if args.reference_images and len(args.reference_images) > MAX_REFERENCE_IMAGES:
        print(f"Error: Maximum {MAX_REFERENCE_IMAGES} reference images allowed", file=sys.stderr)
        sys.exit(EXIT_INVALID_ARGS)

    # Verify input files exist
    if args.input_image and not Path(args.input_image).exists():
        print(f"Error: Input image not found: {args.input_image}", file=sys.stderr)
        sys.exit(EXIT_FILE_NOT_FOUND)

    if args.reference_images:
        for ref_path in args.reference_images:
            if not Path(ref_path).exists():
                print(f"Error: Reference image not found: {ref_path}", file=sys.stderr)
                sys.exit(EXIT_FILE_NOT_FOUND)


def generate_image(
    prompt: str,
    model: str = DEFAULT_MODEL,
    aspect_ratio: str = DEFAULT_ASPECT_RATIO,
    size: str = DEFAULT_SIZE,
    input_image: Optional[str] = None,
    reference_images: Optional[list[str]] = None,
    verbose: bool = False,
) -> bytes:
    """Generate an image using the Gemini API."""
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("Error: google-genai package not installed.", file=sys.stderr)
        print("Install it with: pip install google-genai", file=sys.stderr)
        sys.exit(EXIT_INVALID_ARGS)

    api_key = get_api_key()

    if verbose:
        print(f"[*] Configuring Gemini client...")
        print(f"[*] Model: {model}")
        print(f"[*] Aspect ratio: {aspect_ratio}")
        print(f"[*] Size: {size}")

    # Initialize client
    client = genai.Client(api_key=api_key)

    # Build content parts
    contents = []

    # Add reference images first (if any)
    if reference_images:
        if verbose:
            print(f"[*] Loading {len(reference_images)} reference image(s)...")
        for ref_path in reference_images:
            img_data, mime_type = load_image(ref_path)
            contents.append(
                types.Part.from_bytes(data=img_data, mime_type=mime_type)
            )

    # Add input image for editing (if any)
    if input_image:
        if verbose:
            print(f"[*] Loading input image for editing: {input_image}")
        img_data, mime_type = load_image(input_image)
        contents.append(
            types.Part.from_bytes(data=img_data, mime_type=mime_type)
        )

    # Build enhanced prompt with aspect ratio and size guidance
    enhanced_prompt = prompt

    # Add aspect ratio instruction
    if aspect_ratio != "1:1":
        enhanced_prompt = f"{prompt} (generate with {aspect_ratio} aspect ratio)"

    # Add size instruction for Pro model
    if model == "gemini-3-pro-image-preview" and size != "1K":
        resolution_map = {"2K": "2048", "4K": "4096"}
        enhanced_prompt = f"{enhanced_prompt} (high resolution: {resolution_map.get(size, '1024')}px)"

    # Add text prompt
    contents.append(enhanced_prompt)

    # Configure generation for image output
    config = types.GenerateContentConfig(
        response_modalities=["IMAGE", "TEXT"],
    )

    if verbose:
        print(f"[*] Generating image...")

    try:
        response = client.models.generate_content(
            model=model,
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

    # Extract image from response with proper error handling
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
                print(f"[*] Image generated successfully")
            return part.inline_data.data

    print("Error: No image in response. The model may have returned text only.", file=sys.stderr)
    try:
        if response.text:
            print(f"Model response: {response.text}", file=sys.stderr)
    except Exception:
        pass  # Ignore if text attribute not available
    sys.exit(EXIT_API_ERROR)


def save_image(image_data: bytes, output_path: str, verbose: bool = False) -> str:
    """Save image data to file."""
    path = Path(output_path)

    # Create parent directories if needed
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        path.write_bytes(image_data)
        if verbose:
            print(f"[*] Saving to: {path}")
        return str(path)
    except Exception as e:
        print(f"Error: Failed to save image: {e}", file=sys.stderr)
        sys.exit(EXIT_SAVE_ERROR)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate images using Google's Gemini API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic text-to-image
  %(prog)s -p "A fluffy orange cat sitting on a windowsill"

  # Specify output and aspect ratio
  %(prog)s -p "Tech startup banner" -o banner.png -a 16:9

  # Use faster model
  %(prog)s -p "Quick sketch of a robot" -m gemini-2.5-flash-image

  # Edit an existing image
  %(prog)s -p "Make the sky more dramatic" -i photo.jpg -o edited.png

  # Use reference images
  %(prog)s -p "Create similar style" -r ref1.png -r ref2.png

Environment:
  GEMINI_API_KEY  Required. Get from https://aistudio.google.com/apikey
        """
    )

    parser.add_argument(
        "-p", "--prompt",
        required=True,
        help="Text prompt describing the image to generate"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: auto-generated)"
    )
    parser.add_argument(
        "-m", "--model",
        default=DEFAULT_MODEL,
        choices=VALID_MODELS,
        help=f"Model to use (default: {DEFAULT_MODEL})"
    )
    parser.add_argument(
        "-a", "--aspect-ratio",
        default=DEFAULT_ASPECT_RATIO,
        choices=VALID_ASPECT_RATIOS,
        help=f"Aspect ratio (default: {DEFAULT_ASPECT_RATIO})"
    )
    parser.add_argument(
        "-s", "--size",
        default=DEFAULT_SIZE,
        choices=VALID_SIZES,
        help=f"Image size - Pro model only (default: {DEFAULT_SIZE})"
    )
    parser.add_argument(
        "-i", "--input-image",
        help="Input image for editing mode"
    )
    parser.add_argument(
        "-r", "--reference-images",
        action="append",
        help=f"Reference image(s) for style guidance (max {MAX_REFERENCE_IMAGES})"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed progress"
    )

    args = parser.parse_args()

    # Validate arguments
    validate_args(args)

    # Generate image
    image_data = generate_image(
        prompt=args.prompt,
        model=args.model,
        aspect_ratio=args.aspect_ratio,
        size=args.size,
        input_image=args.input_image,
        reference_images=args.reference_images,
        verbose=args.verbose,
    )

    # Determine output path
    output_path = args.output or generate_filename(args.prompt)

    # Save image
    saved_path = save_image(image_data, output_path, args.verbose)

    print(f"Image saved to: {saved_path}")
    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
