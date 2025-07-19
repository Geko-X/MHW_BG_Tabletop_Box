Hardware lighting and effects "box" for MHW:BG.

Also shows player and card counts on a 7-segment display.

# Hardware
- Raspberry Pi Pico
- MAX7219 7-segment display
- 2x potentiometers
- 2x WS2812B lightstrips (16 LEDs and "many" LEDs)
- 10x tactile buttons
  - 5 for time and card counts
  - 5 for effects


## Pins

- Potentiometers on GP 26 and 27 (Physcial pins 31 and 32)
  - Wire to ADC_VREF (pin 35) and ADC_GND (pin 33)
- Tactile buttons on GP 6-15 (Physical pins 9-12, 14-17, 19, 20)
  - Wire to 3V3 OUT (pin 36)
    
- MAX7219
  - VCC: VBUS
  - DIN: GP 3 (Phsycial pin 5)
  - CLOCK: GP 2 (Phsycial pin 4)
  - CS: GP 5 (Phsycial pin 7)
    
Small WS2812B:
  - VCC: VBUS
  - DIN: GP 17 (Physcial pin 22)
    
Large WS2812B:
  - VCC: VBUS
  - DIN: GP 16 (Phsycial pin 21)

## Wiring

![Wiring diagram](https://github.com/Geko-X/MHW_BG_Tabletop_Box/blob/main/MHW_BG_Box_bb.png)
