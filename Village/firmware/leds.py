# Village – Pico W SK6812 RGBW LED effects (oil lamp / fireplace).
#
# This module drives a strip of SK6812 RGBW LEDs with per-LED HSV-based colors
# and configurable flicker. Effects: "off", "lamp" (warm orange), "fireplace"
# (redder, dimmer). Each LED has its own base hue/saturation/value and
# per-channel flicker magnitude (dh, ds, dv). Colors are computed in HSV,
# converted to RGB, then to RGBW (white = min(R,G,B)); a hardware R/G swap
# is applied for strips that display red/green reversed.
#
# Dependencies: config, time, urandom; optional neopixel.Neopixel driver.
# See Village/docs/leds_control.md for full documentation and diagrams.

import config
import time
import urandom

try:
    from neopixel import Neopixel
    _driver = "neopixel"
except ImportError:
    Neopixel = None
    _driver = None

_strip = None       # Neopixel strip instance or DummyStrip
_mode = "off"      # "off" | "lamp" | "fireplace"
_brightness = 255  # Global brightness 0-255
_last_update = 0   # time.ticks_ms() of last update (throttle)
_hue_step = 0      # for LED_TEST_HUE_CYCLE: increments each frame

# Mode-specific HSV offsets (dh, ds, dv) added to base config. Fireplace: redder, less sat/value.
_MODE_OFFSET = {"lamp": (0, 0, 0), "fireplace": (15, -30, -20)}


def _hsv_to_rgb(h, s, v):
    """
    Convert HSV to RGB using the standard hexagonal cone model.

    :param h: Hue in degrees, 0-360 (0=red, 120=green, 240=blue; 30=orange).
    :param s: Saturation 0-1 (0=gray, 1=full color).
    :param v: Value (brightness) 0-1 (0=black, 1=full).
    :return: Tuple (r, g, b) with each component 0-255.
    """
    h = h % 360
    s = max(0, min(1, s))
    v = max(0, min(1, v))
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    r = max(0, min(255, int((r + m) * 255)))
    g = max(0, min(255, int((g + m) * 255)))
    b = max(0, min(255, int((b + m) * 255)))
    return (r, g, b)


def _rand_unit():
    """Uniform random in [0, 1). Uses 16-bit resolution."""
    return urandom.getrandbits(16) / 65535.0


def _rand_diff(magnitude):
    """
    Flicker delta: magnitude * (random() - random()).
    Gives a triangular-like distribution (values near 0 more likely than extremes).
    """
    if magnitude <= 0:
        return 0
    return magnitude * 0.5 * ((_rand_unit() + _rand_unit() + _rand_unit() + _rand_unit()) - (_rand_unit() + _rand_unit() + _rand_unit() + _rand_unit()))


def _get_led_config(i):
    """
    Return the 6-tuple (h, s, v, dh, ds, dv) for LED index i.
    Uses config.LED_HSV_CONFIG[i] if present; otherwise extends with a default.
    s and v: if both are in [0, 1], they are treated as 0-1 and scaled to 0-255
    so that (120, 1, 1) means full saturation and value (green).
    """
    cfg = getattr(config, "LED_HSV_CONFIG", None) or []
    if i < len(cfg):
        raw = cfg[i]
    else:
        raw = (30, 150, 255, 8, 20, 35)
        if cfg and isinstance(cfg[-1], (tuple, list)) and len(cfg[-1]) >= 6:
            raw = cfg[-1]
    h, s, v, dh, ds, dv = raw[0], raw[1], raw[2], raw[3], raw[4], raw[5]
    # Allow config to use 0-1 for s and v (e.g. (120, 1, 1) for full green)
    if 0 <= s <= 1 and 0 <= v <= 1:
        s = int(round(s * 255))
        v = int(round(v * 255))
    return (h, s, v, dh, ds, dv)


