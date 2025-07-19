from debounce import DebouncedSwitch
from machine import Pin, Timer, PWM, SPI, ADC
import micropython
import time
import max7219_8digit as seg
import glowbit

import asyncio

from pico_constants import *
from patterns import *

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
# GLOWBIT_SIZE = 67
GLOWBIT_SIZE = 200
GLOWBIT_BRIGHTNESS = 8
GLOWBIT_FPS = UPDATES_PER_SECOND

effect_stick = glowbit.stick(
	pin = PIN_LEDS_LARGE,
	numLEDs = GLOWBIT_SIZE,
	brightness = GLOWBIT_BRIGHTNESS,
	rateLimitFPS = GLOWBIT_FPS,
	sm = 0
)

stick = glowbit.stick(
	pin = PIN_LEDS_SMALL,
	numLEDs = 16,
	brightness = GLOWBIT_BRIGHTNESS,
	rateLimitFPS = GLOWBIT_FPS,
	sm = 1
)



# Buttons
button_time = Pin(PIN_INPUT_10, Pin.IN, Pin.PULL_DOWN)
button_player_1 = Pin(PIN_INPUT_9, Pin.IN, Pin.PULL_DOWN)
button_player_2 = Pin(PIN_INPUT_8, Pin.IN, Pin.PULL_DOWN)
button_card_1 = Pin(PIN_INPUT_7, Pin.IN, Pin.PULL_DOWN)
button_card_2 = Pin(PIN_INPUT_6, Pin.IN, Pin.PULL_DOWN)

button_effect_1 = Pin(PIN_INPUT_1, Pin.IN, Pin.PULL_DOWN)
button_effect_2 = Pin(PIN_INPUT_2, Pin.IN, Pin.PULL_DOWN)
button_effect_3 = Pin(PIN_INPUT_3, Pin.IN, Pin.PULL_DOWN)
button_effect_4 = Pin(PIN_INPUT_4, Pin.IN, Pin.PULL_DOWN)
button_effect_5 = Pin(PIN_INPUT_5, Pin.IN, Pin.PULL_DOWN)

'''
======== HELPERS ========
'''

def normalise_value(value, max = 1):
	return value / max
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
	#print("Display -> "  + str(msg))

'''
======== GAME ========
'''

GAME_PLAYERS_MAX = 10
GAME_CARDS_MAX = 10

GAME_TIME_START = 40

class Game():
	currentHunters = 0
	currentCards = 0
	currentTime = 0

	setup = True
	pattern = False

	def __init__(self, hunters, cards, time):
		self.currentHunters = hunters
		self.currentCards = cards
		self.currentTime = time

	def get_formatted_players(self) -> str:
		return "P" + str(self.currentHunters)

	def get_formatted_cards(self) -> str:
		return "C" + str(self.currentCards)

	def get_fromatted_display(self) -> str:
		return ("%-4s" % self.get_formatted_players()) + ("%-4s" % self.get_formatted_cards())

	def set_time(self, time: int):
		if(time > GAME_TIME_START):
			time = GAME_TIME_START
		if(time < 0):
			time = 0

		self.currentTime = time
		print("Time set to " + str(time))

	def add_time(self, change: int):
		print("Adding time: " + str(change))
		self.set_time(self.currentTime + change)

	def __str__(self):
		return "T: " + str(self.currentTime) + "\t" + self.get_fromatted_display()

GAME = Game(0, 0, GAME_TIME_START)

'''
======== GLOWBIT ========
'''

graph = None

'''
======== ASYNC TASKS ========

'''

async def task_blink_led(time = 1):
	while True:
		led.toggle()
		await asyncio.sleep(time)

async def task_pattern_test():
	GAME.pattern = True
	print("Pattern Test")
	#await loop_pixel_async(stick, 0xFF0000, 3)
	#patterns_test(stick)
	GAME.pattern = False
	#await asyncio.sleep(0)

'''
======== MAIN ========
'''

table_color = effect_stick.blue()
start_color = stick.green()
end_color = stick.red()

def init_timegraph():
	global graph
	global GAME_TIME_START
 
	GAME_TIME_START = GAME.currentTime
	graph = stick.newGraph1D(0, 16 - 1, 0, GAME.currentTime, start_color, "Solid", True)
	print("Started time graph with max time of " + str(GAME.currentTime))

# Button callbacks

def button_callback(p: int):		
	led.toggle()
	print("BUTTON: "+ str(p))
 
