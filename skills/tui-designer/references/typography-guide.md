# Typography Guide for Retro/Cyberpunk TUI

Monospace fonts and special characters for authentic terminal aesthetics.

## Recommended Fonts

### Web Fonts (Priority Order)

1. **GNU Unifont** - Tuimorphic default, excellent Unicode coverage including box-drawing
2. **IBM Plex Mono** - Clean, modern, open source
3. **JetBrains Mono** - Developer-focused with ligatures
4. **Fira Code** - Popular with ligatures, good at small sizes
5. **Source Code Pro** - Adobe, wide character support
6. **Roboto Mono** - Google, clean and readable
7. **Inconsolata** - Humanist monospace

### iOS/macOS Fonts

1. **SF Mono** - Apple system monospace (macOS 10.12+, iOS 17+)
2. **Menlo** - Pre-SF Mono system font
3. **Monaco** - Classic Mac terminal font
4. **Courier New** - Universal fallback

### Font Stacks

**Web (Full Stack):**
```css
font-family:
  'GNU Unifont',
  'IBM Plex Mono',
  'JetBrains Mono',
  'Fira Code',
  'SF Mono',
  'Menlo',
  'Monaco',
  'Consolas',
  'Liberation Mono',
  'Courier New',
  monospace;
```

**Web (Minimal):**
```css
font-family: 'SF Mono', 'Menlo', 'Consolas', monospace;
```

**Terminal Aesthetic:**
```css
font-family: 'VT323', 'Press Start 2P', 'Courier New', monospace;
```

---

## Font Loading (Web)

### Google Fonts
```html
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;700&display=swap" rel="stylesheet">
```

### Self-Hosted with @font-face
```css
@font-face {
  font-family: 'GNU Unifont';
  src: url('/fonts/unifont.woff2') format('woff2');
  font-weight: normal;
  font-style: normal;
  font-display: swap;
}
```

### Tuimorphic (Bundled)
```tsx
import 'tuimorphic/styles.css'; // Includes GNU Unifont
```

---

## SwiftUI Font Declarations

### System Monospace
```swift
// Dynamic type with monospace design
Text("Terminal")
    .font(.system(size: 16, weight: .regular, design: .monospaced))

// Using Font.Design
.font(.system(.body, design: .monospaced))

// Monospaced digits only (keeps proportional letters)
Text("12:34:56")
    .monospacedDigit()
```

### SF Mono Specifically
```swift
// SF Mono by name
Text("Code")
    .font(.custom("SFMono-Regular", size: 14))

// Available SF Mono weights
// SFMono-Light, SFMono-Regular, SFMono-Medium
// SFMono-Semibold, SFMono-Bold, SFMono-Heavy
```

### Custom Font with Dynamic Type
```swift
extension Font {
    static func terminalFont(size: CGFloat) -> Font {
        .custom("JetBrainsMono-Regular", size: size, relativeTo: .body)
    }
}

// Usage
Text("Output").font(.terminalFont(size: 14))
```

---

## Box-Drawing Characters

Essential characters for creating terminal-style borders and frames.

### Light Box Drawing
```
Horizontal:  ─  (U+2500)
Vertical:    │  (U+2502)
Corners:     ┌ ┐ └ ┘  (U+250C, U+2510, U+2514, U+2518)
T-pieces:    ├ ┤ ┬ ┴  (U+251C, U+2524, U+252C, U+2534)
Cross:       ┼  (U+253C)
```

### Heavy Box Drawing
```
Horizontal:  ━  (U+2501)
Vertical:    ┃  (U+2503)
Corners:     ┏ ┓ ┗ ┛  (U+250F, U+2513, U+2517, U+251B)
T-pieces:    ┣ ┫ ┳ ┻  (U+2523, U+252B, U+2533, U+253B)
Cross:       ╋  (U+254B)
```

### Double Line
```
Horizontal:  ═  (U+2550)
Vertical:    ║  (U+2551)
Corners:     ╔ ╗ ╚ ╝  (U+2554, U+2557, U+255A, U+255D)
T-pieces:    ╠ ╣ ╦ ╩  (U+2560, U+2563, U+2566, U+2569)
Cross:       ╬  (U+256C)
```

### Rounded Corners
```
Corners:     ╭ ╮ ╰ ╯  (U+256D, U+256E, U+256F, U+2570)
```

### Block Elements
```
Full block:     █  (U+2588)
Light shade:    ░  (U+2591)
Medium shade:   ▒  (U+2592)
Dark shade:     ▓  (U+2593)
Half blocks:    ▀ ▄ ▌ ▐  (U+2580, U+2584, U+258C, U+2590)
```

---

## Example Frames

### Simple Frame
```
┌──────────────────┐
│  SYSTEM STATUS   │
├──────────────────┤
│  CPU: 45%        │
│  MEM: 2.1GB      │
└──────────────────┘
```

### Double Frame
```
╔══════════════════╗
║   WARNING        ║
╠══════════════════╣
║ Access Denied    ║
╚══════════════════╝
```

### Rounded Frame
```
╭──────────────────╮
│  Welcome Back    │
╰──────────────────╯
```

### Mixed (Heavy/Light)
```
┏━━━━━━━━━━━━━━━━━━┓
┃  MAIN MENU       ┃
┣━━━━━━━━━━━━━━━━━━┫
┃ 1. New Game      ┃
┃ 2. Load Game     ┃
┃ 3. Options       ┃
┗━━━━━━━━━━━━━━━━━━┛
```

---

## CSS Helper Classes

```css
/* Terminal text styling */
.terminal-text {
  font-family: 'SF Mono', 'Consolas', monospace;
  font-size: 14px;
  line-height: 1.4;
  letter-spacing: 0;
  white-space: pre;
  tab-size: 4;
}

/* Uppercase terminal headers */
.terminal-header {
  font-family: 'SF Mono', monospace;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

/* Blinking cursor */
.cursor::after {
  content: '█';
  animation: blink 1s step-end infinite;
}

@keyframes blink {
  50% { opacity: 0; }
}
```

---

## SwiftUI Text Modifiers

```swift
extension Text {
    func terminalStyle() -> some View {
        self
            .font(.system(size: 14, design: .monospaced))
            .tracking(0)
            .lineSpacing(2)
    }

    func terminalHeader() -> some View {
        self
            .font(.system(size: 16, weight: .bold, design: .monospaced))
            .textCase(.uppercase)
            .tracking(2)
    }
}
```

---

## Unicode Ranges Reference

For custom font subsetting or fallback configuration:

| Range | Description |
|-------|-------------|
| U+0020-007F | Basic Latin (ASCII) |
| U+2500-257F | Box Drawing |
| U+2580-259F | Block Elements |
| U+25A0-25FF | Geometric Shapes |
| U+2600-26FF | Miscellaneous Symbols |
| U+2190-21FF | Arrows |

---

## Performance Tips

1. **Subset fonts** to include only needed characters
2. **Use `font-display: swap`** for faster initial render
3. **Preload critical fonts**:
   ```html
   <link rel="preload" href="/fonts/mono.woff2" as="font" crossorigin>
   ```
4. **Consider system fonts first** for fastest loading
5. **Cache fonts** with long expiry headers