def init():
    """
    Initialize the LED strip. Uses config.LED_COUNT, LED_DATA_PIN, LED_ORDER.
    Transfer mode is PUT_CRITICAL to avoid glitches from interrupts during send.
    If the neopixel driver is missing, a no-op DummyStrip is used so callers
    (e.g. main/MQTT) still run without errors.
    """
    global _strip
    if Neopixel is not None:
        _strip = Neopixel(
            config.LED_COUNT,
            0,
            config.LED_DATA_PIN,
            config.LED_ORDER,
            transfer_mode="PUT_CRITICAL",
        )
        if hasattr(_strip, "brightness"):
            _strip.brightness(1)
        set_mode(_mode)
        return _strip
    class _DummyStrip:
        def fill(self, _): pass
        def show(self): pass
        def set_pixel(self, _, __): pass
    _strip = _DummyStrip()
    set_mode(_mode)
    return _strip


def set_mode(mode):
    """
    Set effect mode: "off", "lamp", or "fireplace".
    For "off", the strip is filled black and shown immediately.
    For "lamp"/"fireplace", the next update() will use the corresponding
    mode offset and per-LED HSV config.
    """
    global _mode
    _mode = mode
    if _strip is None:
        return
    if mode == "off":
        _strip.fill((0, 0, 0, 0))
        _strip.show()


def set_brightness(value):
    """Set global brightness 0-255. Applied in update() via the strip's brightness API."""
    global _brightness
    _brightness = max(0, min(255, value))


def _sample_led_color(led_index):
    """
    Sample a single frame of color for one LED: base HSV + mode offset + random
    flicker (using _rand_diff for each channel), then convert to RGB and
    optionally to RGBW (white = min(R,G,B), R/G/B reduced so hue is preserved).
    When LED_TEST_HUE_CYCLE is True: H increments each frame (no flicker), full S/V.
    """
    if getattr(config, "LED_TEST_HUE_CYCLE", False):
        step_size = getattr(config, "LED_TEST_HUE_STEP", 3)
        n = config.LED_COUNT
        # Stagger so each LED is at a different hue; all cycle through 0-360
        h = (_hue_step * step_size + led_index * (360 // max(1, n))) % 360
        s = 1.0
        v = 1.0
    else:
        h, s, v, dh, ds, dv = _get_led_config(led_index)
        oh, os_, ov = _MODE_OFFSET.get(_mode, (0, 0, 0))
        h = (h + oh + _rand_diff(dh)) % 360
        s = max(0, min(255, s + os_ + _rand_diff(ds))) / 255.0
        v = max(0, min(255, v + ov + _rand_diff(dv))) / 255.0
    r, g, b = _hsv_to_rgb(h, s, v)
    # RGBW: move common component to W so we don't wash out the color
    if "W" in config.LED_ORDER.upper():
        w = min(r, g, b)
        r = max(0, min(255, r - w))
        g = max(0, min(255, g - w))
        b = max(0, min(255, b - w))
        w = max(0, min(255, w))
    else:
        w = 0
    return (r, g, b, w)


def update():
    """
    Advance the animation by one frame. Call periodically (e.g. every 35 ms).
    Throttled so at most one frame per 35 ms. For each LED: sample HSV with
    flicker, convert to RGB(W), apply R/G swap for hardware, set_pixel, then
    show(). Brightness is applied once via the strip's global brightness.
    When LED_TEST_HUE_CYCLE is True, _hue_step increments each frame.
    """
    global _last_update, _hue_step
    if _strip is None or _mode == "off":
        return
    now = time.ticks_ms()
    if time.ticks_diff(now, _last_update) < 35:
        return
    _last_update = now
    if getattr(config, "LED_TEST_HUE_CYCLE", False):
        _hue_step += 1
    n = config.LED_COUNT
    has_w = "W" in config.LED_ORDER.upper()
    # Driver expects brightness 1-255 (not 0-1). Passing scale 0-1 made bratio=1/255 → all pixels 0 or 1.
    if _brightness == 0:
        _strip.fill((0, 0, 0, 0) if has_w else (0, 0, 0))
        _strip.show()
        return
    if hasattr(_strip, "brightness"):
        _strip.brightness(int(_brightness))
    for i in range(n):
        r, g, b, w = _sample_led_color(i)
        # Hardware R/G swap: send (g, r, b[, w]) so strip displays correct hue
        rgbw = (g, r, b, w) if has_w else (g, r, b)
        _strip.set_pixel(i, rgbw)
    _strip.show()
