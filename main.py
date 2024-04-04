from machine import Pin, Timer, PWM, SPI, ADC
import time
import max7219_8digit as seg
import glowbit

from pico_constants import *

UPDATES_PER_SECOND = 10
SLEEP_TIME = 1 / UPDATES_PER_SECOND

# Main LED

led = Pin(PIN_LED, Pin.OUT)
timer = Timer()

# Potentiometers

pot_0 = ADC(PIN_ADC_0)
pot_1 = ADC(PIN_ADC_1)

# 7-Seg

seg_data = Pin(PIN_SEG_DISPLAY_DATA)
seg_clock = Pin(PIN_SEG_DISPLAY_CLOCK)
seg_cs = Pin(PIN_SEG_DISPLAY_CS, Pin.OUT)

DISPLAY_INTESITY = 0

spi = SPI(0, baudrate=10000000, polarity=1, phase=0, sck = seg_clock, mosi = seg_data)
display = seg.Display(spi, seg_cs, DISPLAY_INTESITY)

# Glowbit
GLOWBIT_PIN = 18
GLOWBIT_SIZE = 16
GLOWBIT_BRIGHTNESS = 8
GLOWBIT_FPS = 30

stick = glowbit.stick(
    pin = GLOWBIT_PIN,
    numLEDs = GLOWBIT_SIZE,
    brightness = GLOWBIT_BRIGHTNESS,
    rateLimitFPS = GLOWBIT_FPS
)

# Buttons
button_1 = Pin(PIN_INPUT_1, Pin.IN, Pin.PULL_UP)

'''
======== HELPERS ========
'''

def normalise_value(value, max = 1):
	return value / max

def lerp(a, b, t):
    return a + (b - a) * t

def lerp_int(a, b, t):
    return (int)(lerp(a, b, t))

def lerp_color(a, b, t):
    c1 = stick.glowbitColour2RGB(a)
    c2 = stick.glowbitColour2RGB(b)
    
    c3 = (lerp_int(c1[0], c2[0], t),
          lerp_int(c1[1], c2[1], t),
          lerp_int(c1[2], c2[2], t)
        )
    
    return stick.rgbColour(c3[0], c3[1], c3[2])

'''
======== HARDWARE ========
'''

# Main LED
def blink(timer):
    led.toggle()

def read_pot_normalised(pot): 
    value = 1 - normalise_value(pot.read_u16(), 65535)
    return round(value, 2)

def read_pot_as_range(pot, max):
    return round(read_pot_normalised(pot) * max)

def write_7seg_display(msg):
    display.write_to_buffer(str(msg))

'''
======== GAME ========
'''

GAME_PLAYERS_MAX = 4
GAME_CARDS_MAX = 8

GAME_TIME_START = 35

def format_players(count):
    return "P" + str(count)

def format_cards(count):
	return "C" + str(count)

def format_display(players, cards):
	return ("%-4s" % format_players(players)) + ("%-4s" % format_cards(cards))

'''
======== GLOWBIT ========
'''

graph = stick.newGraph1D(0, GLOWBIT_SIZE - 1, 0, GAME_TIME_START, stick.red(), "Solid", True)

'''
======== MAIN ========
'''

def button_callback(p: Pin):
    
    if(p.value() == 0):
        led.value(1)
        
    else:
        led.value(0)
        
def button_callback_toggle(p: Pin):
    led.toggle()

def init():
    # Start main LED blink
    #timer.init(freq=1, mode=Timer.PERIODIC, callback=blink)
    write_7seg_display(' ')
    
    stick.chaos(5)
    stick.blankDisplay()

    button_1.irq(handler = button_callback_toggle, trigger = Pin.IRQ_RISING)

def main():
    
    gameTimeCurrent = GAME_TIME_START
    
    while True:
        time.sleep(SLEEP_TIME)

        players = read_pot_as_range(pot_0, GAME_PLAYERS_MAX)
        cards = read_pot_as_range(pot_1, GAME_CARDS_MAX)
        
        # s = game.format_display(value, value)
        # print(s)
        
        write_7seg_display(format_display(players, cards))
        
        display.display()

        gameTimeCurrent = gameTimeCurrent - 1
        if(gameTimeCurrent <= 0):
            gameTimeCurrent = GAME_TIME_START
        
        c = lerp_color(stick.red(), stick.green(), gameTimeCurrent / GAME_TIME_START)
        graph.colour = c  
        stick.updateGraph1D(graph, gameTimeCurrent)
        
init()
main()