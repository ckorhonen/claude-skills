---
name: playdate-dev
description: Playdate game development in Lua with the Playdate SDK. Covers game loop, sprites, graphics, input (crank, buttons, accelerometer), audio, UI, performance, metadata (pdxinfo), and simulator/device workflow. Use when asked to make a Playdate game, implement Playdate-specific mechanics, or apply Playdate design and accessibility guidelines.
---

# Playdate Dev

## Overview

Build Playdate games in Lua using the official Playdate SDK. The Playdate is a small yellow handheld with a 400×240 1-bit display, a physical crank, A/B buttons, and a D-pad. Understanding its constraints and unique input is essential.

**Hardware specs:**
- Display: 400×240 pixels, 1-bit (black/white only)
- Memory: ~16 MB RAM (aim for <8 MB peak usage)
- CPU: 180 MHz Cortex-M7 (device is slower than simulator — always profile on hardware)
- Input: A button, B button, D-pad (up/down/left/right), crank, menu button
- Audio: 44.1kHz stereo, Synth + SamplePlayer APIs
- Accelerometer: 3-axis, opt-in to save battery

## Quick Start Workflow

1. Clarify the request scope (gameplay goal, target device vs simulator, SDK version, release vs prototype).
2. Choose inputs and accessibility (buttons, crank, accelerometer; provide non-crank alternatives; respect reduce-flashing setting).
3. Choose rendering approach (sprites vs immediate draw, image sizes, refresh rate, 1x vs 2x scale).
4. Implement the core loop (define `playdate.update()`, update game state, call `playdate.graphics.sprite.update()` and `playdate.timer.updateTimers()` when used).
5. Add metadata and launcher assets (`pdxinfo`, buildNumber, launcher card and icon sizes).
6. Test in the Simulator and on hardware (screen legibility, crank feel, audio balance, performance).

## Starter Project

- Copy `assets/lua-starter` into a new project folder.
- Keep `Source/main.lua` and `Source/pdxinfo` in the source root.
- Replace placeholder values in `pdxinfo` and extend the update loop.

Build with:
```bash
pdc Source GameName.pdx      # compile to .pdx bundle
# Then open GameName.pdx in the Simulator, or drag to device
```

## Core Game Loop

```lua
-- main.lua
import "CoreLibs/object"
import "CoreLibs/graphics"
import "CoreLibs/sprites"
import "CoreLibs/timer"

local gfx <const> = playdate.graphics

-- Game state
local playerX, playerY = 200, 120

function playdate.update()
    -- 1. Handle input
    if playdate.buttonIsPressed(playdate.kButtonLeft) then
        playerX -= 2
    elseif playdate.buttonIsPressed(playdate.kButtonRight) then
        playerX += 2
    end

    -- 2. Handle crank
    local crankDelta = playdate.getCrankChange()  -- degrees since last update
    playerY += crankDelta * 0.1                    -- map crank to movement

    -- 3. Update sprites and timers (required each frame if used)
    gfx.sprite.update()
    playdate.timer.updateTimers()

    -- 4. Draw (if not using sprites)
    gfx.clear()
    gfx.fillCircleAtPoint(playerX, playerY, 10)
end
```

## Input API

### Buttons

```lua
-- Check if button is held this frame
playdate.buttonIsPressed(playdate.kButtonA)
playdate.buttonIsPressed(playdate.kButtonB)
playdate.buttonIsPressed(playdate.kButtonUp)
playdate.buttonIsPressed(playdate.kButtonDown)
playdate.buttonIsPressed(playdate.kButtonLeft)
playdate.buttonIsPressed(playdate.kButtonRight)

-- Single-frame press/release events
local pressed, released = playdate.getButtonState()
if pressed & playdate.kButtonA ~= 0 then
    -- A was pressed this frame
end

-- Callbacks (simpler for menu-style code)
function playdate.AButtonDown()
    -- A pressed
end
function playdate.AButtonUp()
    -- A released
end
```

### Crank

```lua
-- Angle in degrees (0-359.99, clockwise = positive)
local angle = playdate.getCrankPosition()

-- Delta since last frame (positive = clockwise)
local delta = playdate.getCrankChange()

-- Detect if crank is docked (folded away)
if playdate.isCrankDocked() then
    -- Show "pull out crank" hint or use button fallback
end

-- Request dock/undock alerts
playdate.setCrankSoundsDisabled(true)  -- suppress built-in clicks
```

### Accelerometer

