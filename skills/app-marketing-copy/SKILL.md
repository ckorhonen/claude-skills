---
name: app-marketing-copy
description: "Write marketing copy and App Store / Google Play listings (ASO keywords, titles, subtitles, short+long descriptions, feature bullets, release notes), plus screenshot caption sets and text-to-image prompt templates for generating store screenshot backgrounds/promo visuals. Use when asked to: write/refresh app marketing copy, craft app store metadata, brainstorm taglines/value props, produce ad/landing/email copy, or generate prompts for screenshot/creative generation."
---

# App Marketing Copy

## Quick start

1) Ask for missing inputs (or infer from repo/product docs):
- App name + 1-sentence value prop
- Target user + primary job-to-be-done
- 3–7 key features + 1–3 differentiators
- Desired tone (and words to use/avoid)
- Platform(s): iOS App Store, Google Play, or both
- Screenshot count and theme (if needed)

2) Confirm deliverables:
- Store listing (iOS, Google Play)
- Marketing pack (landing hero, feature blurbs, CTAs, ads)
- Screenshot pack (caption copy + image-generation prompts)

3) Produce 2–3 variants per high-impact field, then recommend a "best pick" with 1-sentence rationale.

## Examples

### Example 1: New App Store Listing

**User input:**
```
App: FocusTimer
Purpose: Pomodoro timer for students
Key features: Custom intervals, study stats, break reminders
Platform: iOS App Store
Tone: Friendly but not childish
```

**Workflow:**
1. Run intake questions to clarify missing details
2. Generate 3 subtitle variants, recommend best
3. Create keyword set optimized for student productivity searches
4. Write full description with feature bullets
5. Generate 5 screenshot captions in narrative order
6. Validate with `scripts/check_app_store_limits.py`

**Expected output:**
- iOS App Store listing (all fields within limits)
- 3 subtitle options with rationale
- Keyword set (100 chars max)
- Screenshot copy pack

### Example 2: Marketing Copy Refresh

**User input:**
```
"Our app store listing conversion is terrible. Help refresh it."
App: PhotoFix (photo editing)
Current problem: Generic copy, keyword-stuffed
```

**Workflow:**
1. Review current listing (if provided)
2. Ask: "What makes PhotoFix different from competitors?"
3. Identify ASO keyword stuffing issues
4. Generate 3 new subtitle variants (specific, benefit-focused)
5. Rewrite full description with user benefits (not tech specs)
6. Create fresh screenshot captions
7. Compare before/after character counts

**Expected output:**
- Refactored listing with specificity
- Side-by-side comparison showing improvements
- Rationale for each change

### Example 3: Multi-Platform Launch

**User input:**
```
Launching on both iOS and Google Play
App: TaskFlow (project management for freelancers)
Need everything: store listings, landing page copy, ads
```

**Workflow:**
1. Complete intake (audience, differentiators, proof points)
2. Generate iOS listing (subtitle, keywords, description)
3. Generate Google Play listing (short desc, feature bullets, full desc)
4. Create marketing pack (10 taglines, 3 hero sections, 6 feature blurbs, 10 CTAs)
5. Generate screenshot copy pack (8 captions + image prompts)
6. Validate all with `scripts/check_app_store_limits.py`

**Expected output:**
- Complete iOS App Store listing
- Complete Google Play listing
- Marketing copy pack (50+ deliverables)
- Screenshot pack with narrative arc

## Intake template (ask, then proceed)

- Audience: who + what they want
- Problem: what's hard today
- Outcome: what "success" looks like
- Differentiators: why this vs alternatives
- Proof: numbers, reviews, awards, press (if any)
- Constraints: claims to avoid, legal/compliance notes, pricing mention policy
- Locale(s): default to US English unless told otherwise

## Outputs

### iOS App Store listing

- Provide: App Name options, Subtitle options, Promotional Text, Keyword set, Full Description, "What's New" (release notes).
- Enforce field limits; if unsure, open `references/app-store-metadata.md` or run `scripts/check_app_store_limits.py`.

### Google Play listing

