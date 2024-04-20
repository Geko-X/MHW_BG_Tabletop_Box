
import glowbit
import time

import asyncio

# Loops single pixel
def loop_pixel(stick: glowbit.stick, color: int, loops: int, dir: int = 1, fps: int = 60):
    
    _fps = stick.rateLimit;
    stick.updateRateLimitFPS(fps)
    stick.blankDisplay()
    
    if(dir == 1):
        start = 0
        end = stick.numLEDs
  
    else:
        start = stick.numLEDs - 1
        end = 0

    for x in range(loops):
        for i in range(start, end, dir):
            stick.blankDisplay()
            stick.pixelSet(i, color)
            stick.pixelsShow()
    
    stick.updateRateLimitFPS(_fps)
    stick.blankDisplay()

async def loop_pixel_async(stick: glowbit.stick, color: int, loops: int, dir: int = 1, fps: int = 60):
    
    _fps = stick.rateLimit;
    stick.updateRateLimitFPS(fps)
    stick.blankDisplay()
    
    if(dir == 1):
        start = 0
        end = stick.numLEDs
  
    else:
        start = stick.numLEDs - 1
        end = 0

    for x in range(loops):
        for i in range(start, end, dir):
            await asyncio.sleep(0)
            stick.blankDisplay()
            stick.pixelSet(i, color)
            stick.pixelsShow()
    
    stick.updateRateLimitFPS(_fps)
    stick.blankDisplay()

# Loops but also does colours
def loop_with_colors(stick: glowbit.stick, colors, loops: int, dir: int = 1, fps: int = 60):
    for x in range(loops):
        c = colors[x % len(colors)]
        loop_pixel(stick, c, 1)

# Ping pongs a pixel
def ping_pong(stick: glowbit.stick, color: int, count: int, start_dir: int = 1, fps: int = 60):
    for c in range(count * 2):
        loop_pixel(stick, color, 1, start_dir, fps)
        start_dir *= -1
        
# Breathe function
def breath(stick: glowbit.stick, color: int, count: int = 5, change = 0.025, fps: int = 100):
    stick.updateRateLimitFPS(fps)
    stick.blankDisplay()

    max_brightness = stick.brightness
    min_brightness = 2
    stick.pixelsFill(color)
    dir = 1
    b = min_brightness

    stick.updateBrightness(min_brightness)
    stick.pixelsShow()
 
    x = count * 2
    while(x > 0):
        b = b + (change * dir)
        if((b <= min_brightness) or (b >= max_brightness)):
            dir = dir * -1
            x = x - 1
        
        _b = ((b / max_brightness) * 255) / max_brightness
        
        stick.updateBrightness(_b)
        stick.pixelsShow()

def intensify(stick: glowbit.stick, count: int = 5, fps: int = 100):
    stick.updateRateLimitFPS(fps)
    stick.blankDisplay()

    r = 0
    x = count
    while(x > 0):
        r = r + 1
        if(r > 255):
            r = 0
            x = x - 1
        
        c = (r << 16) + (r << 8) + r
        stick.pixelsFillNow(c)

def flash(stick: glowbit.stick, color = 0xEAE347, brightness = 50, flash_time = 0.5, count = 1, delay = 0.2):   
    stick.blankDisplay()
    stick.pixelsShow()

    stick.pixelsFill(color)
    stick.updateBrightness(brightness / 2)
    
    ticks = flash_time * stick.rateLimit
    
    for _ in range(count):
        b_delta = stick.brightness / ticks
        b = stick.brightness
        
        for t in range(ticks):
            b = b - b_delta
            if b <= 1: b = 0
            
            stick.updateBrightness(b)
            stick.pixelsShow()
            
        stick.updateBrightness(brightness / 2)
        time.sleep(0.2)
        

def tziti_flash(stick: glowbit.stick):
    stick.blankDisplay()
    stick.pixelsShow()
    time.sleep(0.5)
    
    flash(stick, brightness = 40, flash_time = 0.2, count = 2)
    time.sleep(0.8)
    flash(stick, brightness = 75, flash_time = 1)

# Main
def patterns_test(stick: glowbit.stick):
    
    #tziti_flash(stick)
    
    colors = [stick.red(), stick.green(), stick.blue(), stick.white(), stick.yellow(), stick.cyan(), stick.cyan()]
    c = 0
    while(True):
        color = colors[c % len(colors)]
        c += 1
        ping_pong(stick, color, 2, 1)
        loop_with_colors(stick, colors, 10, fps = 200)
        stick.brightness = 5
        breath(stick, color, 2)
        intensify(stick, 2)
        