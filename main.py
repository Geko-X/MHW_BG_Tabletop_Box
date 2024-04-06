from debounce import DebouncedSwitch
from machine import Pin, Timer, PWM, SPI, ADC
import time
import max7219_8digit as seg
import glowbit

from pico_constants import *

UPDATES_PER_SECOND = 100
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
button_time = Pin(PIN_INPUT_1, Pin.IN, Pin.PULL_UP)
button_player_1 = Pin(PIN_INPUT_2, Pin.IN, Pin.PULL_UP)
button_player_2 = Pin(PIN_INPUT_3, Pin.IN, Pin.PULL_UP)
button_card_1 = Pin(PIN_INPUT_4, Pin.IN, Pin.PULL_UP)
button_card_2 = Pin(PIN_INPUT_5, Pin.IN, Pin.PULL_UP)

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

def read_pot_normalised(pot) -> int: 
    value = 1 - normalise_value(pot.read_u16(), 65535)
    return round(value, 2)

def read_pot_as_range(pot, max) -> int:
    return round(read_pot_normalised(pot) * max)

def write_7seg_display(msg):
    display.write_to_buffer(str(msg))

'''
======== GAME ========
'''

GAME_PLAYERS_MAX = 10
GAME_CARDS_MAX = 10

GAME_TIME_START = 35

class Game():
    currentHunters = 0
    currentCards = 0
    currentTime = 0

    def __init__(self, hunters, cards, time):
        self.currentHunters = hunters
        self.currentCards = cards
        self.currentTime = time
        
        print(self)

    def get_formatted_players(self) -> str:
        return "P" + str(self.currentHunters)

    def get_formatted_cards(self) -> str:
        return "C" + str(self.currentCards)

    def get_fromatted_display(self) -> str:
        return ("%-4s" % self.get_formatted_players()) + ("%-4s" % self.get_formatted_cards())

    def __str__(self):
        return "T: " + str(self.currentTime) + "\t" + self.get_fromatted_display()

GAME = Game(0, 0, GAME_TIME_START)

'''
======== GLOWBIT ========
'''

graph = stick.newGraph1D(0, GLOWBIT_SIZE - 1, 0, GAME_TIME_START, stick.red(), "Solid", True)

'''
======== MAIN ========
'''

# Button callbacks

def button_callback(p: Pin):
    
    # if(p.value() == 0):
    #     led.value(1)
        
    # else:
    #     led.value(0)
        
    led.toggle()
    print("BUTTON: "+ str(p.value()))
        
def button_player_update(change: int):
    GAME.currentHunters += change
    if(GAME.currentHunters > GAME_PLAYERS_MAX):
        GAME.currentHunters = GAME_PLAYERS_MAX
    if(GAME.currentHunters < 0):
        GAME.currentHunters = 0
    
def button_cards_update(change: int):
    GAME.currentCards += change
    if(GAME.currentCards > GAME_CARDS_MAX):
        GAME.currentCards = GAME_CARDS_MAX
    if(GAME.currentCards < 0):
        GAME.currentCards = 0

def button_decrement_time(args):
    GAME.currentTime -= 1
    if(GAME.currentTime < GAME_CARDS_MAX):
        GAME.currentTime = 0
        
    # write_7seg_display("T " + str(GAME.currentTime))
    # display.display()
    # time.sleep(1)

start_color = stick.green()
end_color = stick.red()

def updateTimeGraph():
    gameTimeCurrent = GAME.currentTime
    c = lerp_color(end_color, start_color, gameTimeCurrent / GAME_TIME_START)
    graph.colour = c
    stick.updateGraph1D(graph, gameTimeCurrent)

def init():
    # Start main LED blink
    #timer.init(freq=1, mode=Timer.PERIODIC, callback=blink)
    write_7seg_display('MHW BG')
    display.display()
    
    # Button callbacks
    # button_time.irq(handler = button_decrement_time, trigger = Pin.IRQ_FALLING)
    # button_player_1.irq(handler = button_player_increment, trigger = Pin.IRQ_FALLING)
    # button_player_2.irq(handler = button_player_decrement, trigger = Pin.IRQ_FALLING)
    # button_card_1.irq(handler = button_cards_increment, trigger = Pin.IRQ_FALLING)
    # button_card_2.irq(handler = button_cards_decrement, trigger = Pin.IRQ_FALLING)
    DebouncedSwitch(button_time, button_decrement_time)
    DebouncedSwitch(button_player_1, button_player_update, 1)
    DebouncedSwitch(button_player_2, button_player_update, -1)
    DebouncedSwitch(button_card_1, button_cards_update, 1)
    DebouncedSwitch(button_card_2, button_cards_update, -1)
    
    # Initialise the LED stick
    stick.chaos(20)
    stick.blankDisplay()

def main():
    
    global start_color
    
    while True:
        
        time.sleep(SLEEP_TIME)
        
        write_7seg_display(GAME.get_fromatted_display())
        
        updateTimeGraph()
        
        brightness = read_pot_as_range(pot_0, 50) + 6
        c = read_pot_as_range(pot_1, 255)
        if(c <= 200):
            start_color = stick.wheel(c)
        else:
            start_color = stick.white()
            
        stick.updateBrightness(brightness)
        # stick.pixelsFill(color)
        
        # stick.pixelsShow()
        display.display()
        
        # # print(stick.power())
        # print(GAME)
        
init()
main()