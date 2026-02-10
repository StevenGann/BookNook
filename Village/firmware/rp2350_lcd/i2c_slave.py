# Village – RP2350-Zero I2C slave: receive register writes from Pico W and update registers.
# Uses hardware I2C slave (i2c_slave_hw) when available; otherwise runs in demo mode (registers at default).

import config
import registers

_use_hw = False


def start():
    """Start I2C slave. If hardware slave is available, init it; main loop must call poll()."""
    global _use_hw
    try:
        import i2c_slave_hw
        i2c_slave_hw.init(
            config.I2C_BUS_ID,
            config.I2C_SDA_PIN,
            config.I2C_SCL_PIN,
            config.I2C_SLAVE_ADDR,
        )
        _use_hw = True
    except Exception:
        _use_hw = False


def poll():
    """Call once per main-loop iteration to process received I2C bytes (when using hardware slave)."""
    if _use_hw:
        try:
            import i2c_slave_hw
            i2c_slave_hw.poll(registers)
        except Exception:
            pass
