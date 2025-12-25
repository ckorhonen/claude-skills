import "CoreLibs/object"
import "CoreLibs/graphics"
import "CoreLibs/sprites"
import "CoreLibs/timer"

local gfx <const> = playdate.graphics

local playerSprite = nil
local speed = 2

local function makePlayerImage()
  local image = gfx.image.new(20, 20)
  gfx.pushContext(image)
  gfx.setColor(gfx.kColorBlack)
  gfx.fillRect(2, 2, 16, 16)
  gfx.popContext()
  return image
end

local function setup()
  local playerImage = makePlayerImage()
  playerSprite = gfx.sprite.new(playerImage)
  playerSprite:moveTo(200, 120)
  playerSprite:add()
end

setup()

function playdate.update()
  if playdate.buttonIsPressed(playdate.kButtonUp) then
    playerSprite:moveBy(0, -speed)
  end
  if playdate.buttonIsPressed(playdate.kButtonRight) then
    playerSprite:moveBy(speed, 0)
  end
  if playdate.buttonIsPressed(playdate.kButtonDown) then
    playerSprite:moveBy(0, speed)
  end
  if playdate.buttonIsPressed(playdate.kButtonLeft) then
    playerSprite:moveBy(-speed, 0)
  end

  gfx.sprite.update()
  playdate.timer.updateTimers()
end
