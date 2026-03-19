---
name: tui-designer
description: Design and implement retro/cyberpunk/hacker-style terminal UIs. Covers React (Tuimorphic), SwiftUI (Metal shaders), and CSS approaches. Use when creating terminal aesthetics, CRT effects, neon glow, scanlines, phosphor green displays, or retro-futuristic interfaces.
---

# TUI Designer - Retro/Cyberpunk Terminal UI Expert

Expert guidance for designing and implementing text-based user interfaces with authentic retro computing aesthetics: CRT monitors, phosphor glow, scanlines, and cyberpunk neon.

## When to Use This Skill

Use this skill when:
- Creating terminal-style or hacker aesthetic UIs
- Implementing CRT monitor effects (scanlines, glow, barrel distortion)
- Building cyberpunk/synthwave/retrowave interfaces
- Using Tuimorphic components in React
- Implementing Metal shaders for retro effects in SwiftUI
- Designing neon glow text and UI elements
- Choosing color palettes for retro computing aesthetics
- Working with monospace fonts and box-drawing characters

## Design Principles

### The Retro/Cyberpunk Aesthetic

This aesthetic draws from:
- **CRT monitors**: Phosphor glow, scanlines, screen curvature, flicker
- **Terminal interfaces**: Monospace fonts, box-drawing characters, green/amber text
- **Cyberpunk fiction**: Neon colors, dark backgrounds, high contrast
- **1980s computing**: ASCII art, limited color palettes, blocky graphics

### Visual Elements Checklist

- [ ] Dark background (near-black with subtle color tint)
- [ ] Monospace typography throughout
- [ ] Box-drawing characters for borders and frames
- [ ] Neon glow on text and/or borders
- [ ] Scanline effect (subtle horizontal lines)
- [ ] Limited color palette (1-3 accent colors)
- [ ] High contrast between text and background
- [ ] Optional: CRT curvature, chromatic aberration, flicker

## Quick Reference: Color Palettes

### Phosphor Green (Classic Terminal)
| Role | Hex | Usage |
|------|-----|-------|
| Bright | `#00ff00` | Primary text, highlights |
| Medium | `#00cc00` | Secondary text |
| Dark | `#009900` | Dimmed elements |
| Background | `#001100` | Main background |
| Deep BG | `#000800` | Panel backgrounds |

### Cyberpunk Neon
| Role | Hex | Usage |
|------|-----|-------|
| Cyan | `#00ffff` | Primary accent |
| Magenta | `#ff00ff` | Secondary accent |
| Electric Blue | `#0066ff` | Tertiary |
| Hot Pink | `#ff1493` | Warnings |
| Background | `#0a0a1a` | Main background |

### Amber CRT
| Role | Hex | Usage |
|------|-----|-------|
| Bright | `#ffb000` | Primary text |
| Medium | `#cc8800` | Secondary |
| Dark | `#996600` | Dimmed |
| Background | `#1a1000` | Main background |

See [color-palettes.md](references/color-palettes.md) for complete specifications.

## Typography

### Recommended Fonts

**Web:**
```css
font-family: 'GNU Unifont', 'IBM Plex Mono', 'JetBrains Mono',
             'SF Mono', 'Consolas', monospace;
```

**SwiftUI:**
```swift
.font(.system(size: 14, weight: .regular, design: .monospaced))
```

### Box-Drawing Characters

```
Light:   ─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼
Heavy:   ━ ┃ ┏ ┓ ┗ ┛ ┣ ┫ ┳ ┻ ╋
Double:  ═ ║ ╔ ╗ ╚ ╝ ╠ ╣ ╦ ╩ ╬
Rounded: ╭ ╮ ╰ ╯
```

See [typography-guide.md](references/typography-guide.md) for complete reference.

## Copywriting

Terminal interfaces have a distinct voice: terse, technical, authoritative. Use these defaults unless the project specifies otherwise.

### Core Principles

