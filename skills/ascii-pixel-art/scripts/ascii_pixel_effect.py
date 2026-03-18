#!/usr/bin/env python3
"""
ASCII Pixel Art Generator
Transforms images into animated ASCII art with subject detection and dynamic effects.
"""

import sys
import base64
from io import BytesIO
from pathlib import Path

try:
    from PIL import Image, ImageFilter, ImageDraw
    import numpy as np
    from rembg import remove
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("\nInstall required packages:")
    print("  pip install pillow rembg numpy")
    sys.exit(1)

# Configuration
TARGET_WIDTH = 900
CELL_W = 11
CELL_H = 14
GRID_STEP = 24
BLUR_RADIUS = 14
BG_DARKEN = 0.65
BG_DESATURATE = 0.5
SUBJECT_THRESHOLD = 0.25
ASCII_RAMP = "@#S08Xox+=;:-,. "
BG_DOT_COLOR = (40, 65, 100)
BG_DOT_OPACITY = 0.3
GRID_OPACITY = 0.05
PIXEL_SIZE = 8  # For pixelation effect


def normalize_color(r, g, b):
    """Preserve hue, maximize brightness"""
    mx = max(r, g, b, 1)
    return int(r / mx * 255), int(g / mx * 255), int(b / mx * 255)


def get_luminance(r, g, b):
    """Calculate perceived luminance"""
    return 0.299 * r + 0.587 * g + 0.114 * b


def char_from_lum(lum, is_subject):
    """Map luminance to ASCII character (inverted for subject)"""
    if not is_subject:
        return '.'
    # Invert: dark = dense char (left), bright = sparse (right)
    idx = int((1.0 - lum) * (len(ASCII_RAMP) - 1))
    idx = max(0, min(len(ASCII_RAMP) - 1, idx))
    return ASCII_RAMP[idx]


def process_image(input_path, output_path=None):
    """
    7-Step pipeline to generate animated ASCII pixel art
    """
    print(f"Processing: {input_path}")
    
    # Step 1: Load and resize
    print("  [1/7] Loading and resizing...")
    img = Image.open(input_path).convert('RGB')
    aspect_ratio = img.height / img.width
    new_height = int(TARGET_WIDTH * aspect_ratio)
    img = img.resize((TARGET_WIDTH, new_height), Image.Resampling.LANCZOS)
    
    # Step 2: Build blurred background
    print("  [2/7] Building blurred background...")
    bg = img.copy()
    bg = bg.filter(ImageFilter.GaussianBlur(radius=BLUR_RADIUS))
    
    # Darken
    bg_array = np.array(bg, dtype=np.float32)
    bg_array *= BG_DARKEN
    
    # Desaturate (blend with grayscale)
    gray = np.dot(bg_array, [0.299, 0.587, 0.114])
    gray = np.stack([gray] * 3, axis=-1)
    bg_array = bg_array * (1 - BG_DESATURATE) + gray * BG_DESATURATE
    
    bg = Image.fromarray(bg_array.astype(np.uint8))
    
    # Pixelate
    small_w = TARGET_WIDTH // PIXEL_SIZE
    small_h = new_height // PIXEL_SIZE
    bg = bg.resize((small_w, small_h), Image.Resampling.BOX)
    bg = bg.resize((TARGET_WIDTH, new_height), Image.Resampling.NEAREST)
    
    # Step 3: Remove background (subject detection)
    print("  [3/7] Detecting subject...")
    mask = remove(img, only_mask=True)
    mask_array = np.array(mask, dtype=np.float32) / 255.0
    
    # Step 4 & 5: Build cell grid and pixel overlay
    print("  [4/7] Building character grid...")
    print("  [5/7] Adding pixel overlay...")
    
    cols = TARGET_WIDTH // CELL_W
    rows = new_height // CELL_H
    
    cells = []
    img_array = np.array(img)
    
    for row in range(rows):
        for col in range(cols):
            y1 = row * CELL_H
            y2 = min((row + 1) * CELL_H, new_height)
            x1 = col * CELL_W
            x2 = min((col + 1) * CELL_W, TARGET_WIDTH)
            
            # Sample cell region
            cell_mask = mask_array[y1:y2, x1:x2]
            cell_rgb = img_array[y1:y2, x1:x2]
            
            # Determine if subject
            is_subject = cell_mask.mean() > SUBJECT_THRESHOLD
            
            # Average RGB
            r = int(cell_rgb[:, :, 0].mean())
            g = int(cell_rgb[:, :, 1].mean())
            b = int(cell_rgb[:, :, 2].mean())
            
            lum = get_luminance(r, g, b) / 255.0
            
            if is_subject:
                char = char_from_lum(lum, True)
                nr, ng, nb = normalize_color(r, g, b)
                color = f"rgb({nr},{ng},{nb})"
            else:
                char = '.'
                color = f"rgb({BG_DOT_COLOR[0]},{BG_DOT_COLOR[1]},{BG_DOT_COLOR[2]})"
            
            # Check if on grid line
            on_grid = (col * CELL_W) % GRID_STEP < CELL_W and (row * CELL_H) % GRID_STEP < CELL_H
            
            cells.append({
                'char': char,
                'color': color,
                'lum': lum,
                'is_subject': is_subject,
                'on_grid': on_grid and is_subject,
                'x': col,
                'y': row
            })
    
    # Step 6: Encode background image
    print("  [6/7] Encoding background...")
    bg_buffer = BytesIO()
    bg.save(bg_buffer, format='PNG')
    bg_base64 = base64.b64encode(bg_buffer.getvalue()).decode('utf-8')
    
    # Step 7: Generate HTML with animations
    print("  [7/7] Generating animated HTML...")
    html = generate_html(bg_base64, cells, cols, rows, TARGET_WIDTH, new_height)
    
    # Write output
    if output_path is None:
        output_path = Path(input_path).stem + '_ascii.html'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✓ Generated: {output_path}")
    print(f"  Dimensions: {cols}×{rows} cells ({TARGET_WIDTH}×{new_height}px)")
    print(f"  Subject cells: {sum(1 for c in cells if c['is_subject'])}/{len(cells)}")