- Provide: Title options, Short Description options, Full Description, Feature bullets, Release notes.
- Enforce limits; see `references/app-store-metadata.md` or `scripts/check_app_store_limits.py`.

### Marketing copy pack

- Provide: 5-10 taglines, 3 hero sections (headline + subhead + CTA), 6 feature blurbs (1-2 sentences), 10 micro-CTAs, 10 ad hooks (short), 5 social posts.
- Keep claims supportable; avoid "#1 / best" unless proven.

### Screenshot pack (copy + prompts)

- Provide: 5-8 screenshot captions (2-5 words each) + optional sub-captions; include a narrative order (setup → value → proof → CTA).
- Provide: per-screenshot art direction + a prompt template for text-to-image generation (backgrounds/illustrations), tailored to the user's tool.
- Use `references/screenshot-prompts.md` for prompt patterns and negative prompts.

## Quality checks (do before final)

- Character limits: validate with `scripts/check_app_store_limits.py` for store fields.
- Consistency: keep the same core value prop across title/subtitle/hero/screenshot 1.
- Compliance: avoid disallowed claims, competitor trademarks, and sensitive targeting; ask if regulated domain (health/finance/kids).
- Readability: short sentences, active voice, scannable bullets.

## Common Pitfalls

### 1. ASO Keyword Stuffing (Unnatural, Hurts Conversion)

**Problem:** Cramming keywords into titles, subtitles, and descriptions makes copy sound robotic and kills conversion rates. App Store algorithms punish overloaded keyword copy in user engagement metrics.

**❌ Bad Example (iOS Subtitle):**
```
Photo Editor Photo Filter Photo Effects Photo Editor App
```

**✅ Good Example (iOS Subtitle):**
```
Professional photo editing, simplified
```

**Why it fails:**
- The bad version repeats "Photo" 4× and "Editor" 2×, signaling spam to both algorithms and users
- Reads unnaturally; users abandon apps that feel compromised
- App Store gives lower ranking boost to keyword-stuffed copy vs. naturally keyword-integrated copy

**What to do instead:**
- Each keyword appears **once naturally** in context
- Prioritize readability and user benefit over keyword density
- Let keywords live in distinct fields (keyword set, full description) where they don't disrupt the narrative
- Example that works: "Photo Editor-Professional Effects, Simplified" (keywords: photo editor, effects; reads naturally)

---

### 2. Generic Value Props (Could Apply to Any App)

**Problem:** Vague promises like "Fast," "Easy," "Simple," or "Best" don't differentiate and raise user skepticism. Without specificity, users can't judge if the app solves *their* problem.

**❌ Bad Examples:**
```
- "The easiest way to edit photos"
- "Powerful and intuitive design tool"
- "Professional-grade app for everyone"
- "The best photo editor on the market"
```

**✅ Good Examples (Specific):**
```
- "One-click background removal-no manual selection needed"
- "AI-powered portrait retouching in 3 taps"
- "Batch edit 100 photos with one template"
- "Remove objects without using expensive software like Photoshop"
```

**Why it matters:**
- Generic language applies to 50+ competitors; users skip it
- Specific claims signal you understand their workflow
- Specificity = trustworthiness; vague = greenwashing
- Good example contrasts against alternatives (Photoshop) users know

**What to do instead:**
- **Lead with outcome + mechanism**: "Auto-remove backgrounds in 2 seconds" (not "fast")
- **Show the job-to-be-done**: "Batch edit 100 photos" (not "powerful")
- **Contrast against status quo**: "No $20/month subscription" (not "affordable")
- **Name the user workflow**: "Retouch headshots for LinkedIn" (not "professional")

---

### 3. Store Listing Length Violations (Truncated on Store Pages)

**Problem:** Copy that exceeds field limits gets truncated mid-sentence, breaking the message and confusing users. Different platforms truncate at different character counts, and mobile displays show fewer characters than desktop.

**Platform Limits (Enforce Strictly):**
| Field | iOS | Google Play | Mobile Display |
|-------|-----|------------|-----------------|
| Subtitle | 30 chars | N/A | ✂️ Truncates at 30 on all devices |
| Short Description | N/A | 80 chars | ✂️ Truncates at 50 on mobile |
| Feature Bullets | N/A | 80 chars each | ✂️ Truncates at 50 on mobile |
| Promotional Text | 170 chars | N/A | ✂️ Truncates at 85 on mobile |

