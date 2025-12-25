# Inside Playdate (Lua Notes)

## Contents
- Project layout and build
- Core loop and timing
- Input: buttons, crank, accelerometer
- Sprites and graphics
- Timers and animation
- UI, keyboard, and menu
- Metadata and launcher
- Debugging and performance

## Project layout and build
- Put Lua sources under `Source/` with a `main.lua` entrypoint.
- If a `pdxinfo` file exists at the root of the source directory, the system uses it.
- PNG and GIF images in the source folder are compiled by `pdc` and load via `playdate.graphics.image.new(path)`.
- Import CoreLibs as needed:
  - `CoreLibs/graphics`, `CoreLibs/sprites`, `CoreLibs/timer`, `CoreLibs/ui`, `CoreLibs/keyboard`, `CoreLibs/crank`

## Core loop and timing
- Implement `playdate.update()`; OS calls it once per frame (default 30 fps).
- Change the rate with `playdate.display.setRefreshRate()`.
- `playdate.update()` runs as a coroutine; you can `coroutine.yield()` for long tasks.
- Use `playdate.wait(ms)` to pause update callbacks; audio continues.
- Use `playdate.start()` and `playdate.stop()` to resume or stop per-frame callbacks.

## Input: buttons, crank, accelerometer
- Buttons: `playdate.buttonIsPressed(playdate.kButtonUp)` (and Left, Right, Down).
- Held callbacks: `playdate.AButtonHeld()` and `playdate.BButtonHeld()` after 1 second.
- Upside Down setting flips d-pad directions; check `playdate.getFlipped()`.
- Crank state:
  - `playdate.isCrankDocked()`
  - `playdate.getCrankPosition()`
  - `playdate.getCrankChange()` (returns change and acceleratedChange)
  - `playdate.getCrankTicks(ticksPerRevolution)` (requires `CoreLibs/crank`)
  - Callbacks: `playdate.cranked(change, acceleratedChange)`, `playdate.crankDocked()`, `playdate.crankUndocked()`
  - Optional: `playdate.setCrankSoundsDisabled(true)`
- Accelerometer:
  - `playdate.startAccelerometer()` and `playdate.stopAccelerometer()`
  - `playdate.readAccelerometer()` returns x, y, z
  - `playdate.accelerometerIsRunning()`

## Sprites and graphics
- Create sprites with `playdate.graphics.sprite.new(image)`.
- Add sprites to the display list with `sprite:add()`.
- Update all sprites each frame with `playdate.graphics.sprite.update()`.
- Avoid confusing `sprite:update()` (one sprite) with `sprite.update()` (all sprites).
- Use `playdate.graphics.sprite:setBackgroundDrawingCallback()` for static backgrounds.
- Create images at runtime:
  - `playdate.graphics.image.new(width, height, [bgcolor])`
  - Draw into images with `playdate.graphics.pushContext(image)` / `playdate.graphics.popContext()`

## Timers and animation
- Call `playdate.timer.updateTimers()` each frame when using timers.
- Call `playdate.frameTimer.updateTimers()` when using frame timers.
- Use `playdate.timer.keyRepeatTimer()` for repeated input actions.

## UI, keyboard, and menu
- Crank indicator (requires `CoreLibs/ui`):
  - `playdate.ui.crankIndicator:draw()` inside `playdate.update()`
  - Call after `playdate.graphics.sprite.update()` if using sprites.
- Grid view (requires `CoreLibs/ui`): `playdate.ui.gridview` uses timers internally.
- Keyboard (requires `CoreLibs/keyboard`):
  - `playdate.keyboard.show([text])`, `playdate.keyboard.hide()`
  - Keyboard works at 1x scale only.
- System menu:
  - `playdate.getSystemMenu()`
  - `menu:addMenuItem`, `menu:addCheckmarkMenuItem`, `menu:addOptionsMenuItem`
  - Max 3 custom menu items.
  - `playdate.setMenuImage(image, [xOffset])` (left 200 px is visible when menu shows).

## Metadata and launcher
- `playdate.metadata` mirrors values from `pdxinfo` (example: `playdate.metadata.version`).
- `buildNumber` must increase for every public release and for sideload updates.

## Debugging and performance
- Debug helpers: `playdate.drawFPS()`, `playdate.debugDraw()`, `printTable()`.
- Simulator-only keys: `playdate.keyPressed(key)`, `playdate.keyReleased(key)`.
- Garbage collection tuning:
  - `playdate.setCollectsGarbage(flag)`
  - `playdate.setMinimumGCTime(ms)`
  - `playdate.setGCScaling(min, max)`
