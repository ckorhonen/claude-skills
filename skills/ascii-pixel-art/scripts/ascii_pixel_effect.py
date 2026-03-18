#!/usr/bin/env python3
"""
ASCII Pixel Art Effect
Convert an image into an animated, interactive ASCII art HTML visualization.

Usage: python3 ascii_pixel_effect.py <input_image> [output.html]

Dependencies: pip install Pillow rembg
"""

import sys
import io
import base64
import json
from pathlib import Path

from PIL import Image, ImageFilter
from rembg import remove

# ── Parameters ──────────────────────────────────────────────────────────────

TARGET_WIDTH = 900
CELL_W, CELL_H = 11, 14
GRID_STEP = 24
BLUR_RADIUS = 14
BG_DARKEN = 0.65
BG_DESAT = 0.50
PIXEL_SIZE = 8
SUBJECT_THRESHOLD = 0.25
ASCII_RAMP = "@#S08Xox+=;:-,. "
BG_DOT_COLOR = (40, 65, 100)
BG_DOT_OPACITY = 0.30
GRID_OPACITY = 0.05


def normalize_color(r, g, b):
    """Normalize color to full saturation."""
    mx = max(r, g, b, 1)
    return int(r / mx * 255), int(g / mx * 255), int(b / mx * 255)


def load_and_resize(path):
    """Step 1: Load image and resize to TARGET_WIDTH."""
    img = Image.open(path).convert("RGB")
    ratio = TARGET_WIDTH / img.width
    new_h = int(img.height * ratio)
    return img.resize((TARGET_WIDTH, new_h), Image.LANCZOS)


def build_blurred_bg(img):
    """Step 2: Build blurred, darkened, desaturated, pixelated background."""
    blurred = img.filter(ImageFilter.GaussianBlur(radius=BLUR_RADIUS))

    # Darken
    pixels = blurred.load()
    w, h = blurred.size
    for y in range(h):
        for x in range(w):
            r, g, b = pixels[x, y]
            pixels[x, y] = (
                int(r * BG_DARKEN),
                int(g * BG_DARKEN),
                int(b * BG_DARKEN),
            )

    # Desaturate 50%
    grey = blurred.convert("L").convert("RGB")
    blurred = Image.blend(blurred, grey, BG_DESAT)

    # Pixelate
    small = blurred.resize(
        (w // PIXEL_SIZE, h // PIXEL_SIZE), Image.BOX
    )
    pixelated = small.resize((w, h), Image.NEAREST)
    return pixelated


def get_subject_mask(img):
    """Step 3: Remove background using rembg to get alpha mask."""
    result = remove(img, only_mask=True)
    if result.mode != "L":
        result = result.convert("L")
    return result


def build_cell_grid(img, mask):
    """Step 5: Build grid of cells with ASCII chars, colors, and subject flag."""
    w, h = img.size
    cols = w // CELL_W
    rows = h // CELL_H
    img_pixels = img.load()
    mask_pixels = mask.load()

    cells = []
    for row in range(rows):
        row_cells = []
        for col in range(cols):
            # Sample region
            x0, y0 = col * CELL_W, row * CELL_H
            x1, y1 = min(x0 + CELL_W, w), min(y0 + CELL_H, h)

            r_sum, g_sum, b_sum, m_sum = 0, 0, 0, 0
            count = 0
            for py in range(y0, y1):
                for px in range(x0, x1):
                    pr, pg, pb = img_pixels[px, py]
                    r_sum += pr
                    g_sum += pg
                    b_sum += pb
                    m_sum += mask_pixels[px, py]
                    count += 1

            if count == 0:
                count = 1

            avg_r = r_sum // count
            avg_g = g_sum // count
            avg_b = b_sum // count
            avg_mask = m_sum / count / 255.0
            lum = (0.299 * avg_r + 0.587 * avg_g + 0.114 * avg_b) / 255.0

            is_subject = avg_mask > SUBJECT_THRESHOLD

            if is_subject:
                # Inverted luminance: dark area = dense char
                idx = int((1.0 - lum) * (len(ASCII_RAMP) - 1))
                idx = max(0, min(idx, len(ASCII_RAMP) - 1))
                char = ASCII_RAMP[idx]
                nr, ng, nb = normalize_color(avg_r, avg_g, avg_b)
                row_cells.append({
                    "char": char,
                    "r": nr, "g": ng, "b": nb,
                    "lum": round(lum, 3),
                    "subject": True,
                })
            else:
                row_cells.append({
                    "char": ".",
                    "r": BG_DOT_COLOR[0],
                    "g": BG_DOT_COLOR[1],
                    "b": BG_DOT_COLOR[2],
                    "lum": round(lum, 3),
                    "subject": False,
                })
        cells.append(row_cells)

    return cells, cols, rows


def image_to_data_uri(img, fmt="JPEG", quality=85):
    """Convert PIL image to base64 data URI."""
    buf = io.BytesIO()
    img.save(buf, format=fmt, quality=quality)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    mime = "image/jpeg" if fmt == "JPEG" else "image/png"
    return f"data:{mime};base64,{b64}"


def generate_html(bg_data_uri, cells, cols, rows, width, height):
    """Steps 4, 6, 7: Generate the self-contained HTML with all layers and animation."""
    cells_json = json.dumps(cells)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ASCII Pixel Art</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ background: #000; display: flex; justify-content: center; align-items: center; min-height: 100vh; overflow: hidden; }}
.wrap {{ position: relative; width: {width}px; height: {height}px; }}
.wrap img, .wrap canvas {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; }}
</style>
</head>
<body>
<div class="wrap">
  <img src="{bg_data_uri}" alt="background">
  <canvas id="grid" width="{width}" height="{height}"></canvas>
  <canvas id="ascii" width="{width}" height="{height}"></canvas>