1. **Terse and Direct** - Every word earns its place
2. **Technical Authority** - The system knows what it's doing
3. **Mechanical Precision** - No hedging, apologies, or filler

### Text Formatting

| Element | Case | Example |
|---------|------|---------|
| Headers/Titles | UPPERCASE | `SYSTEM STATUS` |
| Labels | UPPERCASE | `CPU USAGE:` |
| Status indicators | UPPERCASE | `ONLINE`, `OFFLINE` |
| Commands/Input | lowercase | `> run diagnostic` |
| Body text | Sentence case | `Connection established` |

### Message Prefixes

```
[SYS] System message       [ERR] Error
[USR] User action          [WRN] Warning
[INF] Information          [NET] Network
```

### Vocabulary Quick Reference

| Action | Terminal Verbs |
|--------|---------------|
| Start | INITIALIZE, BOOT, LAUNCH, ACTIVATE |
| Stop | TERMINATE, HALT, ABORT, KILL |
| Save | WRITE, COMMIT, STORE, PERSIST |
| Load | READ, FETCH, RETRIEVE, LOAD |
| Delete | PURGE, REMOVE, CLEAR, WIPE |

| State | Terminal Words |
|-------|---------------|
| Working | PROCESSING, EXECUTING, RUNNING |
| Done | COMPLETE, SUCCESS, FINISHED |
| Failed | ERROR, FAULT, ABORTED |
| Ready | ONLINE, AVAILABLE, ARMED |

### Common Patterns

```
> INITIALIZING SYSTEM...
> LOADING MODULES [████████░░] 80%
> AUTHENTICATION COMPLETE
> SYSTEM READY

ERROR: ACCESS DENIED
ERR_CONNECTION_REFUSED: Timeout after 30s
WARNING: Low disk space (< 10%)

CONFIRM DELETE? [Y/N]
SELECT OPTION [1-5]:
```

### Avoid

- "Please", "Sorry", "Oops"
- "Just", "Maybe", "Might"
- Excessive exclamation points
- Emoji (unless specifically requested)

See [copywriting-guide.md](references/copywriting-guide.md) for complete voice and tone reference.

---

## Platform: React with Tuimorphic

