# Village – Pico W: lamp/fireplace LEDs only (WiFi, MQTT, I2C disabled).

import leds
import time

leds.init()
leds.set_mode("lamp")   # "off" | "lamp" | "fireplace"
leds.set_brightness(255)

while True:
    leds.update()
    time.sleep_ms(50)