</div>
<script>
(function() {{
  const CELL_W = {CELL_W}, CELL_H = {CELL_H};
  const COLS = {cols}, ROWS = {rows};
  const GRID_STEP = {GRID_STEP};
  const GRID_OPACITY = {GRID_OPACITY};
  const BG_DOT_OPACITY = {BG_DOT_OPACITY};
  const ASCII_RAMP = {json.dumps(ASCII_RAMP)};
  const cells = {cells_json};

  // ── Step 4: Pixel grid overlay ──
  const gridCtx = document.getElementById('grid').getContext('2d');
  gridCtx.fillStyle = 'rgba(255,255,255,' + GRID_OPACITY + ')';
  for (let row = 0; row < ROWS; row++) {{
    for (let col = 0; col < COLS; col++) {{
      if (!cells[row][col].subject) continue;
      const x = col * CELL_W, y = row * CELL_H;
      if (x % GRID_STEP === 0 || y % GRID_STEP === 0) {{
        gridCtx.fillRect(x, y, CELL_W, CELL_H);
      }}
    }}
  }}

  // ── Step 7: Animation ──
  const asciiCanvas = document.getElementById('ascii');
  const ctx = asciiCanvas.getContext('2d');
  ctx.font = CELL_H + 'px monospace';
  ctx.textBaseline = 'top';

  let frame = 0;
  let mouseCol = -100, mouseRow = -100;
  const flickerMap = new Map();

  asciiCanvas.addEventListener('mousemove', function(e) {{
    const rect = asciiCanvas.getBoundingClientRect();
    const scaleX = asciiCanvas.width / rect.width;
    const scaleY = asciiCanvas.height / rect.height;
    mouseCol = Math.floor((e.clientX - rect.left) * scaleX / CELL_W);
    mouseRow = Math.floor((e.clientY - rect.top) * scaleY / CELL_H);
  }});

  asciiCanvas.addEventListener('mouseleave', function() {{
    mouseCol = -100; mouseRow = -100;
  }});

  function animate() {{
    ctx.clearRect(0, 0, asciiCanvas.width, asciiCanvas.height);
    const time = frame * 0.05;

    for (let row = 0; row < ROWS; row++) {{
      for (let col = 0; col < COLS; col++) {{
        const cell = cells[row][col];
        const x = col * CELL_W, y = row * CELL_H;
        let ch = cell.char;
        let r = cell.r, g = cell.g, b = cell.b;
        let alpha = cell.subject ? 1.0 : BG_DOT_OPACITY;
        let glow = 0;

        if (cell.subject) {{
          // Sine pulse on bright cells
          const pulse = 0.85 + 0.15 * Math.sin(time + col * 0.3 + row * 0.2);
          if (cell.lum > 0.5) {{
            alpha *= pulse;
          }}

          // Shine sweep (diagonal)
          const sweepPos = ((time * 2) % (COLS + ROWS + 20)) - 10;
          const cellDiag = col + row;
          const sweepDist = Math.abs(cellDiag - sweepPos);
          if (sweepDist < 5) {{
            const sweepIntensity = 1 - sweepDist / 5;
            r = Math.min(255, r + Math.floor(60 * sweepIntensity));
            g = Math.min(255, g + Math.floor(60 * sweepIntensity));
            b = Math.min(255, b + Math.floor(60 * sweepIntensity));
          }}

          // Glow on high-lum cells
          if (cell.lum > 0.6) {{
            glow = cell.lum * pulse * 8;
          }}

          // Random flicker
          const key = row * COLS + col;
          if (flickerMap.has(key)) {{
            const f = flickerMap.get(key);
            if (frame < f.end) {{
              ch = ASCII_RAMP[Math.floor(Math.random() * ASCII_RAMP.length)];
            }} else {{
              flickerMap.delete(key);
            }}
          }} else if (Math.random() < 0.0025) {{
            flickerMap.set(key, {{ end: frame + 2 + Math.floor(Math.random() * 7) }});
          }}

          // Hover ripple
          const dx = col - mouseCol, dy = row - mouseRow;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 8) {{
            const ripple = 1 - dist / 8;
            r = Math.min(255, Math.floor(r * (1 - ripple) + 0 * ripple));
            g = Math.min(255, Math.floor(g * (1 - ripple) + 255 * ripple));
            b = Math.min(255, Math.floor(b * (1 - ripple) + 255 * ripple));
            if (dist < 2) {{
              ch = ASCII_RAMP[Math.floor(Math.random() * ASCII_RAMP.length)];
            }}
          }}
        }}

        // Draw
        if (glow > 0) {{
          ctx.shadowBlur = glow;
          ctx.shadowColor = 'rgba(' + r + ',' + g + ',' + b + ',0.6)';
        }} else {{
          ctx.shadowBlur = 0;
        }}

        ctx.fillStyle = 'rgba(' + r + ',' + g + ',' + b + ',' + alpha + ')';
        ctx.fillText(ch, x, y);
      }}
    }}

    frame++;
    requestAnimationFrame(animate);
  }}

  animate();
}})();
</script>
</body>
</html>"""


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 ascii_pixel_effect.py <image> [output.html]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "ascii_art.html"

    print(f"Loading {input_path}...")
    img = load_and_resize(input_path)
    w, h = img.size
    print(f"  Resized to {w}x{h}")

    print("Building blurred background...")
    bg = build_blurred_bg(img)

    print("Removing background (rembg)...")
    mask = get_subject_mask(img)

    print("Building cell grid...")
    cells, cols, rows = build_cell_grid(img, mask)
    print(f"  Grid: {cols}x{rows} cells")

    print("Encoding background...")
    bg_uri = image_to_data_uri(bg)

    print("Generating HTML...")
    html = generate_html(bg_uri, cells, cols, rows, w, h)

    Path(output_path).write_text(html)
    print(f"Done! Output: {output_path}")
    print(f"  File size: {len(html) / 1024:.0f} KB")


if __name__ == "__main__":
    main()