```lua
-- Must opt-in (saves battery when off)
playdate.startAccelerometer()

-- Read in update()
local x, y, z = playdate.readAccelerometer()
-- x,y,z each in range ~[-1, 1] (1G = 1.0)
-- x: tilt left/right, y: tilt front/back, z: up/down

-- Remember to stop when not needed
playdate.stopAccelerometer()
```

## Graphics

### Drawing Modes

```lua
local gfx <const> = playdate.graphics

-- Screen is black (0) and white (1) only
gfx.setColor(gfx.kColorBlack)  -- or kColorWhite, kColorClear, kColorXOR
gfx.setImageDrawMode(gfx.kDrawModeFillBlack)  -- for rendering images

-- Immediate drawing (clears each frame)
function playdate.update()
    gfx.clear(gfx.kColorWhite)  -- clear to white
    gfx.drawRect(10, 10, 100, 50)
    gfx.fillRect(20, 20, 80, 30)
    gfx.drawLine(0, 0, 400, 240)
    gfx.drawCircleAtPoint(200, 120, 40)
    gfx.fillCircleAtPoint(200, 120, 40)
    gfx.drawText("Hello Playdate!", 10, 10)
end
```

### Images

```lua
-- Load from .png file (must be in Source/)
local img = gfx.image.new("images/player")  -- no extension needed

-- Draw image
img:draw(x, y)
img:drawCentered(x, y)

-- Flip/transform
img:draw(x, y, gfx.kImageFlippedX)

-- Image tables (sprite sheets)
local table = gfx.imagetable.new("images/walk")  -- walk-table-32-32.png format
local frame = table:getImage(frameIndex)  -- 1-indexed
```

### Fonts and Text

```lua
-- System fonts
local font = gfx.font.new("fonts/Roobert-10-Bold")  -- SDK includes several
gfx.setFont(font)
gfx.drawText("Score: " .. score, 10, 10)

-- Centered text
gfx.drawTextInRect("Hello!", 0, 100, 400, 30, nil, nil, kTextAlignment.center)
```

### Sprite System

```lua
-- Create sprite
local playerSprite = gfx.sprite.new()
playerSprite:setImage(gfx.image.new("images/player"))
playerSprite:moveTo(200, 120)
playerSprite:setZIndex(10)
playerSprite:add()  -- add to sprite list

-- Custom sprite class (OOP pattern)
class('Player').extends(gfx.sprite)

function Player:init()
    Player.super.init(self)
    self:setImage(gfx.image.new("images/player"))
    self:add()
end

function Player:update()
    if playdate.buttonIsPressed(playdate.kButtonRight) then
        self:moveBy(2, 0)
    end
end

-- In playdate.update():
gfx.sprite.update()  -- required every frame
```

### Collision Detection (via Sprites)

```lua
-- Set collision rect
playerSprite:setCollideRect(0, 0, playerSprite:getSize())

-- Query collisions after move
local actualX, actualY, cols, len = playerSprite:moveWithCollisions(newX, newY)

-- Collision response
for i = 1, len do
    local col = cols[i]
    print("Hit:", col.other:getTag())  -- other sprite's tag
end
```

## Audio

```lua
-- Sample playback
local sfx = playdate.sound.sampleplayer.new("sounds/jump")  -- .wav or .aif
sfx:play()

-- Background music (loops by default)
local music = playdate.sound.fileplayer.new("sounds/bgm")
music:play(0)  -- 0 = loop forever
music:setVolume(0.7)

-- Synthesizer (procedural audio)
local synth = playdate.sound.synth.new(playdate.sound.kWaveformSquare)
synth:setFrequency(440)
synth:setVolume(0.5)
synth:playNote("A4", 0.5, 0.25)  -- note, volume, duration
```

## Timers

```lua
import "CoreLibs/timer"

-- One-shot timer (fires after 2000ms)
playdate.timer.performAfterDelay(2000, function()
    print("Two seconds passed!")
end)

-- Repeating timer
local t = playdate.timer.new(500, function()
    -- fires every 500ms
end)
t.repeats = true

-- Value timer (lerp a value over time)
local vt = playdate.timer.new(1000, 0, 100)  -- 1000ms, from 0 to 100
-- In update: use vt.value

-- IMPORTANT: Must call every frame
playdate.timer.updateTimers()
```

## pdxinfo Metadata

