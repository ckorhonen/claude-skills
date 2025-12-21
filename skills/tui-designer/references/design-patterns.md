# Design Patterns for Retro/Cyberpunk TUI

Layout patterns, composition techniques, and aesthetic principles for terminal-style interfaces.

## Core Aesthetic Principles

### 1. Information Density
Terminal UIs pack information efficiently. Use:
- Compact layouts with minimal padding
- Dense text with clear hierarchy
- Multiple data points visible simultaneously

### 2. Visual Hierarchy Through Typography
Without color variety, create hierarchy via:
- **UPPERCASE** for headers and labels
- `lowercase` for body content
- Different brightness levels (bright/medium/dim)
- Box-drawing borders for emphasis

### 3. Monochrome with Purpose
Limit colors to reinforce the aesthetic:
- One primary color (green, amber, cyan)
- Brightness variations for hierarchy
- Reserve secondary colors for alerts/status

### 4. Authentic Imperfection
CRT monitors weren't perfect. Subtle effects add authenticity:
- Slight scanlines
- Gentle glow/bloom
- Occasional flicker
- Rounded screen edges

---

## Layout Patterns

### Full-Screen Terminal

```
┌─────────────────────────────────────────┐
│ SYSTEM MONITOR v2.1                     │
├─────────────────────────────────────────┤
│                                         │
│  > STATUS: ONLINE                       │
│  > UPTIME: 47d 12h 34m                  │
│  > LOAD:   0.42 0.38 0.31               │
│                                         │
│  [CPU]  ████████░░░░░░░░  45%           │
│  [MEM]  ██████████░░░░░░  62%           │
│  [DSK]  ████░░░░░░░░░░░░  23%           │
│                                         │
├─────────────────────────────────────────┤
│ > _                                     │
└─────────────────────────────────────────┘
```

### Split Panel Layout

```
┌─────────────────┬───────────────────────┐
│ NAVIGATION      │ CONTENT               │
├─────────────────┤                       │
│ > Dashboard     │ ┌─────────────────┐   │
│   Logs          │ │ System Status   │   │
│   Settings      │ │                 │   │
│   Users         │ │ CPU: 45%        │   │
│   Reports       │ │ MEM: 2.1GB      │   │
│                 │ │ NET: 142MB/s    │   │
│                 │ └─────────────────┘   │
│                 │                       │
└─────────────────┴───────────────────────┘
```

### Dashboard Grid

```
┌─────────────┬─────────────┬─────────────┐
│ CPU         │ MEMORY      │ NETWORK     │
│             │             │             │
│    45%      │   2.1GB     │  142MB/s    │
│  ████░░░░   │  ██████░░   │  ↑78 ↓64    │
└─────────────┴─────────────┴─────────────┘
┌───────────────────────────────────────────┐
│ RECENT ACTIVITY                           │
├───────────────────────────────────────────┤
│ 14:23:01  User login: admin               │
│ 14:22:45  Service started: nginx          │
│ 14:22:30  Config updated: /etc/app.conf   │
└───────────────────────────────────────────┘
```

### Dialog/Modal

```
╔═══════════════════════════════════════╗
║            ⚠ WARNING                  ║
╠═══════════════════════════════════════╣
║                                       ║
║  Are you sure you want to proceed?    ║
║  This action cannot be undone.        ║
║                                       ║
║  ┌─────────┐       ┌─────────┐        ║
║  │ CANCEL  │       │ CONFIRM │        ║
║  └─────────┘       └─────────┘        ║
║                                       ║
╚═══════════════════════════════════════╝
```

---

## Component Patterns

### Status Indicators

```
ONLINE  ● ──────────────  Active and running
OFFLINE ○ ──────────────  Disconnected
WARNING ◐ ──────────────  Needs attention
ERROR   ◉ ──────────────  Critical issue
```

CSS/SwiftUI:
```css
.status-online::before { content: '●'; color: #00ff00; }
.status-offline::before { content: '○'; color: #666666; }
.status-warning::before { content: '◐'; color: #ffcc00; }
.status-error::before { content: '◉'; color: #ff4444; }
```

### Progress Bars

```
ASCII blocks:
[████████░░░░░░░░░░░░] 40%
[████████████████████] 100%
[░░░░░░░░░░░░░░░░░░░░] 0%

Braille dots:
⣿⣿⣿⣿⣿⣿⣿⣿⣀⣀⣀⣀⣀⣀⣀⣀ 50%

Simple:
|========          | 40%
```

### Menu Navigation

```
┌─ MAIN MENU ─────────────────────┐
│                                 │
│   [1] New Project               │
│   [2] Open Project              │
│   [3] Recent Files         →    │
│   ─────────────────────────     │
│   [4] Settings                  │
│   [5] Help                      │
│   ─────────────────────────     │
│   [Q] Quit                      │
│                                 │
│   Enter selection: _            │
│                                 │
└─────────────────────────────────┘
```

### Data Tables

```
┌──────────┬──────────┬──────────┬──────────┐
│ NAME     │ STATUS   │ CPU      │ MEMORY   │
├──────────┼──────────┼──────────┼──────────┤
│ server-1 │ ONLINE   │ 45%      │ 2.1GB    │
│ server-2 │ ONLINE   │ 32%      │ 1.8GB    │
│ server-3 │ OFFLINE  │ --       │ --       │
│ server-4 │ WARNING  │ 89%      │ 3.2GB    │
└──────────┴──────────┴──────────┴──────────┘
```