def button_effect_start(i: int):
    print("Starting effect "+ str(i))
    
    if i == 1:
        #tziti_flash(effect_stick)
        #invasion(effect_stick)
        scoutfly(effect_stick)  
        
    if i == 2:
        c = lerp_color(effect_stick, table_color, 0, 0.5)
        effect_stick.updateBrightness(150 / 2)
        color_burst(effect_stick, effect_stick.white(), fade_in = 0.2, fade_out = 3)
        #fade(effect_stick, 0, c)
        
    if i == 3:
        c = lerp_color(effect_stick, table_color, 0, 0.5)
        fade(effect_stick, table_color, c)
        color_burst(effect_stick, 0xFF8800)
        fade(effect_stick, c, table_color)
     
    if i == 4:
        color_burst(effect_stick, effect_stick.purple(), 1, 3, 3)
            
    if i == 5:
        c = lerp_color(effect_stick, table_color, 0, 0.2)
        fade(effect_stick, table_color, c)
        loop_pixel(effect_stick, effect_stick.yellow(), 3, 0, 1, 100, c)
        fade(effect_stick, c, table_color)
 
def button_player_update(change: int):
		
	if(GAME.setup):
		GAME.add_time(change * 5)
		return
	
	else:
		GAME.currentHunters = GAME.currentHunters + change
		if(GAME.currentHunters > GAME_PLAYERS_MAX):
			GAME.currentHunters = GAME_PLAYERS_MAX
		if(GAME.currentHunters < 0):
			GAME.currentHunters = 0
	
def button_cards_update(change: int):
	
	if(GAME.setup):
		GAME.add_time(change)
		return

	else:
		GAME.currentCards = GAME.currentCards + change
		if(GAME.currentCards > GAME_CARDS_MAX):
			GAME.currentCards = GAME_CARDS_MAX
		if(GAME.currentCards < 0):
			GAME.currentCards = 0

def button_decrement_time(args):
 
	if(GAME.setup):
		GAME.setup = False
		init_timegraph()
  
	else:
		GAME.currentTime -= 1
		if(GAME.currentTime < 0):
			GAME.currentTime = 0
		print("Time: " + str(GAME.currentTime))
   
	# write_7seg_display("T " + str(GAME.currentTime))
	# display.display()
	# time.sleep(1)

def updateTimeGraph():
 
	if(graph is None):
		return
	
	else:
		gameTimeCurrent = GAME.currentTime
		c = lerp_color(stick, end_color, start_color, gameTimeCurrent / GAME_TIME_START)
		graph.colour = c
		stick.updateGraph1D(graph, gameTimeCurrent)


async def init():
	
	print("Starting async tasks")
	asyncio.create_task(task_blink_led(1))
 
	write_7seg_display("MHW BG")
	display.display()
 
	stick.chaos(50)
	# effect_stick.chaos(50)
	
	# Button callbacks
	DebouncedSwitch(button_time, button_decrement_time)
	DebouncedSwitch(button_player_1, button_player_update, 1)
	DebouncedSwitch(button_player_2, button_player_update, -1)
	DebouncedSwitch(button_card_1, button_cards_update, 1)
	DebouncedSwitch(button_card_2, button_cards_update, -1)
 
	DebouncedSwitch(button_effect_1, button_effect_start, 1)
	DebouncedSwitch(button_effect_2, button_effect_start, 2)
	DebouncedSwitch(button_effect_3, button_effect_start, 3)
	DebouncedSwitch(button_effect_4, button_effect_start, 4)
	DebouncedSwitch(button_effect_5, button_effect_start, 5)
	
	# Initialise the LED sticks
	stick.pixelsFillNow(start_color)
	effect_stick.pixelsFillNow(table_color)
 
	write_7seg_display("TIME " + str(GAME.currentTime))
	display.display()
 
	#GAME.setup = False
 
	await asyncio.sleep(0)
 
async def main():
	
	global table_color
	
	await init()
	
	await asyncio.sleep(0)
 
	while True:
		
		brightness = read_pot_as_range(pot_0, 100)
		c = read_pot_as_range(pot_1, 255)
  
		if(c <= 250):
			color = effect_stick.wheel(c)
		else:
			color = effect_stick.white()
			
		table_color = lerp_color(effect_stick, color, 0, 0.25)
		effect_stick.updateBrightness(brightness)
  
		if GAME.setup:
			write_7seg_display("T " + str(GAME.currentTime))

		else:
			write_7seg_display(GAME.get_fromatted_display())
		
		if not GAME.pattern:
			updateTimeGraph()
  
		effect_stick.pixelsFill(table_color)
		effect_stick.pixelsShow()
		display.display()
		
		await asyncio.sleep(SLEEP_TIME)

async def shutdown():
		
	print("Cleanup")
		
	write_7seg_display("        ")
	display.display()
	stick.pixelsFillNow(stick.black())
	effect_stick.pixelsFillNow(effect_stick.black())
	led.off()
	
	for task in asyncio.gather():
		task.cancel()
		
try:
	asyncio.run(main())
except:
	asyncio.run(shutdown())
finally:
	asyncio.new_event_loop()