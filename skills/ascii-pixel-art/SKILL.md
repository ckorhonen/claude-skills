# ASCII Pixel Art Generator

Generate animated ASCII art from images with subject detection, blurred pixelated backgrounds, and dynamic visual effects.

## Description

Transform images into interactive ASCII art with sophisticated visual effects. Uses computer vision to detect subjects, creates atmospheric backgrounds, and adds cinematic animations including pulse effects, diagonal sweeps, random flickers, and interactive hover responses.

## When to Use

✅ **Use when:**
- Creating artistic visualizations of photos or portraits
- Generating retro/cyberpunk aesthetic content
- Building interactive web art pieces
- Converting images to animated HTML displays
- Creating unique social media content
- Demonstrating creative coding techniques

❌ **Do NOT use when:**
- Simple text-based ASCII art is sufficient
- Performance is critical (heavy processing required)
- Accessibility is paramount (relies on visual effects)
- Source image has no clear subject (works best with portraits/objects)
- Output needs to be static (this generates animated HTML)

## Prerequisites

**Required packages:**
```bash
pip install pillow rembg numpy
```

**System requirements:**
- Python 3.7+
- ~500MB RAM for image processing
- rembg model downloads automatically (~180MB)

## Usage

### Basic Command
```bash
python3 scripts/ascii_pixel_effect.py <input_image> [output.html]
```

### Examples
```bash
# Generate with default output name
python3 scripts/ascii_pixel_effect.py portrait.jpg

# Specify output file
python3 scripts/ascii_pixel_effect.py photo.png artwork.html

# Process multiple images
for img in *.jpg; do
  python3 scripts/ascii_pixel_effect.py "$img" "${img%.jpg}.html"
done
```

## How It Works

### 7-Step Pipeline

**1. Load and Resize**
- Opens image, converts to RGB
- Resizes to 900px width (maintains aspect ratio)
- Uses LANCZOS filter for high-quality downscaling

**2. Build Blurred Background**
- Applies Gaussian blur (radius=14)
- Darkens by 35% (multiply by 0.65)
- Desaturates 50% (blend with luminance grayscale)
- Pixelates using BOX filter downscale + NEAREST upscale
- Creates atmospheric base layer

**3. Subject Detection**
- Runs rembg to generate alpha mask
- Threshold: mask mean > 0.25 for subject detection
- **Critical:** Uses mask ONLY (no luminance supplement)
- Prevents bright backgrounds from getting ASCII chars

**4. Pixel Grid Overlay**
- White boxes at 24px intervals
- 5% opacity for subtle cyberpunk aesthetic
- Applied only to subject cells
- Static layer (drawn once)

**5. Build Character Grid**
- Cell size: 11×14 pixels
- Samples average RGB and luminance per cell
- **Subject cells:** ASCII char from density ramp, normalized color
- **Background cells:** `.` character in dark blue (40, 65, 100)
- ASCII ramp: `@#S08Xox+=;:-,. ` (inverted luminance)

**6. Composite Layers**
- Layer 1: Blurred background (base64 embedded)
- Layer 2: Pixel grid canvas
- Layer 3: ASCII character canvas
- Single wrapper div stretches all layers to match

**7. Animate (JavaScript)**
- **Sine wave pulse:** Bright subject cells oscillate
- **Diagonal shine:** Sweeping highlight effect
- **Random flicker:** 0.25% chance per cell, 2-8 frame duration
- **Hover ripple:** Interactive cyan glow within 8 cells
- **Character scatter:** Random chars on hover within 2 cells
- **Dynamic glow:** shadowBlur scales with luminance and pulse
- **Background dots:** Static 30% opacity

## Parameters

| Parameter | Value | Purpose |
|-----------|-------|---------|
| TARGET_WIDTH | 900px | Output image width |
| CELL_W × CELL_H | 11×14px | Character cell dimensions |
| GRID_STEP | 24px | Pixel grid interval |
| Blur radius | 14 | Background blur strength |
| BG darken | 0.65 | Background darkening (35% darker) |
| BG desaturate | 50% | Background color reduction |
| Subject threshold | 0.25 | Mask mean for subject detection |
| ASCII ramp | `@#S08Xox+=;:-,. ` | Density gradient (dark→light) |
| BG dot color | (40, 65, 100) | Background character RGB |
| BG dot opacity | 30% | Background character transparency |
| Grid opacity | 5% | Pixel grid visibility |

## Color Formula

```python
def normalize_color(r, g, b):
    """Preserve hue, maximize brightness"""
    mx = max(r, g, b, 1)
    return int(r/mx*255), int(g/mx*255), int(b/mx*255)
```

This normalizes RGB values so the brightest channel reaches 255, preserving hue while maximizing color saturation for subject pixels.

## Output

**Self-contained HTML file:**
- No external dependencies
- Background image base64-encoded
- Inline CSS and JavaScript
- Opens directly in browser
- Interactive hover effects
- ~500KB-2MB depending on image size

**Visual effects:**
- 60fps animations
- Responsive to mouse movement
- Cinematic lighting and glow
- Cyberpunk/retro aesthetic

## Tips & Best Practices

**Image Selection:**
- **Best:** Portraits, people, distinct objects
- **Good:** Product photos, artwork with clear subjects
- **Avoid:** Landscapes, abstract patterns, busy backgrounds

**Performance:**
- Processing time: 5-15 seconds per image
- Output size: ~1-2MB HTML
- Browser performance: Excellent (canvas-based)

**Artistic Control:**
- Darker source images → more dramatic contrast
- High-contrast subjects → better edge definition
- Clean backgrounds → cleaner dot matrix
- Centered subjects → better visual balance

**Common Issues:**
- **Subject not detected:** Try images with clearer foreground/background separation
- **Too bright:** Source image may need adjustment
- **Choppy animation:** Check browser hardware acceleration

## Related Variants

- **v2 (Gray BG):** Alternative with neutral gray background instead of pixelated blur
- See `skills/ascii-pixel-effect-v2/SKILL.md` for implementation

## References

- Original implementation: March 2026
- Taught by: Sensei
- Inspired by: Classic ASCII art + modern web animations
- Technique: Computer vision + generative art

## License

MIT License - Free to use and modify
