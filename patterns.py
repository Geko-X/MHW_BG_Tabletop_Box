
import glowbit
import time
import random

import asyncio

def lerp(a, b, t):
	return a + (b - a) * t

def lerp_int(a, b, t):
	return (int)(lerp(a, b, t))

def lerp_color(stick: glowbit.stick, a, b, t):
	c1 = stick.glowbitColour2RGB(a)
	c2 = stick.glowbitColour2RGB(b)
	
	c3 = (lerp_int(c1[0], c2[0], t),
		  lerp_int(c1[1], c2[1], t),
		  lerp_int(c1[2], c2[2], t)
		)
	
	return stick.rgbColour(c3[0], c3[1], c3[2])

def fade(stick: glowbit.stick, start_color: int, end_color: int, fade_time = 0.5):
    
    ticks = fade_time * stick.rateLimit
    
    for t in range(ticks):
        perc = (float)(t) / ticks
        c = lerp_color(stick, start_color, end_color, perc)
        stick.pixelsFill(c)
        stick.pixelsShow()

# Loops single pixel
def loop_pixel(stick: glowbit.stick, color: int, loops: int, offset = 0, dir: int = 1, fps: int = 60, base_color = 0):
    
    _fps = stick.rateLimit;
    stick.updateRateLimitFPS(fps)
    if base_color == 0:
        stick.blankDisplay()
    else:
        stick.pixelsFill(base_color)
    
    if(dir == 1):
        start = 0
        end = stick.numLEDs
  
    else:
        start = stick.numLEDs - 1
        end = 0

    for x in range(loops):
        for i in range(start, end, dir):
            if base_color == 0:
                stick.blankDisplay()
            else:
                stick.pixelsFill(base_color)
            
            pID = (i + offset) % (stick.numLEDs - 1)
            
            stick.pixelSet(pID, color)
            stick.pixelsShow()
    
    stick.updateRateLimitFPS(_fps)
    if base_color == 0:
        stick.blankDisplay()
    else:
        stick.pixelsFill(base_color)

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
        loop_pixel(stick, c, 0, 1)

# Ping pongs a pixel
def ping_pong(stick: glowbit.stick, color: int, count: int, start_dir: int = 1, fps: int = 60):
    for c in range(count * 2):
        loop_pixel(stick, color, 0, 1, start_dir, fps)
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

def color_burst(stick: glowbit.stick, color, fade_in = 0.5, duration = 1, fade_out = 2):
    _c = stick.getPixel(0)
    _c2 = lerp_color(stick, _c, 0, 0.5)
    fade(stick, _c, _c2)
    fade(stick, _c2, color, fade_in)
    time.sleep(duration)
    fade(stick, color, _c, fade_out)

def scoutfly(stick: glowbit.stick, start_color = 0x001100, fly_colour = 0xFFFF00):
    
    _c = stick.getPixel(0)
    fade(stick, _c, start_color)
    
    offset = random.randint(0, stick.numLEDs - 1)
    for i in range(3):
        loop_pixel(stick, fly_colour, 1, offset,
                   dir = 1 if ((offset + 1) % 2 == 0) else -1,
                   fps = (i + 1) * 50,
                   base_color = start_color
                )
    color_burst(stick, fly_colour)
    fade(stick, start_color, _c)

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
        time.sleep(delay)
        
def tziti_flash(stick: glowbit.stick):
    
    _c = stick.getPixel(0)
    fade(stick, _c, 0)
    time.sleep(0.5)
    
    flash(stick, brightness = 150, flash_time = 0.2, count = 2)
    time.sleep(0.8)
    flash(stick, brightness = 150, flash_time = 1)
    
    fade(stick, 0, _c)

def invasion(stick: glowbit.stick):
    _c = stick.getPixel(0)
    _b = stick.brightness
    fade(stick, _c, 0)
    #time.sleep(0.5)
    #flash(stick, stick.red(), brightness = 200, flash_time = 0.6, count = 10, delay = 0.6)
    
    stick.brightness = 250

    for i in range(5):
        fade(stick, stick.black(), stick.red(), 0.1)
        time.sleep(0.54)
        fade(stick, stick.red(), stick.black(), 0.1)
        time.sleep(0.54)

    stick.brightness = _b
    fade(stick, 0, _c)

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
        