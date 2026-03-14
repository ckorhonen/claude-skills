# Evangelion Design Style Guide

## Sections

1. Source distillation
2. Palette
3. Typography
4. Composition
5. Motion
6. Web and mobile implementation
7. Review checklist

## 1. Source distillation

The analyzed material points to a consistent visual logic:

- UI is not ornament first. It exists to amplify threat, surveillance, synchronization, system readiness, or mission control.
- The visual building blocks are simple but exact: rulers, circles, bars, sine waves, matrices, crosshairs, frames, warning boxes, and panoramic masks.
- Motion is fast, procedural, and state-driven. Elements count, scan, blink, arm, or lock. They do not bounce, drift, or wobble.
- Density is controlled. Large black gaps make the active signals feel more urgent.
- The strongest looks stay disciplined with color. Most screens use one hot family with a small secondary signal rather than a rainbow of accents.

## 2. Palette

Use a dark structural base and then choose a single dominant signal family.

### Core darks

| Token | Hex | Role |
| --- | --- | --- |
| `eva-bg` | `#0b090b` | Primary background |
| `eva-panel` | `#140e0f` | Raised panels, masked overlays |
| `eva-panel-2` | `#221012` | Deep active surfaces |
| `eva-fog` | `#344642` | Cool atmospheric support for HUD views |

### Hot signal family

| Token | Hex | Role |
| --- | --- | --- |
| `eva-alert` | `#8f1507` | Critical alerts, outlines, emphasis |
| `eva-alert-2` | `#bb622d` | Warm linework, secondary highlight |
| `eva-warning` | `#f19e1f` | Timers, warning numerals, caution indicators |
| `eva-warning-soft` | `#cca552` | Filled charts, inactive caution blocks |

### Support signals

| Token | Hex | Role |
| --- | --- | --- |
| `eva-signal-green` | `#549f58` | Normal state, active confirmations |
| `eva-cool` | `#6f9b95` | Secondary graph lines, cool data overlays |
| `eva-ink` | `#f3ece2` | Title-card type, rare bright text |
| `eva-muted` | `#9c8a78` | Secondary labels, noncritical captions |

### Palette rules

- Keep at least 70% of the screen in dark neutrals.
- Use only one hot family as the main emphasis on a given view.
- Add green or cool teal as semantic state, not as decoration.
- Avoid full-spectrum neon mixes. Evangelion reads as disciplined hazard graphics, not nightclub lighting.
- If a surface glows, keep the glow tight and local to active lines or numerals.

### Ready-made color modes

- `command-red`: `eva-bg` + `eva-panel` + `eva-alert` + `eva-warning`
- `hud-fog`: `eva-bg` + `eva-fog` + `eva-warning` + tiny `eva-alert`
- `bio-scan`: `eva-bg` + deep crimson substrate + `eva-signal-green` + restrained `eva-warning`
- `title-card`: `eva-bg` + `eva-ink` + one muted hot accent

### Example CSS tokens

```css
:root {
  --eva-bg: #0b090b;
  --eva-panel: #140e0f;
  --eva-panel-2: #221012;
  --eva-fog: #344642;
  --eva-alert: #8f1507;
  --eva-alert-2: #bb622d;
  --eva-warning: #f19e1f;
  --eva-warning-soft: #cca552;
  --eva-signal-green: #549f58;
  --eva-cool: #6f9b95;
  --eva-ink: #f3ece2;
  --eva-muted: #9c8a78;
}
```

## 3. Typography

Use typography like instrumentation, not editorial web chrome.

### Recommended pairing

- Condensed sans: `IBM Plex Sans Condensed`, `Archivo Narrow`, `League Gothic`, or `DIN Condensed` analogs
- Mono: `IBM Plex Mono`, `JetBrains Mono`, or `Space Mono`
- Rare display serif for title-card moments: `Cormorant Garamond`, `Bodoni Moda`, or another severe high-contrast serif

### Type rules

- Default to uppercase for labels and section headers.
- Keep labels short and concrete: `SYNC RATE`, `TARGET`, `PHASE`, `LOCK`, `INTERNAL`, `LAYER 01`.
- Use tabular numerals everywhere numbers animate or align.
- Let body copy be sparse. Evangelion-style screens communicate through labels, figures, and states, not long paragraphs.
- Treat the serif mode as exceptional. Most screens should live in condensed sans plus mono.

## 4. Composition

### Structural patterns

