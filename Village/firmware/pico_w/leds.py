# Village – Pico W SK6812 RGBW LED effects (oil lamp / fireplace).
# Requires a NeoPixel-compatible driver (e.g. neopixel.py or built-in) for RGBW.
# Effect modes: "off", "lamp", "fireplace".

import config
import time

# Optional: use machine.bitstream or a bundled neopixel. We assume an object
# with .fill(rgbw), .write(), and per-pixel setter, or we use a minimal PIO driver.
# If your build has neopixel.Neopixel (e.g. pico neopixel), use that.
try:
    from neopixel import Neopixel
    _driver = "neopixel"
except ImportError:
    Neopixel = None
    _driver = None

_strip = None
_mode = "off"
_brightness = 255  # 0-255
_last_update = 0
_flicker_phase = 0


def init():
    global _strip
    if Neopixel is not None:
        _strip = Neopixel(
            config.LED_COUNT,
            0,
            config.LED_DATA_PIN,
            config.LED_ORDER,
        )
        if hasattr(_strip, "brightness"):
            _strip.brightness(1)
        set_mode(_mode)
        return _strip
    # No neopixel driver: use dummy so MQTT/I2C still work (LEDs do nothing)
    class _DummyStrip:
        def fill(self, _): pass
        def show(self): pass
    _strip = _DummyStrip()
    set_mode(_mode)
    return _strip


def set_mode(mode):
    global _mode
    _mode = mode
    if _strip is None:
        return
    if mode == "off":
        _strip.fill((0, 0, 0, 0))
        _strip.show()
    # lamp/fireplace: updated in update()


def set_brightness(value):
    global _brightness
    _brightness = max(0, min(255, value))


def _lamp_color():
    # Warm yellow/orange, slight random for flicker
    import urandom
    r = 220 + urandom.getrandbits(4)
    g = 140 + urandom.getrandbits(4)
    b = 40
    w = 20 + urandom.getrandbits(3)
    return (r, g, b, w)


def _fireplace_color():
    import urandom
    r = 200 + urandom.getrandbits(5)
    g = 80 + urandom.getrandbits(4)
    b = 30
    w = 30 + urandom.getrandbits(4)
    return (r, g, b, w)


def update():
    """Call periodically (e.g. every 50–100 ms) to animate lamp/fireplace."""
    global _last_update, _flicker_phase
    if _strip is None or _mode == "off":
        return
    now = time.ticks_ms()
    if time.ticks_diff(now, _last_update) < 60:
        return
    _last_update = now
    _flicker_phase += 1
    scale = _brightness / 255.0
    if _mode == "lamp":
        c = _lamp_color()
    elif _mode == "fireplace":
        c = _fireplace_color()
    else:
        return
    r, g, b, w = c
    r = int(r * scale)
    g = int(g * scale)
    b = int(b * scale)
    w = int(w * scale)
    _strip.fill((r, g, b, w))
    if hasattr(_strip, "brightness"):
        _strip.brightness(scale)
    _strip.show()
