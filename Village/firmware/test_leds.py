# Village – Pico W LED test only (no WiFi, MQTT)
# Run from REPL: exec(open('test_leds.py').read())
# Or upload as main.py and reset the board to auto-run.

import config
import time

print("=== LED Test ===")
print("LED_COUNT:", config.LED_COUNT)
print("LED_DATA_PIN:", config.LED_DATA_PIN)
print("LED_ORDER:", config.LED_ORDER)
print()

# Import neopixel driver
try:
    from neopixel import Neopixel
    print("neopixel driver: OK")
except ImportError as e:
    print("neopixel driver: FAIL -", e)
    raise

# Init strip (state_machine=0 for Pico W).
# PUT_CRITICAL = disable interrupts during send to avoid glitches (unpredictable colors).
strip = Neopixel(
    config.LED_COUNT,
    0,
    config.LED_DATA_PIN,
    config.LED_ORDER,
    transfer_mode="PUT_CRITICAL",
)
print("Neopixel init: OK")
print()

def solid(r, g, b, w=0):
    """Fill all LEDs with solid color (RGB or RGBW)."""
    if "W" in config.LED_ORDER.upper():
        strip.fill((r, g, b, w))
    else:
        strip.fill((r, g, b))
    strip.show()

def clear():
    """Turn all LEDs off."""
    solid(0, 0, 0, 0)

# Test 1: Brief flash RED (checks wiring, pin, data direction)
print("Test 1: Red flash (1 sec)...")
solid(255, 0, 0, 0)
time.sleep(1)
clear()
time.sleep(0.5)
print("  Done. Did you see red?")
print()

# Test 2: Brief flash WHITE (RGBW strip)
if "W" in config.LED_ORDER.upper():
    print("Test 2: White flash (1 sec)...")
    solid(0, 0, 0, 255)
    time.sleep(1)
    clear()
    time.sleep(0.5)
    print("  Done. Did you see white?")
print()

# Test 3: Dim white (low brightness – some strips need level shift)
print("Test 3: Dim white (3 sec)...")
solid(50, 50, 50, 50)
time.sleep(3)
clear()
print("  Done.")
print()

# Test 4: Loop – cycle R, G, B, W (hold Ctrl+C to stop)
print("Test 4: Color cycle (R->G->B->W). Press Ctrl+C to stop.")
print()

try:
    colors = [(255, 0, 0, 0), (0, 255, 0, 0), (0, 0, 255, 0), (0, 0, 0, 255)]
    i = 0
    while True:
        c = colors[i % 4]
        solid(*c)
        print("  ", ["RED", "GREEN", "BLUE", "WHITE"][i % 4])
        time.sleep(1)
        i += 1
except KeyboardInterrupt:
    pass

clear()
print()
print("Test ended. LEDs off.")