def generate_html(bg_base64, cells, cols, rows, width, height):
    """Generate self-contained HTML with animations"""
    
    cells_json = '[\n'
    for c in cells:
        cells_json += f"  {{char:'{c['char']}',color:'{c['color']}',lum:{c['lum']:.3f},subj:{str(c['is_subject']).lower()},grid:{str(c['on_grid']).lower()},x:{c['x']},y:{c['y']}}},\n"
    cells_json += ']'
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ASCII Pixel Art</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ 
  background: #000; 
  display: flex; 
  justify-content: center; 
  align-items: center; 
  min-height: 100vh;
  overflow: hidden;
}}
.wrap {{ 
  position: relative; 
  width: {width}px; 
  height: {height}px;
}}
.wrap > * {{ 
  position: absolute; 
  top: 0; 
  left: 0; 
  width: 100%; 
  height: 100%;
}}
#bg {{ width: 100%; height: 100%; object-fit: contain; }}
canvas {{ image-rendering: pixelated; }}
</style>
</head>
<body>
<div class="wrap">
  <img id="bg" src="data:image/png;base64,{bg_base64}" alt="background">
  <canvas id="grid" width="{width}" height="{height}"></canvas>
  <canvas id="ascii" width="{width}" height="{height}"></canvas>
</div>
<script>
const CELL_W = {CELL_W};
const CELL_H = {CELL_H};
const COLS = {cols};
const ROWS = {rows};
const BG_DOT_OPACITY = {BG_DOT_OPACITY};
const GRID_OPACITY = {GRID_OPACITY};

const cells = {cells_json};

// Grid canvas (static)
const gridCanvas = document.getElementById('grid');
const gridCtx = gridCanvas.getContext('2d');
gridCtx.strokeStyle = 'rgba(255,255,255,' + GRID_OPACITY + ')';
gridCtx.lineWidth = 1;

cells.forEach(c => {{
  if (c.grid) {{
    gridCtx.strokeRect(c.x * CELL_W, c.y * CELL_H, CELL_W, CELL_H);
  }}
}});

// ASCII canvas (animated)
const asciiCanvas = document.getElementById('ascii');
const ctx = asciiCanvas.getContext('2d');
ctx.font = '14px monospace';
ctx.textAlign = 'left';
ctx.textBaseline = 'top';

