# Village – RP2350-Zero register state (updated by I2C slave when master writes).
# Protocol: register 0 = scene_id, register 1 = brightness (see docs/i2c_protocol.md).

current_scene = 0
current_brightness = 255


def set_register(reg, value):
    global current_scene, current_brightness
    if reg == 0x00:
        current_scene = value & 0xFF
    elif reg == 0x01:
        current_brightness = value & 0xFF


def get_scene():
    return current_scene


def get_brightness():
    return current_brightness
