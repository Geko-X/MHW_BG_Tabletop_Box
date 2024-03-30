from machine import Pin, Timer, PWM, SPI, ADC
import time
import max7219_8digit as seg

UPDATES_PER_SECOND = 10
SLEEP_TIME = 1 / UPDATES_PER_SECOND

# Main LED
led = Pin(25, Pin.OUT)
timer = Timer()

# Potentiometers
adc_0 = 26
adc_1 = 27

pot_0 = ADC(adc_0)
pot_1 = ADC(adc_1)

# 7-Seg
# MAX7219 VCC pin to VBUS
# MAX7219 GND pin to GND
# MAX7219 DIN pin to digital GPIO3
# MAX7219 CS pin to digital GPIO5
# MAX7219 CLOCK pin to digital GPIO2

spi = SPI(0, baudrate=10000000, polarity=1, phase=0, sck=Pin(2), mosi=Pin(3))
ss = Pin(5, Pin.OUT)
display = seg.Display(spi, ss, 0)


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

def format_players(count):
    return "P" + str(count)

def format_cards(count):
	return "C" + str(count)

def format_display(players, cards):
	return ("%-4s" % format_players(players)) + ("%-4s" % format_cards(cards))

'''
======== MAIN ========
'''

def init():
    # Start main LED blink
    timer.init(freq=1, mode=Timer.PERIODIC, callback=blink)
    write_7seg_display(' ')

def main():
    while True:
        time.sleep(SLEEP_TIME)

        players = read_pot_as_range(pot_0, GAME_PLAYERS_MAX)
        cards = read_pot_as_range(pot_1, GAME_CARDS_MAX)
        
        # s = game.format_display(value, value)
        # print(s)
        
        write_7seg_display(format_display(players, cards))
        
        display.display()
        
init()
main()