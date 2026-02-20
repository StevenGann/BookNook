"""Village – Pico W: lamp/fireplace LEDs + button-triggered ambient audio.

Entry point for the Village book nook firmware. Initializes:
    - SK6812 RGBW LEDs (lamp/fireplace effects)
    - MP3-TF-16P module (ambient audio)
    - Button (ambient trigger)

Main loop runs leds.update() and ambient.update() every 50 ms.
"""

import leds
import dfplayer
import ambient
import time

leds.init()
leds.set_mode("lamp")   # "off" | "lamp" | "fireplace"
leds.set_brightness(255)

dfplayer.init()
ambient.init()  # select_source + button init

while True:
    leds.update()
    ambient.update()
    time.sleep_ms(50)
