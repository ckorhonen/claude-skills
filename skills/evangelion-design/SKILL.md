---
name: evangelion-design
description: "Design original Evangelion-inspired web and mobile interfaces with NERV-like command-center, HUD, psychographic, sync-monitor, breach-warning, and title-card language: sharp geometry, tactical typography, disciplined data density, danger-first palettes, wireframe analysis forms, repeated instrument arrays, and mechanical animation. Use when users ask for Evangelion, NERV, anime control room UI, sci-fi military instrumentation, diagnostic overlays, psychographic displays, sync monitors, countdown screens, or dramatic system-state motion for product interfaces."
---

# Evangelion Design

Apply Evangelion-inspired interface language to web and mobile products without turning the result into generic neon cyberpunk or a direct franchise copy. The source material uses UI as story pressure: severe geometry, narrow color signals, dense but legible telemetry, and motion that behaves like machinery under stress.

## Quick Start

1. Pick the screen role first: `hud`, `command-center`, `psychograph`, `sync-ladder`, `reactor-diagnostic`, `breach-monitor`, or `title-card`.
2. Pick one hot accent family for the screen: `amber`, `red`, or `signal-green`. Add one cool support only when the composition needs separation.
3. Build the layout from frames, rulers, rings, bars, masks, repeated device arrays, and crosshair geometry before adding decorative texture.
4. Animate the screen by revealing state: counters, sweeps, trace plotting, sync steps, panel swaps, and alert pulses.
5. Keep the work original. Echo the language of Evangelion, but do not reuse exact logos, title cards, or one-to-one screen compositions.

## Workflow

### 1. Define the dramatic job

Choose the emotional function before choosing components.

- `hud`: first-person overlays on top of imagery; use wide masks, target brackets, sparse ticks, and range markers.
- `command-center`: black-field dashboards with multiple contained modules, status rails, tables, and analytic views.
- `diagnostic`: charts, sync traces, matrices, and ring analyzers; prioritize precision and hierarchy over spectacle.
- `psychograph`: bounded graph surfaces with rulers, sparse cross markers, label boxes, and one dense organic or signal trace.
- `sync-ladder`: repeated capsules, bars, or slotted modules stepping across rows or diagonals with one or two repeated labels.
- `reactor-diagnostic`: a framed triptych or panoramic board with a dominant central radial analyzer and intentionally sparse side bays.
- `breach-monitor`: oversized timers, progress blocks, rack arrays, projected-penetration bars, and other imminent-threat displays.
- `warning-state`: higher contrast, repeated status labels, countdowns, and tighter cadence.
- `title-card`: near-empty black compositions with oversized typography and one dominant accent.

### 2. Compose the screen

- Anchor major modules to edges, diagonals, panoramic masks, or one large enclosing frame. Large dead zones are useful because they create tension.
- Prefer clipped rectangles, notched frames, circles, ring charts, ladders, ruled lines, wireframe curves, and external callout labels.
- Use one or two dominant geometric ideas per view. Do not stack every sci-fi trope into the same screen.
- Use repetition aggressively when the screen is about synchronization, layers, purity, or compatibility. Identical modules are part of the drama.
- Let one hero structure dominate: a scribble trace, a wireframe globe, a circular reactor, a countdown, or a field of capsules.
- Keep corners sharp or minimally cut. Rounded consumer-app cards weaken the tone.
- Treat texture as secondary. The framework should read clearly even before glow, grain, or background imagery is added.

### 3. Set typography and copy

- Use condensed sans for labels and headers.
- Use monospaced numerals for timers, telemetry, and tables.
- Reserve a dramatic display serif for rare splash or chapter-card moments only.
- Default to uppercase labels, short phrases, system verbs, and explicit state language.
- Use tiny micro-labels and registration marks to make large canvases feel calibrated, but keep the active label path bright enough to scan.
- Use bilingual copy only when it is meaningful and accurate.

### 4. Adapt for product UI

- On web, lean into widescreen overlays, dense side rails, and multi-panel compositions.
- On mobile, reduce simultaneous modules. Keep one hero instrument per screen and collapse side bays into stacked rails, tabs, or swipable diagnostics.
- Convert ultra-wide frames into a central instrument plus one secondary strip instead of compressing every module into illegible miniatures.
- Let dense telemetry support the mood, but make primary actions readable without it.
- Translate the style through the existing design system when possible instead of rebuilding every primitive.

Read `references/style-guide.md` for palette, type, layout, motion, and implementation tokens.
Read `references/source-signals.md` when you want the rationale behind the look and the analyzed source cues.

## Common Pitfalls

The most frequent failure modes when applying Evangelion design language:

### Too Literal: Copying Frames Instead of Extracting Principles

**The trap:** Taking a screenshot from the anime and translating it directly to your product — replicating the AT field borders, the exact LCL tank layout, or the bridge console panel-for-panel.

**Why it fails:** 
- Licensed assets and direct copies undermine originality
- Anime compositions are designed for 16:9 narrative pacing, not responsive product interaction
- A slavish copy reads as theme-park superficiality, not disciplined design language

**What works instead:**
- Extract the *principle* (e.g., "layered transparent rings showing state") not the shape
- Adapt the scale and rhythm to your product's actual data density and user workflow
- Let your interface solve your problem first; the Evangelion language is the *tone*, not the template

**Example:** NERV uses nested ring analyzers for multi-layer status. A real product using this principle would adapt it to show network latency layers, cache hierarchies, or concurrent request states — the *structure* echoes, but the content is native.

---

### Information Overload Without Hierarchy

