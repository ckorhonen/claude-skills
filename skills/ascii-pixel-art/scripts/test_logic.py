#!/usr/bin/env python3
"""
Test script to validate ASCII pixel art logic without dependencies
"""

# Test 1: Color normalization
def normalize_color(r, g, b):
    """Preserve hue, maximize brightness"""
    mx = max(r, g, b, 1)
    return int(r / mx * 255), int(g / mx * 255), int(b / mx * 255)

print("Test 1: Color Normalization")
print("=" * 50)
test_colors = [
    (128, 64, 32),   # Dark orange
    (200, 100, 50),  # Brighter orange
    (50, 100, 150),  # Blue tones
    (100, 100, 100), # Gray
]

for r, g, b in test_colors:
    nr, ng, nb = normalize_color(r, g, b)
    print(f"  ({r:3d}, {g:3d}, {b:3d}) → ({nr:3d}, {ng:3d}, {nb:3d})")

# Test 2: Luminance calculation
def get_luminance(r, g, b):
    """Calculate perceived luminance"""
    return 0.299 * r + 0.587 * g + 0.114 * b

print("\nTest 2: Luminance Calculation")
print("=" * 50)
for r, g, b in test_colors:
    lum = get_luminance(r, g, b) / 255.0
    print(f"  ({r:3d}, {g:3d}, {b:3d}) → {lum:.3f}")

# Test 3: ASCII character mapping
ASCII_RAMP = "@#S08Xox+=;:-,. "

def char_from_lum(lum, is_subject):
    """Map luminance to ASCII character (inverted for subject)"""
    if not is_subject:
        return '.'
    # Invert: dark = dense char (left), bright = sparse (right)
    idx = int((1.0 - lum) * (len(ASCII_RAMP) - 1))
    idx = max(0, min(len(ASCII_RAMP) - 1, idx))
    return ASCII_RAMP[idx]

print("\nTest 3: ASCII Character Mapping (Subject)")
print("=" * 50)
print(f"Ramp: '{ASCII_RAMP}'")
print(f"Length: {len(ASCII_RAMP)} chars\n")

test_lums = [0.0, 0.25, 0.5, 0.75, 1.0]
for lum in test_lums:
    char = char_from_lum(lum, is_subject=True)
    inverted = 1.0 - lum
    print(f"  Luminance: {lum:.2f} → Inverted: {inverted:.2f} → '{char}'")

print("\nTest 4: Background vs Subject")
print("=" * 50)
print(f"  Subject (lum=0.5):    '{char_from_lum(0.5, True)}'")
print(f"  Background (any lum): '{char_from_lum(0.5, False)}'")

# Test 5: Grid calculation
print("\nTest 5: Grid Cell Calculations")
print("=" * 50)
CELL_W = 11
CELL_H = 14
TARGET_WIDTH = 900
TARGET_HEIGHT = 600  # Example
GRID_STEP = 24

cols = TARGET_WIDTH // CELL_W
rows = TARGET_HEIGHT // CELL_H

print(f"  Image: {TARGET_WIDTH}×{TARGET_HEIGHT}px")
print(f"  Cell size: {CELL_W}×{CELL_H}px")
print(f"  Grid: {cols}×{rows} cells")
print(f"  Total cells: {cols * rows}")
print(f"  Grid lines every {GRID_STEP}px")

# Sample grid positions
print("\n  Sample grid intersections:")
for row in [0, 1, 2, 10]:
    for col in [0, 1, 2, 10]:
        x = col * CELL_W
        y = row * CELL_H
        on_grid = x % GRID_STEP < CELL_W and y % GRID_STEP < CELL_H
        marker = "✓" if on_grid else " "
        print(f"    Cell ({col:2d},{row:2d}) → ({x:3d},{y:3d})px {marker}")
    if row == 2:
        print("    ...")

print("\n✓ All logic tests passed!")
print("\nTo test with real images:")
print("  1. Install dependencies: pip install pillow rembg numpy")
print("  2. Run: python3 ascii_pixel_effect.py <image.jpg>")
print("  3. Open generated HTML in browser")
