# Screenshot generation prompts (templates)

Goal: generate consistent backgrounds/illustrations for app store screenshots and promo images (usually behind real UI screenshots). Default: “no text, no logos, no device frame”.

## Inputs to ask for

- Brand colors (hex if possible) + vibe words (e.g., calm, bold, playful, premium)
- Screenshot set size (usually 5–8) + story order
- Style: minimal / geometric / soft 3D / illustrative / photo-collage / retro
- Tool: Midjourney, DALL·E, Stable Diffusion, “other” (keep prompts tool-neutral if unknown)

## Global “style bible” prompt (make once, reuse)

Use this to keep all screenshots visually consistent:

- Minimal abstract background, cohesive color palette: {brand_colors}, subtle texture/noise, lots of negative space for UI overlay, gentle lighting, modern, clean, high contrast, no text, no watermark, no logo, no device, high resolution, vertical composition.

Then add per-screenshot “concept” lines (below) while keeping the style bible constant.

## Per-screenshot concept prompt pattern

Base:

- {style_bible}. Visual metaphor for “{concept}” using simple shapes/lighting. Keep center area clear for UI overlay. No text, no letters, no logos, no watermark.

Example concepts (swap in your app’s story):

- Screenshot 1 (core promise): clarity / speed / calm / control / “get it done”
- Screenshot 2 (feature 1): organization / planning / tracking / discovery
- Screenshot 3 (feature 2): automation / smart suggestions / shortcuts
- Screenshot 4 (proof): progress / streaks / charts / milestones (abstract, not literal)
- Screenshot 5 (delight): customization / themes / personalization
- Screenshot 6–8 (optional): collaboration / offline / security / integrations (abstract)

## Style variants (drop-in modifiers)

Append one modifier per series; don’t mix too many:

- Minimal gradient: “smooth gradient bands, subtle grain, soft shadows”
- Geometric: “bold geometric shapes, crisp edges, modern Swiss design”
- Soft 3D: “rounded 3D shapes, clay/plastic material, studio lighting”
- Illustrative: “flat vector illustration, limited palette, paper texture”
- Photo-collage: “clean cutout shapes + blurred bokeh background, premium editorial”
- Retro tech: “subtle CRT scanlines, neon glow, dark background, restrained”

## Negative prompt checklist

Include (exact phrasing optional):

- no text, no words, no letters
- no watermark, no logo, no brand marks
- no device frame, no phone mockup (unless explicitly desired)
- avoid faces/people unless the product demands it

