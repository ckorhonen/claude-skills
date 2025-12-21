# Color Palettes for Retro/Cyberpunk TUI

Complete color specifications for terminal and cyberpunk aesthetics.

## Phosphor Green (Classic Terminal)

The iconic green-on-black of early computer terminals.

| Role | Hex | RGB | HSL | Usage |
|------|-----|-----|-----|-------|
| Bright | `#00ff00` | 0, 255, 0 | 120, 100%, 50% | Primary text, highlights |
| Medium | `#00cc00` | 0, 204, 0 | 120, 100%, 40% | Secondary text |
| Dim | `#009900` | 0, 153, 0 | 120, 100%, 30% | Tertiary, inactive |
| Muted | `#006600` | 0, 102, 0 | 120, 100%, 20% | Borders, separators |
| Background | `#001100` | 0, 17, 0 | 120, 100%, 3% | Main background |
| Deep BG | `#000800` | 0, 8, 0 | 120, 100%, 2% | Panel backgrounds |

### CSS Variables
```css
:root {
  --phosphor-bright: #00ff00;
  --phosphor-medium: #00cc00;
  --phosphor-dim: #009900;
  --phosphor-muted: #006600;
  --phosphor-bg: #001100;
  --phosphor-bg-deep: #000800;
}
```

### SwiftUI Colors
```swift
extension Color {
    static let phosphorBright = Color(red: 0, green: 1, blue: 0)
    static let phosphorMedium = Color(red: 0, green: 0.8, blue: 0)
    static let phosphorDim = Color(red: 0, green: 0.6, blue: 0)
    static let phosphorMuted = Color(red: 0, green: 0.4, blue: 0)
    static let phosphorBg = Color(red: 0, green: 0.067, blue: 0)
    static let phosphorBgDeep = Color(red: 0, green: 0.031, blue: 0)
}
```

### Tailwind Config
```js
colors: {
  phosphor: {
    bright: '#00ff00',
    medium: '#00cc00',
    dim: '#009900',
    muted: '#006600',
    bg: '#001100',
    'bg-deep': '#000800',
  }
}
```

---

## Cyberpunk Neon

High-contrast neon colors on dark backgrounds for cyberpunk aesthetics.

| Role | Hex | RGB | HSL | Usage |
|------|-----|-----|-----|-------|
| Cyan | `#00ffff` | 0, 255, 255 | 180, 100%, 50% | Primary accent |
| Magenta | `#ff00ff` | 255, 0, 255 | 300, 100%, 50% | Secondary accent |
| Electric Blue | `#0066ff` | 0, 102, 255 | 216, 100%, 50% | Tertiary accent |
| Hot Pink | `#ff1493` | 255, 20, 147 | 328, 100%, 54% | Warnings, CTAs |
| Neon Yellow | `#ffff00` | 255, 255, 0 | 60, 100%, 50% | Highlights |
| Background | `#0a0a1a` | 10, 10, 26 | 240, 44%, 7% | Main background |
| Deep BG | `#050510` | 5, 5, 16 | 240, 52%, 4% | Panel backgrounds |
| Surface | `#12121f` | 18, 18, 31 | 240, 27%, 10% | Cards, dialogs |

### CSS Variables
```css
:root {
  --cyber-cyan: #00ffff;
  --cyber-magenta: #ff00ff;
  --cyber-blue: #0066ff;
  --cyber-pink: #ff1493;
  --cyber-yellow: #ffff00;
  --cyber-bg: #0a0a1a;
  --cyber-bg-deep: #050510;
  --cyber-surface: #12121f;
}
```

### SwiftUI Colors
```swift
extension Color {
    static let cyberCyan = Color(red: 0, green: 1, blue: 1)
    static let cyberMagenta = Color(red: 1, green: 0, blue: 1)
    static let cyberBlue = Color(red: 0, green: 0.4, blue: 1)
    static let cyberPink = Color(red: 1, green: 0.078, blue: 0.576)
    static let cyberYellow = Color(red: 1, green: 1, blue: 0)
    static let cyberBg = Color(red: 0.039, green: 0.039, blue: 0.102)
    static let cyberSurface = Color(red: 0.071, green: 0.071, blue: 0.122)
}
```

---

## Amber CRT

Warm amber tones from early monochrome displays.

