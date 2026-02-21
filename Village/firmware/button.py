"""Village – Debounced button for ambient sound trigger.

This module provides a simple, debounced interface for reading a momentary
push-button connected to the Pico W. It is designed for the ambient audio
trigger but can be used for any single-button input.

Wiring:
    - One leg of the switch → config.BUTTON_PIN (default GP10)
    - Other leg → GND
    - Internal pull-up is used; button press pulls the pin low (active-low)

Config (in config.py):
    BUTTON_PIN: GPIO number for the button (default 10)
    BUTTON_DEBOUNCE_MS: Minimum ms a press must be held to register (default 50)

Usage:
    button.init()
    while True:
        if button.pressed():
            # Handle press (e.g. start ambient audio)
        ...
"""

import config
import time
from machine import Pin

_pin = None
_last_raw = 1
_last_stable = 1
_debounce_until = 0


def init():
    """Configure the button pin as input with internal pull-up.

    Reads BUTTON_PIN and BUTTON_DEBOUNCE_MS from config.
    Must be called before pressed().

    Returns:
        The configured Pin object, or None if config is missing.
    """
    global _pin
    pin = getattr(config, "BUTTON_PIN", 10)
    _pin = Pin(pin, Pin.IN, Pin.PULL_UP)
    return _pin


def pressed():
    """Report a new, debounced button press (falling edge).

    Returns True exactly once per press, after the button has been held low
    for at least BUTTON_DEBOUNCE_MS. Subsequent calls return False until the
    button is released and pressed again.

    Should be called every main-loop iteration for responsive detection.

    Returns:
        True if a new press was detected this call, False otherwise.
    """
    global _last_raw, _last_stable, _debounce_until
    if _pin is None:
        return False
    raw = _pin.value()
    now = time.ticks_ms()
    # Transition high→low: start debounce
    if _last_raw == 1 and raw == 0:
        _debounce_until = time.ticks_add(now, getattr(config, "BUTTON_DEBOUNCE_MS", 50))
    _last_raw = raw
    # After debounce period, if still low and we were previously stable high → press
    if raw == 0 and _last_stable == 1 and time.ticks_diff(now, _debounce_until) >= 0:
        _last_stable = 0
        return True
    if raw == 1:
        _last_stable = 1
    return False
