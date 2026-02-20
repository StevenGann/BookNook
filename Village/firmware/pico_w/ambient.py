"""Village – Ambient audio state machine (button-triggered, fade-in/out, timeout).

Orchestrates playback of random ambient clips from the MP3-TF-16P module when
the user presses a button. Supports soft fade-in and fade-out, a configurable
timeout, and immediate stop on a second button press.

State diagram:
    IDLE → FADE_IN (on button press)
    FADE_IN → PLAYING (when fade completes) or IDLE (on button = immediate stop)
    PLAYING → FADE_OUT (after AMBIENT_TIMEOUT_SEC) or IDLE (on button = immediate stop)
    FADE_OUT → IDLE (when fade completes)

Config (in config.py):
    AMBIENT_TIMEOUT_SEC: Playback duration before auto fade-out (default 10)
    AMBIENT_FADE_IN_MS: Duration of fade-in in ms (default 500)
    AMBIENT_FADE_OUT_MS: Duration of fade-out in ms (default 500)
    AMBIENT_VOLUME: Target volume 0–30 during playback (default 20)
    MP3_CMD_DELAY_MS: Minimum ms between MP3 commands (affects fade step rate)

Dependencies:
    dfplayer, button, config

Usage:
    dfplayer.init()
    ambient.init()
    while True:
        ambient.update()
        time.sleep_ms(50)
"""

import config
import time
import dfplayer
import button

_IDLE = 0
_FADE_IN = 1
_PLAYING = 2
_FADE_OUT = 3

_state = _IDLE
_play_start = 0
_fade_step = 0
_fade_last_ms = 0


def _cfg(key, default):
    """Read config value with default fallback."""
    return getattr(config, key, default)


def init():
    """Initialize ambient audio: select SD source and init button.

    Call this after dfplayer.init(). Configures the MP3 player to use the SD
    card and initializes the button module for press detection.
    """
    dfplayer.select_source(dfplayer.SOURCE_SD)
    button.init()


def _start_fade_in():
    global _state, _fade_step, _fade_last_ms
    dfplayer.set_volume(0)
    dfplayer.random_all()
    _state = _FADE_IN
    _fade_step = 0
    _fade_last_ms = time.ticks_ms()


def _do_immediate_stop():
    global _state
    dfplayer.stop()
    _state = _IDLE


def _step_fade_in():
    global _state, _play_start, _fade_step, _fade_last_ms
    delay = _cfg("MP3_CMD_DELAY_MS", 120)
    fade_ms = _cfg("AMBIENT_FADE_IN_MS", 500)
    target = min(30, _cfg("AMBIENT_VOLUME", 20))
    n_steps = max(1, fade_ms // delay)
    now = time.ticks_ms()
    if time.ticks_diff(now, _fade_last_ms) < delay:
        return
    _fade_last_ms = now
    _fade_step += 1
    vol = min(target, (target * _fade_step) // n_steps)
    dfplayer.set_volume(vol)
    if _fade_step >= n_steps or vol >= target:
        _state = _PLAYING
        _play_start = time.ticks_ms()


def _step_fade_out():
    global _state, _fade_step, _fade_last_ms
    delay = _cfg("MP3_CMD_DELAY_MS", 120)
    fade_ms = _cfg("AMBIENT_FADE_OUT_MS", 500)
    target = min(30, _cfg("AMBIENT_VOLUME", 20))
    n_steps = max(1, fade_ms // delay)
    now = time.ticks_ms()
    if time.ticks_diff(now, _fade_last_ms) < delay:
        return
    _fade_last_ms = now
    _fade_step += 1
    vol = max(0, target - (target * _fade_step) // n_steps)
    dfplayer.set_volume(vol)
    if _fade_step >= n_steps or vol <= 0:
        dfplayer.stop()
        _state = _IDLE


def update():
    """Advance the ambient audio state machine.

    Polls the button, handles transitions, and performs fade stepping.
    Call this every main-loop iteration (e.g. every 50 ms).
    """
    global _state, _play_start, _fade_step, _fade_last_ms
    bp = button.pressed()

    if _state == _IDLE:
        if bp:
            _start_fade_in()
        return

    if _state == _FADE_IN:
        if bp:
            _do_immediate_stop()
            return
        _step_fade_in()
        return

    if _state == _PLAYING:
        if bp:
            _do_immediate_stop()
            return
        elapsed_sec = time.ticks_diff(time.ticks_ms(), _play_start) // 1000
        if elapsed_sec >= _cfg("AMBIENT_TIMEOUT_SEC", 10):
            _state = _FADE_OUT
            _fade_step = 0
            _fade_last_ms = time.ticks_ms()
        return

    if _state == _FADE_OUT:
        _step_fade_out()
