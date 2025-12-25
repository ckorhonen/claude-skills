# Designing for Playdate (Notes)

## Contents
- Screen and graphics
- Text and fonts
- Rendering scale and transforms
- Refresh rate and performance
- Sound
- Input and accessibility
- UI and system affordances
- Launcher metadata and assets

## Screen and graphics
- Screen is 400 x 240 pixels at 173 ppi; pixels are small for the physical size.
- No backlight; screen is reflective and looks best in bright light.
- Black bezel is about 3 mm; edge-to-edge art can blend into the bezel.
- Physical center line is offset: x = 228 aligns with the Playdate centerline.
- Player sprite readability: around 32 x 32 pixels is a reasonable minimum.
- Tiles: avoid tiny tiles like 8 x 8; 32 x 32 is comfortable; power-of-2 tiles are easier to author.

## Text and fonts
- Dialog text: cap height at least 12 px, preferably 14 px.
- HUD text: can go down to 10 px; absolute minimum is 8 px.
- Use clear shapes and strong contrast; strokes should be at least 2 px thick.
- Compare font size against printed text; if it is smaller than book text, it is likely too small.
- System UI uses Roobert 20 and 24 (SDK resources); Asheville 14 indicates a font loading error.

## Rendering scale and transforms
- 2x scale can improve readability; use `playdate.display.setScale()`.
- Font design at 2x needs special care to stay legible.
- Runtime rotation or scaling is CPU-heavy (no GPU); pre-render rotated assets when possible.
- Use image tables and touch up converted art to reduce noise.

## Refresh rate and performance
- Default refresh rate is 30 fps; 20 fps can be ok for low-motion games.
- Max refresh rate is 50 fps; frame time shrinks by 40 percent and battery can suffer.
- Consider lower refresh rate for static or turn-based games.

## Sound
- Audio supports 44.1 kHz; test on device and with headphones.
- Normalize levels so your game does not feel louder or quieter than others.
- Provide subtitles or visual cues for sound effects and dialog.
- Warn players if audio is required for gameplay.

## Input and accessibility
- Crank + button: B is often more comfortable than A when cranking.
- If crank is used, map d-pad or button alternatives when possible.
- Buttons in menus: A confirms, B cancels or goes back.
- Allow more than one input for essential actions (A, B, d-pad, crank).
- Accelerometer is 3-axis only; provide calibration if tilt is used.

## UI and system affordances
- Use `playdate.ui.crankIndicator` when crank input is required.
- Keep on-screen keyboard use short; long text entry can feel slow.
- Use QR codes for long URLs and display the text URL too.

## Launcher metadata and assets
- Provide accurate `pdxinfo` metadata (name, version, buildNumber).
- buildNumber must increase for every public release and for sideload updates.
- Launcher card has no label; include the game name in the image.
- Asset sizes:
  - card-pressed.png: 350 x 155
  - icon-pressed.png: 32 x 32
  - wrapping-pattern.png: 400 x 240
