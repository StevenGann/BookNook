# Village – Pico W I2C master: send scene/brightness to LCD controllers (RP2350-Zero).
# Uses config.LCD_I2C_ADDRESSES; index 0 = first address, etc.

from machine import I2C, Pin
import config

# Registers on the RP2350-Zero (see docs/i2c_protocol.md)
REG_SCENE = 0x00
REG_BRIGHTNESS = 0x01

_i2c = None


def init():
    global _i2c
    _i2c = I2C(
        0,
        sda=Pin(config.I2C_SDA_PIN),
        scl=Pin(config.I2C_SCL_PIN),
        freq=config.I2C_FREQ,
    )
    return _i2c


def _addr_for_index(index):
    addrs = config.LCD_I2C_ADDRESSES
    if index < 0 or index >= len(addrs):
        return None
    return addrs[index]


def set_scene(index, scene_id):
    """Set animation scene for LCD at index. scene_id: 0=off, 1=idle, 2=figure_walk, etc."""
    addr = _addr_for_index(index)
    if addr is None:
        return False
    try:
        _i2c.writeto(addr, bytes([REG_SCENE, scene_id & 0xFF]))
        return True
    except OSError:
        return False


def set_brightness(index, value):
    """Set brightness for LCD at index. value: 0–255."""
    addr = _addr_for_index(index)
    if addr is None:
        return False
    try:
        _i2c.writeto(addr, bytes([REG_BRIGHTNESS, value & 0xFF]))
        return True
    except OSError:
        return False


def lcd_count():
    return len(config.LCD_I2C_ADDRESSES)