- Panoramic masks for HUD overlays
- Thin ruled frames with hard corners
- Circular analyzers, reticles, and sweep arcs
- Stacked status rails and numbered layers
- Waveform traces, sine curves, and graph axes
- Grid-backed data tables with strong alignment
- Asymmetric placement with one dominant anchor and one or two secondary modules

### Composition rules

- Start with a black field and place only the modules the story needs.
- Make one module the main event. Everything else supports it.
- Use scale contrast aggressively: large number or chart, then tiny labels.
- Keep line weights thin and precise. Heavy borders feel too chunky.
- Prefer clipping, masking, and hard containment over drop shadows.
- Allow photographic or illustrated imagery behind HUDs, but desaturate it so the overlay owns the hierarchy.

### What to avoid

- Generic card grids with equal weight everywhere
- Pill buttons and soft rounded corners
- Full-screen blur panels
- Decorative hexagon wallpaper with no functional meaning
- Overbuilt chrome around simple controls

## 5. Motion

The reference motion behaves like an operating system under pressure.

### Motion principles

- Mechanical, not playful
- State-driven, not ornamental
- Fast, but readable
- Linear or stepped, not springy
- Localized to active elements, not the whole page

### Primary motion patterns

| Pattern | Duration | Usage |
| --- | --- | --- |
| `line-draw` | `80-160ms` | Frames, rulers, brackets drawing on |
| `scan-sweep` | `180-320ms` | Horizontal or radial scanner pass |
| `counter-tick` | `40-70ms` per step | Timers and telemetry increments |
| `lock-on` | `120-220ms` | Brackets converging on a target |
| `panel-swap` | `80-140ms` | Hard state change between modules |
| `alert-pulse` | `700-1200ms` | Ongoing critical state indicator |

### Motion rules

- Prefer `linear`, `ease-out`, or `steps(2-6, end)` timing.
- Use stagger as a system boot-up cue: frame, then labels, then numbers.
- Let countdowns visibly tick. They should feel procedural.
- Use opacity, transform, clip, and mask reveals instead of large blurs.
- Keep loops purposeful and narrow in scope. A small alert pulse is better than a whole-screen shimmer.
- On mobile, reduce simultaneous animated layers and pair critical state changes with subtle haptics when available.

### What to avoid

- Spring easing, bounce, overshoot
- Floating parallax
- Continuous hover bobbing
- Large breathing glows
- Full-screen flicker that harms readability

### Reduced motion fallback

- Keep all state changes readable with motion disabled.
- Replace sweeps with instant reveals.
- Freeze looping alert motion into static high-contrast states.
- Preserve countdown meaning via text and color, not motion alone.

### Example CSS timing

```css
.eva-counter {
  transition: opacity 120ms linear, transform 120ms ease-out;
}

.eva-scan {
  animation: eva-scan 240ms linear;
}

.eva-alert-pulse {
  animation: eva-alert-pulse 900ms steps(3, end) infinite;
}
```

## 6. Web and mobile implementation

### Web

- Use wide hero canvases for HUD or command views.
- Allow secondary telemetry to live in rails, overlays, and side modules.
- Favor CSS variables or design tokens so the palette can be reused consistently.
- Keep primary actions obvious; style the state display around them instead of burying them.

### Mobile

- Promote one active module per screen.
- Stack supporting metrics into narrow bands, tabs, or drawers.
- Reserve tiny telemetry for noninteractive support text.
- Respect safe areas; hard-edged frames should not collide with the notch or home indicator.
- Use motion sparingly. A single scan or lock-on reads better than five concurrent loops.

### SwiftUI color setup

```swift
extension Color {
    static let evaBg = Color(red: 0.043, green: 0.035, blue: 0.043)
    static let evaPanel = Color(red: 0.078, green: 0.055, blue: 0.059)
    static let evaAlert = Color(red: 0.561, green: 0.082, blue: 0.027)
    static let evaWarning = Color(red: 0.945, green: 0.620, blue: 0.122)
    static let evaSignal = Color(red: 0.329, green: 0.624, blue: 0.345)
}
```

## 7. Review checklist

- Does the screen communicate a clear system state or mission context?
- Is one module obviously primary?
- Is the palette limited and intentional?
- Would the interface still read if all motion stopped?
- Are the numbers aligned and easy to scan?
- Is the mobile version simplified rather than compressed?
- Does the result feel original rather than copied from a specific Evangelion frame?