**❌ Bad Example (iOS Subtitle - 40 chars, exceeds 30-char limit):**
```
Professional photo editing, now simplified
```
**Displays as:** "Professional photo editing, now si..." (truncated mid-word)

**✅ Good Example (iOS Subtitle - 27 chars, fits perfectly):**
```
Professional photo editing
```

**❌ Bad Example (Google Play Feature Bullet - 95 chars, exceeds 80-char limit):**
```
Automatically remove backgrounds from any photo without manual selection or complicated tools
```
**Displays as:** "Automatically remove backgrounds from any photo without manual selection or..." (incomplete thought)

**✅ Good Example (Google Play Feature Bullet - 78 chars, fits with room):**
```
Auto-remove backgrounds in seconds-no manual selection needed
```

**What to do instead:**
- Always run copy through `scripts/check_app_store_limits.py` before final
- Write tight; avoid filler words (a, the, very, really, just)
- Prioritize the first 50 characters-everything after may be hidden on mobile
- Use contractions (don't, it's) to save characters without losing personality

---

### 4. Feature Bullets as Technical Specs (Not User Benefits)

**Problem:** Listing technical features instead of outcomes confuses users about what they can *do* with the app. Users don't buy specs; they buy results.

**❌ Bad Examples (Technical Specs):**
```
- Advanced color grading engine with 256-bit processing
- Support for RAW file formats (CR2, NEF, DNG)
- Multi-threaded rendering with GPU acceleration
- Compatible with iOS 14.0+ and requires 2GB RAM
```

**✅ Good Examples (User Benefits):**
```
- Make any photo look professional in one tap
- Edit RAW files on your phone (not just JPGs)
- Preview edits in real-time without lag
- Works on any recent iPhone or iPad
```

**Why it fails:**
- Technical language alienates casual users (your target)
- Users can't visualize the benefit ("256-bit processing"-so what?)
- Specs are checked *after* deciding to download, not before
- Example: "GPU acceleration" matters; "makes editing instant" is what users want

**The Translation Pattern:**
| Technical Spec | User Benefit |
|---|---|
| "EXIF data preservation" | "Keep photo location and date intact" |
| "32-bit color depth" | "Smooth gradients, no banding or color loss" |
| "Real-time collaborative editing" | "Edit with your team without emailing files back-and-forth" |
| "On-device processing (no cloud)" | "Your photos never leave your phone" |

**What to do instead:**
- **Start with the job**: What is the user trying to accomplish?
- **Translate feature → benefit**: "Supports 50+ filters" → "Dozens of professional styles, instantly"
- **Use "so that" test**: "Feature X, **so that** you can [benefit]" - if you can't complete it, it's not a benefit yet
- **Show before/after** in copy if possible: "Turn blurry photos into magazine-quality shots"

---

### 5. Missing Localization Considerations (Cultural Tone Issues)

**Problem:** Copy written for US English doesn't translate culturally to other markets. Phrases that work in English sound off, awkward, or even tone-deaf in other languages and regions. Keyword searches also vary by locale.