[Tuimorphic](https://github.com/douglance/tuimorphic) is a React component library providing 37 terminal-styled, accessible UI components.

### Quick Start

```bash
npm install tuimorphic
```

```tsx
import { Button, Card, Input } from 'tuimorphic';
import 'tuimorphic/styles.css';

function App() {
  return (
    <div className="theme-dark tint-green">
      <Card>
        <h1>SYSTEM ACCESS</h1>
        <Input placeholder="Enter command..." />
        <Button variant="primary">EXECUTE</Button>
      </Card>
    </div>
  );
}
```

### Theme Configuration

Apply themes via CSS classes on a parent element:

```jsx
// Dark mode with green tint
<div className="theme-dark tint-green">

// Light mode with cyan tint
<div className="theme-light tint-blue">
```

**Available tints:** `tint-green`, `tint-blue`, `tint-red`, `tint-yellow`, `tint-purple`, `tint-orange`, `tint-pink`

### Key Components

| Component | Usage |
|-----------|-------|
| `Button` | Actions with `variant="primary\|secondary\|ghost"` |
| `Input` | Text input with terminal styling |
| `Card` | Container with box-drawing borders |
| `Dialog` | Modal dialogs |
| `Menu` | Dropdown menus |
| `CodeBlock` | Syntax-highlighted code |
| `Table` | Data tables |
| `Tabs` | Tabbed navigation |
| `TreeView` | File tree display |

See [tuimorphic-reference.md](references/tuimorphic-reference.md) for complete API.

### Adding Neon Glow

Enhance Tuimorphic with CSS glow effects:

```css
/* Neon text glow */
.neon-text {
  color: #0ff;
  text-shadow:
    0 0 5px #fff,
    0 0 10px #fff,
    0 0 20px #0ff,
    0 0 40px #0ff,
    0 0 80px #0ff;
}

/* Neon border glow */
.neon-border {
  border-color: #0ff;
  box-shadow:
    0 0 5px #0ff,
    0 0 10px #0ff,
    inset 0 0 5px #0ff;
}

/* Flickering animation */
@keyframes flicker {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.95; }
  52% { opacity: 1; }
  54% { opacity: 0.9; }
}

.flicker {
  animation: flicker 3s infinite;
}
```

---

## Platform: SwiftUI with Metal Shaders

iOS 17+ supports Metal shaders directly in SwiftUI via `.colorEffect()`, `.distortionEffect()`, and `.layerEffect()`.

### CRT Effect Implementation

**CRT.metal:**
```metal
#include <metal_stdlib>
#include <SwiftUI/SwiftUI.h>
using namespace metal;

[[stitchable]] half4 crtEffect(
    float2 position,
    SwiftUI::Layer layer,
    float time,
    float2 size,
    float scanlineIntensity,
    float distortionStrength
) {
    float2 uv = position / size;

    // Barrel distortion
    float2 center = uv - 0.5;
    float dist = length(center);
    float2 distorted = center * (1.0 + distortionStrength * dist * dist);
    float2 samplePos = (distorted + 0.5) * size;

    // Bounds check
    if (samplePos.x < 0 || samplePos.x > size.x ||
        samplePos.y < 0 || samplePos.y > size.y) {
        return half4(0, 0, 0, 1);
    }

    // Sample color
    half4 color = layer.sample(samplePos);

    // Scanlines
    float scanline = sin(position.y * 3.14159 * 2.0) * scanlineIntensity;
    color.rgb *= 1.0 - scanline;

    // Subtle color shift (chromatic aberration)
    color.r *= 1.0 + 0.02 * sin(time * 2.0);
    color.b *= 1.0 - 0.02 * sin(time * 2.0);

    // Slight flicker
    color.rgb *= 1.0 + 0.01 * sin(time * 60.0);

    return color;
}
```

**SwiftUI View Modifier:**
```swift
struct CRTEffectModifier: ViewModifier {
    @State private var startTime = Date()
    var scanlineIntensity: Float = 0.1
    var distortionStrength: Float = 0.1

    func body(content: Content) -> some View {
        TimelineView(.animation) { timeline in
            let time = Float(timeline.date.timeIntervalSince(startTime))
            GeometryReader { geo in
                content
                    .layerEffect(
                        ShaderLibrary.crtEffect(
                            .float(time),
                            .float2(geo.size),
                            .float(scanlineIntensity),
                            .float(distortionStrength)
                        ),
                        maxSampleOffset: .init(width: 10, height: 10)
                    )
            }
        }
    }
}

extension View {
    func crtEffect(
        scanlines: Float = 0.1,
        distortion: Float = 0.1
    ) -> some View {
        modifier(CRTEffectModifier(
            scanlineIntensity: scanlines,
            distortionStrength: distortion
        ))
    }
}
```

**Usage:**
```swift
Text("SYSTEM ONLINE")
    .font(.system(size: 24, weight: .bold, design: .monospaced))
    .foregroundColor(.green)
    .crtEffect(scanlines: 0.15, distortion: 0.08)
```

### Neon Glow in SwiftUI

```swift
extension View {
    func neonGlow(color: Color, radius: CGFloat = 10) -> some View {
        self
            .shadow(color: color.opacity(0.8), radius: radius / 4)
            .shadow(color: color.opacity(0.6), radius: radius / 2)
            .shadow(color: color.opacity(0.4), radius: radius)
            .shadow(color: color.opacity(0.2), radius: radius * 2)
    }
}

// Usage
Text("NEON")
    .font(.system(size: 48, design: .monospaced))
    .foregroundColor(.cyan)
    .neonGlow(color: .cyan, radius: 15)
```

See [metal-shaders-ios.md](references/metal-shaders-ios.md) for complete shader code.

---

## Platform: CSS/Vanilla Web

### Scanlines Overlay

```css
.crt-container {
    position: relative;
    background: #000800;
}

.crt-container::after {
    content: '';
    position: absolute;
    inset: 0;
    background: repeating-linear-gradient(
        0deg,
        rgba(0, 0, 0, 0.15),
        rgba(0, 0, 0, 0.15) 1px,
        transparent 1px,
        transparent 2px
    );
    pointer-events: none;
}
```

### Neon Text Effect

```css
.neon-text {
    color: #0ff;
    text-shadow:
        /* White core */
        0 0 5px #fff,
        0 0 10px #fff,
        /* Colored glow layers */
        0 0 20px #0ff,
        0 0 30px #0ff,
        0 0 40px #0ff,
        0 0 55px #0ff,
        0 0 75px #0ff;
}
```

### CRT Curvature (CSS Transform)

```css
.crt-screen {
    border-radius: 20px;
    transform: perspective(1000px) rotateX(2deg);
    box-shadow:
        inset 0 0 50px rgba(0, 255, 0, 0.1),
        0 0 20px rgba(0, 255, 0, 0.2);
}
```

### WebGL CRT with CRTFilter.js

```html
<script type="module">
import { CRTFilterWebGL } from 'crtfilter';

const canvas = document.getElementById('crt-canvas');
const crt = new CRTFilterWebGL(canvas, {
    scanlineIntensity: 0.15,
    glowBloom: 0.3,
    chromaticAberration: 0.002,
    barrelDistortion: 0.1,
    staticNoise: 0.03,
    flicker: true,
    retraceLines: true
});

crt.start();
</script>
```

See [crt-effects-web.md](references/crt-effects-web.md) for complete techniques.

---

## Effect Patterns

### Scanlines

| Platform | Implementation |
|----------|---------------|
| CSS | `repeating-linear-gradient` pseudo-element |
| SwiftUI | Metal shader with `sin(position.y * frequency)` |
| WebGL | Fragment shader brightness modulation |

### Bloom/Glow

| Platform | Implementation |
|----------|---------------|
| CSS | Multiple `text-shadow` with increasing blur |
| SwiftUI | Multiple `.shadow()` modifiers |
| WebGL | Gaussian blur pass + additive blend |
| Three.js | `UnrealBloomPass` with `luminanceThreshold` |

### Chromatic Aberration

| Platform | Implementation |
|----------|---------------|
| CSS | Three overlapping elements with color channel offset |
| SwiftUI | Sample texture at offset positions per RGB channel |
| WebGL | Sample UV with slight offset per channel |

### Flicker

| Platform | Implementation |
|----------|---------------|
| CSS | `@keyframes` animation varying opacity 0.9-1.0 |
| SwiftUI | Timer-driven opacity or shader time-based |
| WebGL | Time-based noise multiplier |

---

## Performance Considerations

### CSS Effects
- `box-shadow` and `text-shadow` are GPU-accelerated but expensive with many layers
- Limit to 4-5 shadow layers for glow effects
- Use `will-change: transform` for animated elements
- Consider `prefers-reduced-motion` media query

### SwiftUI/Metal
- Metal shaders run at 60-120fps on all devices supporting iOS 17+
- `.layerEffect()` processes every pixel - keep shaders simple
- Pre-compile shaders with `.compile()` (iOS 18+)
- Test on older devices (A12 minimum for iOS 17)

### WebGL
- CRTFilter.js uses hardware acceleration, minimal performance impact
- Bloom effects in Three.js require render-to-texture passes
- Consider lower resolution render targets for mobile

### General
- Reduce effect intensity on mobile devices
- Provide option to disable effects for accessibility
- Profile with actual content, not just empty screens

---

## Templates

Ready-to-use starter files:

- [react-tuimorphic-starter.tsx](templates/react-tuimorphic-starter.tsx) - React app with Tuimorphic
- [swiftui-crt-view.swift](templates/swiftui-crt-view.swift) - SwiftUI view with CRT effect
- [crt-shader.metal](templates/crt-shader.metal) - Complete Metal shader
- [neon-glow.css](templates/neon-glow.css) - CSS neon effects

---

## Common Pitfalls

This section documents real failure modes and edge cases that break TUI implementations. These are non-obvious gotchas discovered through practical use across platforms.

### Terminal Compatibility Issues

**Problem:** Escape sequences vary across terminal emulators. What works in iTerm2 may fail in older xterm, SSH terminals, or Windows Terminal.

**Common failures:**
- **256-color vs ANSI:** Terminals support different color depths. Code using `#rgb` hex colors works in modern terminals but falls back to 16-color ANSI on older systems.
- **Reset sequences:** Forgetting to reset text attributes (`\x1b[0m` or `\x1b[m`) can poison the terminal state for subsequent output.
- **Unicode box-drawing on Windows:** Windows PowerShell/Terminal may not render `─ │ ┌ ┐` correctly. Test on Windows before shipping.
- **VT100 incompleteness:** SSH to older Linux systems often hits VT100-only support. Box-drawing characters render as gibberish.

**Prevention:**
- Test on target terminals: iTerm2, Terminal.app, Windows Terminal, SSH Linux, Alacritty
- Fall back to ASCII when box-drawing fails: use `+`, `-`, `|` as fallback
- Always reset attributes after styled text: `\x1b[0m` is your friend
- Detect terminal capability: Check `TERM` env var (`TERM=xterm-256color` vs `TERM=xterm`)

**Example safe wrapper:**
```javascript
const supportsUnicode = process.env.TERM && process.env.TERM.includes('256');
const border = supportsUnicode ? '─' : '-';
```

### Layout Breaks on Resize

**Problem:** Fixed-width layouts collapse when terminal resizes. Common in web-based TUI where aspect ratio changes unexpectedly.

**Common failures:**
- **Hardcoded line widths:** A centered header assuming 80-column width breaks on a 60-column terminal.
- **Overflow hidden without truncation:** Content that's 100% width + padding exceeds container, causing text to spill or wrap unexpectedly.
- **Aspect ratio assumptions:** Scanline overlays, CRT curves assume 16:9. On ultra-wide or mobile, artifacts become obvious.
- **Grid layouts with fixed items:** Using `display: grid` with `grid-template-columns: 100px 200px 100px` fails to adapt to small screens.

**Prevention:**
- Use viewport-relative units: `vw`, `vh`, or `calc(100% - Xpx)`
- Implement text truncation with ellipsis: `overflow: hidden; text-overflow: ellipsis; white-space: nowrap;`
- Test at: 120 columns, 80 columns, 40 columns (mobile), ultra-wide
- For scanline effects, use percentage-based frequency that scales with viewport
- Use CSS `@media` or JS `ResizeObserver` to adapt layout dynamically

**Scanline example that fails:**
```css
/* ❌ Breaks on narrow screens */
background: repeating-linear-gradient(0deg, transparent, transparent 20px, black 20px, black 21px);
```

**Better approach:**
```css
/* ✅ Scales with viewport height */
background: repeating-linear-gradient(0deg, transparent, transparent calc(2% of height), black calc(2% of height), black calc(2% of height + 1px));
```

### Input Handling Edge Cases

**Problem:** User input isn't just alphanumeric. Real-world input includes multi-byte UTF-8, special keys, paste buffers, and autocomplete.

**Common failures:**
- **UTF-8 character counting:** JavaScript's `string.length` counts UTF-16 code units, not characters. A 4-byte emoji `🎮` has `length: 2`, breaking cursor positioning and validation.
- **Paste buffer handling:** Users paste large blocks of text. Input handlers without streaming cause UI to freeze.
- **Arrow keys vs WASD:** Terminal-based games assume WASD but users expect arrow keys. Missing support = bad UX.
- **Special keys lost in translation:** Ctrl+C, Ctrl+Z, Tab work differently across platforms. SSH terminals lose some meta-keys.
- **IME composition:** Input Method Engine (for Chinese, Japanese, Korean) sends partial characters before final composition. Validating on every keystroke breaks IME input.

**Prevention:**
- Use grapheme-aware libraries: `Intl.Segmenter` (modern), or `graphemesplitter` npm package
- Implement paste as multi-character stream, not a single event
- Support both arrow keys AND WASD for navigation
- Handle IME: validate only on final `compositionend`, not `compositionupdate`
- Test on macOS (Command key), Windows (Alt), Linux (various WM behavior)

**Correct UTF-8 cursor positioning:**
```javascript
// ❌ Wrong: counts UTF-16 code units
const cursorPos = input.value.length;  // "🎮🎮" = length: 4

// ✅ Correct: counts grapheme clusters
const segmenter = new Intl.Segmenter();
const cursorPos = [...segmenter.segment(input.value)].length;  // "🎮🎮" = 2
```

### Performance Issues

**Problem:** TUI effects (scanlines, glow, flicker) are expensive. Naive implementations cause jank and CPU/battery drain.

**Common failures:**
- **Continuous redraws:** Updating DOM every frame via JS (not GPU) causes 60+ reflows per second. Leads to choppy animation, 100%+ CPU.
- **Too many text-shadow layers:** Each `text-shadow: 0 0 5px, 0 0 10px, 0 0 20px, ...` requires a separate GPU pass. 10+ shadows = measurable lag.
- **Flickering at high frequency:** `setInterval(..., 16ms)` for flicker ties to animation frame time, causing stutter if main thread is busy.
- **Scanline overlay recompute:** Recalculating `repeating-linear-gradient` on every resize (without debounce) causes jank.
- **WebGL without throttling:** Full-screen CRT shaders running at 120fps on low-end mobile = instant battery drain.

**Prevention:**
- Use CSS `@keyframes` for continuous effects (GPU-accelerated)
- Limit neon glow to 3-4 text-shadow layers; test on mobile
- Debounce resize handlers: `ResizeObserver` with throttle, or `window.requestAnimationFrame`
- Use `will-change: transform, filter` sparingly on elements that animate
- Provide reduced-motion option: `prefers-reduced-motion: reduce`
- On mobile, detect CPU capacity: throttle effects on low-power devices

**Flicker that performs well:**
```css
/* ✅ GPU-accelerated, smooth */
@keyframes flicker {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.95; }
}
.flicker { animation: flicker 3s infinite; }
```

**Flicker that causes jank:**
```javascript
// ❌ Main thread blocked, stutter
setInterval(() => {
  element.style.opacity = Math.random() > 0.5 ? 1 : 0.9;
}, 50);
```

### Accessibility Gaps

**Problem:** Terminal UIs often ignore accessibility. Screen readers, keyboard navigation, color contrast all suffer.

**Common failures:**
- **No keyboard navigation:** Clickable elements only respond to mouse. Screen reader users and keyboard-only users are blocked.
- **Color-only status indicators:** Red text for error, green for success. Colorblind users (8% of males, 0.5% of females) can't distinguish.
- **Missing ARIA labels:** Screen readers announce "Button" instead of "Execute command". Confusing for blind users.
- **Fixed-size text:** Neon glow at 48px looks cool but breaks at 14px for visually impaired users. No zoom support = inaccessible.
- **No focus indicators:** After Tab-navigating to a button, there's no visible focus ring. Users lose their place.
- **Animated elements without pause:** Flicker and scanlines can trigger photosensitive epilepsy. Missing `prefers-reduced-motion` support = legal/safety risk.

**Prevention:**
- Implement full keyboard navigation: Tab/Shift+Tab, Enter to activate, Arrow keys for lists
- Test with screen reader: VoiceOver (macOS), NVDA (Windows), JAWS
- Add ARIA labels: `aria-label="Start system"`, `aria-describedby="help-text"`
- Ensure 4.5:1 contrast ratio for text (WCAG AA standard)
- Provide `prefers-reduced-motion` alternative: disable flicker, scanlines, animations
- Focus indicators: `:focus { outline: 2px solid #0ff; }` is mandatory

**Accessible neon button:**
```tsx
<button
  aria-label="Execute diagnostic"
  className="neon-button"
  onClick={handleClick}
  onKeyDown={(e) => e.key === 'Enter' && handleClick()}
>
  EXECUTE
</button>

<style>
  .neon-button:focus {
    outline: 2px solid #0ff;
    outline-offset: 2px;
  }
  
  @media (prefers-reduced-motion: reduce) {
    .neon-button {
      text-shadow: none; /* Remove glow */
      animation: none;   /* Remove flicker */
    }
  }
</style>
```

### Terminal Emulator Differences

**Quick reference for platform-specific behaviors:**

| Emulator | Notable Quirks | Fix |
|----------|---|---|
| **iTerm2** (macOS) | Renders all Unicode correctly; true-color support | None needed |
| **Terminal.app** (macOS) | Limited color palette; older xterm behavior | Test with 256-color mode |
| **Alacritty** | Ultra-fast; true-color; may not render some Unicode | Works reliably if iTerm2 works |
| **Windows Terminal** | Supports true-color; WSL integration works well | None needed for modern code |
| **PowerShell** | Old versions render box-drawing as `?`; use fallback | Check `$PSVersionTable` |
| **SSH/xterm** | VT100 only; no true-color; no mouse events | Fall back to ASCII + ANSI colors |
| **Tmux** | Passthrough mode required for true-color: `set -g default-terminal "tmux-256color"` | Configure tmux.conf |
| **Screen** | Even older terminal support; avoid fancy effects | Use ASCII-only mode |

**Platform detection example:**
```bash
if [[ "$TERM" == "xterm" ]]; then
  # Old terminal: use ASCII
  BORDER="+"
  COLORS="ANSI"
elif [[ "$TERM" == *"256color"* ]]; then
  # Modern terminal: use box-drawing + 256 colors
  BORDER="─"
  COLORS="256"
else
  # Unknown: default to safe
  BORDER="+"
  COLORS="ANSI"
fi
```

### When CRT Effects Backfire

**Problem:** Scanlines, glow, and distortion look cool in mockups but cause problems in practice.

**Common failures:**
- **Scanlines reduce readability:** Fine horizontal lines over text make it harder to read, especially on mobile or at distance. People with low vision can't read it.
- **Glow hides text:** Heavy neon glow (`text-shadow` with 10+ layers) blurs text edges, reducing legibility.
- **Barrel distortion breaks alignment:** CRT curvature looks authentic but makes content appear misaligned. Users think UI is broken.
- **Flicker induces motion sickness:** Subtle flicker causes nausea in some users. Photosensitive epilepsy is a real safety concern.

**Prevention:**
- Use subtle scanlines: 10-15% opacity, visible but not interfering with text
- Limit glow intensity: if glow radius > 20px, text becomes unreadable
- Distortion is decorative only: never use it for critical layout
- Always provide `prefers-reduced-motion` escape hatch
- Test with actual users: "Can you read this comfortably?"

---

## Resources

### Libraries
- [Tuimorphic](https://github.com/douglance/tuimorphic) - React terminal UI components
- [Inferno](https://github.com/twostraws/Inferno) - Metal shaders for SwiftUI
- [CRTFilter.js](https://github.com/nicholashamilton/crtfilter) - WebGL CRT effects
- [@react-three/postprocessing](https://github.com/pmndrs/react-postprocessing) - React Three.js effects

### Documentation
- [SwiftUI Metal Shaders](https://developer.apple.com/documentation/swiftui/view/layereffect(_:maxsampleoffset:isenabled:))
- [CSS text-shadow](https://developer.mozilla.org/en-US/docs/Web/CSS/text-shadow)

### Inspiration
- [SRCL / Sacred Computer](https://srcl.org/) - Design influence for Tuimorphic
- [Cool Retro Term](https://github.com/Swordfish90/cool-retro-term) - Terminal emulator with CRT effects