| Role | Hex | RGB | HSL | Usage |
|------|-----|-----|-----|-------|
| Bright | `#ffb000` | 255, 176, 0 | 41, 100%, 50% | Primary text |
| Medium | `#cc8c00` | 204, 140, 0 | 41, 100%, 40% | Secondary text |
| Dim | `#996800` | 153, 104, 0 | 41, 100%, 30% | Tertiary |
| Muted | `#664400` | 102, 68, 0 | 40, 100%, 20% | Borders |
| Background | `#1a1000` | 26, 16, 0 | 37, 100%, 5% | Main background |
| Deep BG | `#0d0800` | 13, 8, 0 | 37, 100%, 3% | Panel backgrounds |

### CSS Variables
```css
:root {
  --amber-bright: #ffb000;
  --amber-medium: #cc8c00;
  --amber-dim: #996800;
  --amber-muted: #664400;
  --amber-bg: #1a1000;
  --amber-bg-deep: #0d0800;
}
```

### SwiftUI Colors
```swift
extension Color {
    static let amberBright = Color(red: 1, green: 0.69, blue: 0)
    static let amberMedium = Color(red: 0.8, green: 0.55, blue: 0)
    static let amberDim = Color(red: 0.6, green: 0.41, blue: 0)
    static let amberBg = Color(red: 0.102, green: 0.063, blue: 0)
}
```

---

## Synthwave / Retrowave

Purple and pink gradients inspired by 1980s aesthetics.

| Role | Hex | RGB | HSL | Usage |
|------|-----|-----|-----|-------|
| Purple | `#9d4edd` | 157, 78, 221 | 273, 69%, 59% | Primary |
| Pink | `#f72585` | 247, 37, 133 | 333, 93%, 56% | Secondary |
| Blue | `#4cc9f0` | 76, 201, 240 | 194, 83%, 62% | Accent |
| Orange | `#ff6f00` | 255, 111, 0 | 26, 100%, 50% | Highlight |
| Background | `#10002b` | 16, 0, 43 | 262, 100%, 8% | Main |
| Surface | `#240046` | 36, 0, 70 | 271, 100%, 14% | Cards |

### CSS Variables
```css
:root {
  --synth-purple: #9d4edd;
  --synth-pink: #f72585;
  --synth-blue: #4cc9f0;
  --synth-orange: #ff6f00;
  --synth-bg: #10002b;
  --synth-surface: #240046;
}
```

---

## Matrix Green

Variations of the iconic Matrix green rain effect.

| Role | Hex | RGB | Usage |
|------|-----|-----|-------|
| Bright | `#00ff41` | 0, 255, 65 | Active characters |
| Medium | `#00cc33` | 0, 204, 51 | Recent characters |
| Dim | `#008f11` | 0, 143, 17 | Older characters |
| Fade | `#003b00` | 0, 59, 0 | Fading trails |
| Background | `#0d0208` | 13, 2, 8 | Screen background |

### CSS Variables
```css
:root {
  --matrix-bright: #00ff41;
  --matrix-medium: #00cc33;
  --matrix-dim: #008f11;
  --matrix-fade: #003b00;
  --matrix-bg: #0d0208;
}
```

---

## Tuimorphic Tints

The 7 built-in color tints for Tuimorphic components.

| Tint | Primary | Accent | Apply via |
|------|---------|--------|-----------|
| Green | `#00ff00` | `#00cc00` | `class="tint-green"` |
| Blue | `#0088ff` | `#0066cc` | `class="tint-blue"` |
| Red | `#ff4444` | `#cc3333` | `class="tint-red"` |
| Yellow | `#ffcc00` | `#cc9900` | `class="tint-yellow"` |
| Purple | `#aa44ff` | `#8833cc` | `class="tint-purple"` |
| Orange | `#ff8800` | `#cc6600` | `class="tint-orange"` |
| Pink | `#ff44aa` | `#cc3388` | `class="tint-pink"` |

---

## Glow Color Formulas

For neon glow effects, use these color progressions:

### Cyan Glow
```css
text-shadow:
  0 0 5px #ffffff,   /* White core */
  0 0 10px #ffffff,
  0 0 20px #00ffff,  /* Color starts */
  0 0 40px #00ffff,
  0 0 80px #00ffff;
```

### Multi-Color Glow (Cyberpunk)
```css
text-shadow:
  0 0 5px #ffffff,
  0 0 10px #ff00ff,  /* Magenta inner */
  0 0 20px #ff00ff,
  0 0 40px #00ffff,  /* Cyan outer */
  0 0 80px #00ffff;
```

---

## Accessibility Notes

- Ensure minimum 4.5:1 contrast ratio for text
- Phosphor green on #001100: ~17:1 ratio (excellent)
- Cyberpunk cyan on #0a0a1a: ~15:1 ratio (excellent)
- Amber on #1a1000: ~12:1 ratio (good)
- Test with color blindness simulators for key UI elements