**❌ Bad Examples (US-Centric, Won't Translate Well):**
```
- "The #1 photo app" (claims don't work globally; also unverifiable)
- "Crush your creative goals" (aggressive tone doesn't translate; weird in Japanese/German)
- "Slay your edits" (slang; meaningless in translation; age-specific)
- "Our app rocks" (informal; risky in formal markets like Germany/Japan)
```

**✅ Good Examples (Culturally Neutral, Translates Well):**
```
- "The most popular photo editor" (verifiable, neutral tone)
- "Achieve professional results in seconds" (universal benefit, formal enough)
- "Make every photo beautiful" (simple, universal, translates directly)
- "Trusted by millions worldwide" (global signal, works everywhere)
```

**Common Localization Pitfalls:**

| Market | Don't | Do |
|--------|-------|-----|
| **Germany** | Aggressive slang ("crush," "slay") | Professional, clear ("achieve," "optimize") |
| **Japan** | Boastful claims ("best," "#1") | Humble confidence ("trusted by millions," "preferred by") |
| **Brazil** | Formal US English | Warm, conversational Portuguese (use native writer) |
| **France** | English marketing phrases | French alternatives (don't just translate) |
| **China/Asia** | Western idioms (sports metaphors) | Universal benefits without cultural references |

**Keyword Differences Across Regions:**
- US searches: "photo editor" (broad)
- Germany searches: "Fotobearbeitung" (more specific; use region-native keyword research)
- Japan searches: "写真編集" (completely different word choice needed)

**❌ Bad Approach:**
```
Write in US English → Translate to other languages → Done
```
(Loses cultural fit, tone, and keyword opportunity)

**✅ Good Approach:**
```
1. Write core value prop in neutral, translatable English
2. Have native speakers for each market adapt tone, keywords, and examples
3. Test keywords in each region's App Store search (not just Google)
4. Avoid slang, sports metaphors, US-specific references
5. Keep formal enough to work in risk-averse markets (Germany, Japan, Korea)
```

**What to do instead:**
- Write neutral English first (works for the world)
- Flag words/phrases that will need cultural adaptation ("#1," slang, US idioms)
- For each locale: hire a native speaker to refine tone and keywords, not just translate
- Keep tone at "professional confidence" level (works across cultures)
- A/B test different tones in each market if feasible

---

## Troubleshooting

### Issue: Character Limit Errors After Generation

**Symptoms:** Copy looks great but exceeds App Store/Play Store field limits

**Solution:**
```bash
# Validate all fields at once
python scripts/check_app_store_limits.py input.json

# Input format
{
  "platform": "ios",  // or "google_play"
  "app_name": "YourApp",
  "subtitle": "Your subtitle text",
  "description": "Full description...",
  "keywords": "keyword,list,comma,separated"
}
```

**Quick fixes:**
- iOS subtitle (30 chars): Remove articles (a, the), use contractions
- Google Play short desc (80 chars): Lead with strongest benefit
- Keywords (100 chars iOS): Remove low-value keywords, use abbreviations

### Issue: Generic/Bland Copy Despite Good Input

**Symptoms:** Generated copy sounds like every other app

**Cause:** Missing specific differentiators or proof points

**Solution:**
1. Ask user: "What's one thing your app does that competitors don't?"
2. Ask for numbers: "How many users? How much time saved?"
3. Find the contrast: "What do users do today that sucks?"
4. Example transform:
   - Before: "Easy photo editing for everyone"
   - After: "Remove backgrounds in 2 taps—no Photoshop subscription"

### Issue: Unclear Which Deliverables to Produce

**Symptoms:** User says "help with app marketing" without specifics

**Solution:**
Present checklist and ask what they need:
- [ ] iOS App Store listing
- [ ] Google Play listing
- [ ] Landing page hero copy
- [ ] Screenshot captions
- [ ] Social media ad hooks
- [ ] Email campaign copy

Then produce only requested items.

### Issue: Keyword Stuffing Creeping Back In

**Symptoms:** Copy passes limits but sounds unnatural

**Cause:** Trying to maximize keyword density

**Solution:**
- Read copy aloud—if it sounds robotic, remove keywords
- Each keyword should appear max 2× in subtitle+description combined
- Use `scripts/check_app_store_limits.py` for length, but manually review readability
- Ask: "Would a human actually say this?"

### Issue: Missing References or Scripts

**Symptoms:** Skill mentions `references/` or `scripts/` files that don't exist

**Solution:**
1. Check if files exist: `ls skills/app-marketing-copy/references/`
2. If missing, proceed without them:
   - Use inline limits instead of `app-store-metadata.md`
   - Manually validate character counts instead of running scripts
3. Recommend to user: "For automated validation, create `scripts/check_app_store_limits.py`"

## Included resources

- `references/app-store-metadata.md`: field map + common limits + output skeletons.
- `references/screenshot-prompts.md`: prompt templates for backgrounds and promo visuals.
- `scripts/check_app_store_limits.py`: quick character-limit checker for iOS/Google Play fields (JSON in, table out).
