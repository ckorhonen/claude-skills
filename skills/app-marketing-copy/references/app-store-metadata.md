# App Store / Play Store metadata (quick reference)

Always verify current requirements in the platform consoles/docs; limits/policies can change.

## Common field limits (characters)

### iOS App Store (App Store Connect)

- App Name: 30
- Subtitle: 30
- Promotional Text: 170
- Keywords: 100 (comma-separated; spaces usually waste chars)
- Description: 4000
- “What’s New” (release notes): 4000

### Google Play (Play Console)

- Title: 30
- Short description: 80
- Full description: 4000

Tip: Use `scripts/check_app_store_limits.py` to sanity-check counts for a draft.

## Output skeletons

### iOS listing skeleton

- App Name (2–3 options)
- Subtitle (2–3 options)
- Promotional Text (1–2 options)
- Keywords (1–3 keyword sets)
- Description (one best version + optional alternate opening paragraph)
  - 1–2 sentence hook (outcome-first)
  - 3–5 benefit bullets (scannable)
  - 3–6 feature bullets (concrete, not fluffy)
  - Proof (optional): review snippet, stat, award (only if true)
  - CTA + “who it’s for”
  - Privacy note (if relevant; no legal advice)
- What’s New (release notes; 1–2 styles: friendly vs factual)

### Google Play listing skeleton

- Title (2–3 options)
- Short description (3–5 options; punchy, outcome-first)
- Full description (one best version + optional alternate first paragraph)
  - Hook
  - Benefits
  - Features
  - Proof (optional)
  - CTA
- Release notes (friendly vs factual)

## ASO keyword heuristics (platform-agnostic)

- Start from: category keywords, core verbs, problems, outcomes, and feature nouns.
- Mix: broad terms + long-tail specifics.
- Avoid: competitor trademarks/brand names, unsupported superlatives, spammy repetition.
- Prefer: words users actually search (plain language over internal jargon).