```ini
# Source/pdxinfo (required)
name=My Game
author=Your Name
description=A short game description
bundleID=com.yourname.mygame
version=1.0.0
buildNumber=1
imagePath=images/
launchSoundPath=sounds/launch
contentWarning=Contains flashing lights
```

Required launcher assets (put in `images/` or configured `imagePath`):
- `launcher/card.png` — 350×155 pixels
- `launcher/card~highlight.png` — 350×155 pixels (highlighted state)
- `launcher/icon.png` — 32×32 pixels
- `launcher/icon~highlight.png` — 32×32 pixels

## Performance Tips

- **Target 30fps** on device (50fps max, but 30fps is standard)
- **Limit `gfx.clear()`** — use `gfx.sprite.update()` dirty-rect rendering instead
- **Prefer sprite system** for moving objects; avoids full-screen redraws
- **Pool objects** — avoid creating new tables/objects every frame
- **Use `playdate.display.setRefreshRate(30)`** if 50fps isn't needed
- **Profile on device** — Simulator is 2-3x faster than hardware

```lua
-- Check frame time
playdate.display.setRefreshRate(30)

-- Draw FPS overlay (for profiling)
playdate.drawFPS(0, 0)
```

## Accessibility

```lua
-- Respect "Reduce Flashing" system setting
if playdate.getReduceFlashing() then
    -- Avoid strobing effects, use slower transitions
end

-- Always provide button fallback for crank actions
if playdate.isCrankDocked() then
    showCrankHint = false  -- hide crank UI hints
    -- Let D-pad substitute for crank
end
```

## Crank UI Indicators

```lua
import "CoreLibs/ui"

-- Show built-in crank indicator (hint to pull out crank)
local crankIndicator = playdate.ui.crankIndicator

function playdate.update()
    if playdate.isCrankDocked() then
        crankIndicator:draw()  -- draws in corner
    end
end
```

## Menu Integration

```lua
-- Add items to the system pause menu
local menu = playdate.getSystemMenu()

-- Checkmark toggle
local soundItem, err = menu:addCheckmarkMenuItem("Sound", true, function(value)
    soundEnabled = value
end)

-- Options list
local diffItem, err = menu:addOptionsMenuItem("Difficulty", {"Easy","Normal","Hard"}, "Normal", function(value)
    difficulty = value
end)
```

## Save/Load Data

```lua
-- Simple key-value store (persists between sessions)
-- Save
local data = {score = 1234, level = 5}
playdate.datastore.write(data)

-- Load
local data = playdate.datastore.read()
if data then
    score = data.score or 0
end

-- Delete save
playdate.datastore.delete()
```

## Common Patterns

### Scene Management

```lua
-- Simple scene switcher
local currentScene = nil

function switchScene(newScene)
    if currentScene and currentScene.leave then
        currentScene:leave()
    end
    gfx.sprite.removeAll()
    currentScene = newScene
    if currentScene.enter then
        currentScene:enter()
    end
end

-- Define scenes as tables
local titleScene = {}
function titleScene:enter() ... end
function titleScene:update() ... end

-- In playdate.update():
function playdate.update()
    if currentScene and currentScene.update then
        currentScene:update()
    end
    gfx.sprite.update()
    playdate.timer.updateTimers()
end
```

### Crank-Driven Mechanic

```lua
-- Accumulate crank ticks for grid-based movement
local TICKS_PER_STEP = 12  -- degrees per step

local crankAccumulator = 0

function playdate.update()
    local delta = playdate.getCrankChange()
    crankAccumulator += delta

    while crankAccumulator >= TICKS_PER_STEP do
        crankAccumulator -= TICKS_PER_STEP
        moveRight()
    end
    while crankAccumulator <= -TICKS_PER_STEP do
        crankAccumulator += TICKS_PER_STEP
        moveLeft()
    end

    -- Button fallback (for docked crank)
    if playdate.buttonJustPressed(playdate.kButtonLeft) then moveLeft() end
    if playdate.buttonJustPressed(playdate.kButtonRight) then moveRight() end
end
```

## Resources

- `references/designing-for-playdate.md` — Screen, text, input, audio, UI, launcher guidance
- `references/inside-playdate-lua.md` — Full Lua API names, file layout, workflow details
- `assets/lua-starter/` — Starter project template
- [Official SDK Docs](https://sdk.play.date/Inside%20Playdate.html) — Authoritative Lua API reference
- [SDK Download](https://play.date/dev/) — Free from Panic
- [Playdate Developer Forum](https://devforum.play.date/) — Community Q&A and examples