let frame = 0;
let mouseX = -1000;
let mouseY = -1000;

// Flicker state
const flickers = cells.map(() => ({{ active: false, duration: 0 }}));

asciiCanvas.addEventListener('mousemove', (e) => {{
  const rect = asciiCanvas.getBoundingClientRect();
  mouseX = (e.clientX - rect.left) * (asciiCanvas.width / rect.width);
  mouseY = (e.clientY - rect.top) * (asciiCanvas.height / rect.height);
}});

function animate() {{
  ctx.clearRect(0, 0, asciiCanvas.width, asciiCanvas.height);
  
  const time = frame * 0.05;
  const shineOffset = (frame * 2) % (COLS + ROWS);
  
  cells.forEach((c, i) => {{
    const cx = c.x * CELL_W + CELL_W / 2;
    const cy = c.y * CELL_H + CELL_H / 2;
    
    // Distance to mouse
    const dx = cx - mouseX;
    const dy = cy - mouseY;
    const dist = Math.sqrt(dx * dx + dy * dy) / CELL_W;
    
    let char = c.char;
    let color = c.color;
    let glow = 0;
    
    if (c.subj) {{
      // Pulse
      const pulse = Math.sin(time + c.x * 0.1 + c.y * 0.1) * 0.5 + 0.5;
      
      // Shine sweep
      const shinePos = c.x + c.y;
      const shineDist = Math.abs(shinePos - shineOffset);
      const shine = Math.max(0, 1 - shineDist / 10) * 0.3;
      
      // Flicker
      if (!flickers[i].active && Math.random() < 0.0025) {{
        flickers[i].active = true;
        flickers[i].duration = 2 + Math.floor(Math.random() * 7);
      }}
      if (flickers[i].active) {{
        flickers[i].duration--;
        if (flickers[i].duration <= 0) flickers[i].active = false;
      }}
      const flicker = flickers[i].active ? 0.3 : 0;
      
      // Hover ripple
      let hover = 0;
      if (dist < 8) {{
        hover = (1 - dist / 8) * 0.5;
        if (dist < 2 && Math.random() < 0.3) {{
          const chars = '@#S08Xox+=;:-,. ';
          char = chars[Math.floor(Math.random() * chars.length)];
        }}
      }}
      
      // Glow based on luminance
      glow = c.lum * (pulse * 0.5 + 0.5) * 8;
      
      // Composite brightness
      const brightness = 1 + pulse * 0.2 + shine + flicker + hover;
      
      // Parse and adjust color
      const match = c.color.match(/rgb\\((\\d+),(\\d+),(\\d+)\\)/);
      if (match) {{
        const r = Math.min(255, Math.floor(parseInt(match[1]) * brightness));
        const g = Math.min(255, Math.floor(parseInt(match[2]) * brightness));
        const b = Math.min(255, Math.floor(parseInt(match[3]) * brightness));
        color = `rgb(${{r}},${{g}},${{b}})`;
      }}
      
      if (hover > 0) {{
        color = color.replace('rgb', 'rgba').replace(')', `,0.8)`);
        const mixCyan = hover;
        color = `rgba(0,255,255,${{mixCyan}})`;
      }}
    }} else {{
      // Background dot
      color = c.color.replace('rgb', 'rgba').replace(')', `,${{BG_DOT_OPACITY}})`);
    }}
    
    // Draw character
    ctx.fillStyle = color;
    if (glow > 0) {{
      ctx.shadowBlur = glow;
      ctx.shadowColor = color;
    }}
    ctx.fillText(char, c.x * CELL_W + 1, c.y * CELL_H);
    if (glow > 0) {{
      ctx.shadowBlur = 0;
    }}
  }});
  
  frame++;
  requestAnimationFrame(animate);
}}

animate();
</script>
</body>
</html>"""


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 ascii_pixel_effect.py <input_image> [output.html]")
        print("\nExample:")
        print("  python3 ascii_pixel_effect.py portrait.jpg")
        print("  python3 ascii_pixel_effect.py photo.png artwork.html")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not Path(input_path).exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)
    
    process_image(input_path, output_path)