**The trap:** Packing every data point, every label, and every decorative trace onto the same black field because "Evangelion is dense."

**Why it fails:**
- Evangelion's density serves hierarchy: critical state signals are *larger and hotter*, secondary telemetry is small and cool-toned
- Without a clear focal point, the user scans randomly and misses actionable data
- Overloading opacity, glow, and animation on every element creates visual noise, not clarity

**What works instead:**
- Establish a clear signal hierarchy: *What does the user need to act on right now?* Make that hero-sized and hot-colored
- Relegate diagnostic telemetry, trend traces, and background metrics to smaller, cooler, lower-contrast zones
- Use negative space aggressively — empty black areas around the hero signal *create tension* and focus

**Example:** A sync monitor screen shows three LCDs: current sync% in bold amber, trend trace in dim green below, and historical peak in micro-text at the edge. The eye goes to sync% first. A common mistake would put all three at the same size, burying the critical metric.

---

### Missing Context Cues: Users Get Lost in Complexity

**The trap:** Building a beautiful command-center dashboard but omitting visual anchors — labels, section dividers, or state markers that let users navigate the complexity.

**Why it fails:**
- Evangelion UI is dense *and* navigable: the AT field outline tells you "this is a status zone," the title card reads top-left, the capsule ladder steps left-to-right
- Without these cues, a user loses spatial awareness and can't find what they're looking for in a glance
- Dense without context becomes overwhelming rather than reassuring

**What works instead:**
- Use frame lines, notched edges, and section labels to partition the screen into scannable zones
- Place consistent reference labels and directional markers so the user knows "I am looking at reactor diagnostics, not personnel sync"
- Let the geometric structure *teach* the user where to look and how to move through the interface

**Example:** A diagnostic triptych has a dominant central analyzer flanked by two status bays. Label the center "CORE THERMAL" and the sides with their own title. Without those labels, the user doesn't know if they're looking at reactor status or personnel data.

---

### Style Over Function: Looks Cool, But Unusable

**The trap:** Prioritizing visual drama (glowing scanlines, sweeping animations, fog effects) over legibility and interaction feedback.

**Why it fails:**
- A gorgeous interface that doesn't clearly show what's happening or how to interact is frustrating, not impressive
- Evangelion's motion serves function: sweep animations reveal state transitions, pulsing alerts mark danger, trace plotting shows time-series data. It's always *doing* something
- Sacrificing click targets, affordances, or state feedback for aesthetic effect breaks usability

**What works instead:**
- Every animation should communicate state change or guide the user's attention
- Every element should have a clear interactive affordance if it's meant to be clicked, swiped, or expanded
- Aesthetic choices (glow, grain, color) should enhance, not obscure, primary actions and critical data

**Example:** A countdown timer animated with a smooth tween from 10 to 0 looks nice but doesn't communicate urgency. The *same timer* with a pulsing red background, bold serif numerals, and a sudden jump when crossing 2 minutes left communicates danger and prompts action.

---

### Ignoring Accessibility: Color and Contrast Issues

**The trap:** Using red-on-dark or red-green combinations as primary signals, assuming low contrast works because Evangelion looks "dark and moody."

**Why it fails:**
- Red and green together are indistinguishable to ~8% of viewers (color blindness)
- Low contrast fails WCAG standards and becomes unreadable on mobile or in bright light
- Evangelion does use red and green, but always with additional *shape, position, or label cues* to distinguish meaning
- Inaccessible designs exclude users and open you to compliance risk

**What works instead:**
- Use color as a support signal, not the primary identifier. Always add label text, icon, or shape distinction
- Test your palette against color-blindness simulators (Coblis, Contrast Ratio) before shipping
- Ensure text and interactive elements meet WCAG AA contrast (4.5:1 for body text, 3:1 for large text)
- Leverage Evangelion's geometric language: if red means "alert," add an exclamation icon or border treatment so deuteranopia viewers still get the signal

**Example:** A status indicator that's just a red circle fails for color-blind users. The *same indicator* as a red circle *plus* a warning symbol *plus* the label "ALERT" works for all viewers and reads as more authentic to Evangelion's label-heavy style.

---

### NERV UI Works; Generic Sci-Fi Doesn't

The difference between authentic Evangelion language and generic neon cyberpunk often comes down to *discipline and specificity*:

| NERV UI (Works) | Generic Sci-Fi (Fails) |
|---|---|
| Flat black, amber, and signal green | Rainbow gradients, purple/cyan neon |
| Tall condensed sans labels with explicit state verbs | Vague floating text and decorative symbols |
| Modular repeated arrays (sync ladder, capsule racks) | Every element unique and ornate |
| Motion reveals state: sweep plots, panel swaps, alert pulses | Motion for motion's sake: constantly drifting glows |
| Negative space creates tension and focus | Every pixel filled with texture and glow |
| Accessible hierarchy and geometric guides | Dense chaos that looks impressive but isn't navigable |
| Typography and shape do the heavy lifting; glow is restrained | Relies on glow and blur to hide weak foundational design |

The key: Evangelion design is *severe* and *specific* about its choices. It's not "make it look sci-fi;" it's "make every element earn its place."

- Do not default to purple gradients, glassmorphism, soft blur, or playful spring motion.
- Do not make every surface glow. Most of the screen should feel matte, dark, and controlled.
- Do not use Japanese text or franchise symbols as decoration.
- Do not sacrifice accessibility for density; the hierarchy should still be clear with motion disabled.
- Do not copy Evangelion assets or layouts literally. Produce an original interpretation with the same tension and rigor.