### Form Layout

```
┌─ USER REGISTRATION ─────────────────────┐
│                                         │
│  USERNAME:  [____________________]      │
│  PASSWORD:  [____________________]      │
│  EMAIL:     [____________________]      │
│                                         │
│  ROLE:      ( ) Admin                   │
│             (●) User                    │
│             ( ) Guest                   │
│                                         │
│  OPTIONS:   [x] Enable notifications    │
│             [ ] Subscribe to updates    │
│                                         │
│  ┌──────────┐  ┌──────────┐             │
│  │  CANCEL  │  │  SUBMIT  │             │
│  └──────────┘  └──────────┘             │
│                                         │
└─────────────────────────────────────────┘
```

### Command Output

```
┌─ TERMINAL ──────────────────────────────┐
│ $ ls -la                                │
│ total 48                                │
│ drwxr-xr-x  12 user  staff   384 Dec 15 │
│ -rw-r--r--   1 user  staff  1420 Dec 15 │
│ -rw-r--r--   1 user  staff   892 Dec 14 │
│                                         │
│ $ npm run build                         │
│ > building project...                   │
│ > ████████████████████ 100%             │
│ > Build complete in 4.2s                │
│                                         │
│ $ _                                     │
└─────────────────────────────────────────┘
```

---

## Animation Principles

### Cursor Blink
```css
@keyframes cursor-blink {
  0%, 49% { opacity: 1; }
  50%, 100% { opacity: 0; }
}
.cursor { animation: cursor-blink 1s step-end infinite; }
```

### Text Typing Effect
```javascript
function typeText(element, text, delay = 50) {
  let i = 0;
  const interval = setInterval(() => {
    element.textContent += text[i];
    i++;
    if (i >= text.length) clearInterval(interval);
  }, delay);
}
```

### Boot Sequence
1. Black screen
2. Single cursor blink
3. System messages appear one by one
4. Progress indicators
5. "READY" message
6. Command prompt appears

### Appropriate Motion
- **Fast**: Cursor blink, text entry
- **Medium**: Panel transitions, menu open/close
- **Slow**: Boot sequences, dramatic reveals
- **None**: Data updates (instant)

---

## Spacing & Sizing

### Character-Based Grid
Terminal UIs align to character widths:
```
Standard: 80 columns × 24 rows
Wide:     120 columns × 40 rows
Compact:  40 columns × 20 rows
```

### Padding Guidelines
- Panel padding: 1-2 characters
- Between elements: 1 line
- Section spacing: 2 lines
- Border to content: 1 character

### Typography Scale (monospace)
```
Header 1:  16-20px, UPPERCASE, bright
Header 2:  14-16px, UPPERCASE, medium
Body:      12-14px, mixed case, medium
Caption:   10-12px, lowercase, dim
```

---

## ASCII Art Integration

### Headers & Logos
```
 _____ _____ _____ _____ _____ _____
|   __|   __|   __|   __|   __|   __|
|__   |   __|__   |__   |   __|   __|
|_____|_____|_____|_____|_____|_____|

╔═╗╦ ╦╔═╗╔╦╗╔═╗╔╦╗  ╔═╗╔═╗
╚═╗╚╦╝╚═╗ ║ ║╣ ║║║  ║ ║╠═╝
╚═╝ ╩ ╚═╝ ╩ ╚═╝╩ ╩  ╚═╝╩
```

### Decorative Dividers
```
════════════════════════════════════
────────────────────────────────────
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
◆ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ◆
```

### Icons (Unicode)
```
Files:    📁 📄 📝 💾
Actions:  ▶ ⏸ ⏹ ⏺ ⏭ ⏮
Status:   ✓ ✗ ● ○ ◉ ◐
Arrows:   ← → ↑ ↓ ↵ ⇒
Misc:     ⚙ ⚡ ⌘ ⎇ ⏎
```

---

## Responsive Considerations

### Breakpoints (character-based)
```
Mobile:   40 columns  (simplified layout)
Tablet:   80 columns  (standard terminal)
Desktop:  120 columns (expanded layout)
```

### Adaptation Strategies

**Mobile (40 cols):**
- Stack panels vertically
- Abbreviate labels
- Hide secondary information
- Simplify borders

**Tablet (80 cols):**
- Side-by-side panels
- Full labels
- Standard box-drawing

**Desktop (120 cols):**
- Multi-column grids
- Expanded details
- Additional panels

---

## Accessibility

### Color Contrast
All text should have minimum 4.5:1 contrast ratio:
- Green #00ff00 on #001100: ~17:1 ✓
- Amber #ffb000 on #1a1000: ~12:1 ✓
- Cyan #00ffff on #0a0a1a: ~15:1 ✓

### Screen Readers
- Use semantic HTML (headings, lists, tables)
- Provide alt text for ASCII art
- Ensure keyboard navigation
- Don't rely solely on color for meaning

### Motion Sensitivity
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.001ms !important;
    transition-duration: 0.001ms !important;
  }
}
```

### High Contrast Mode
Provide option to disable glow effects and increase contrast:
```css
.high-contrast {
  --text-color: #ffffff;
  --bg-color: #000000;
  text-shadow: none;
  filter: none;
}
```
