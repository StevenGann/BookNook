# Village – RP2350-Zero ST7789 display init.
# Requires st7789py (russhughes/st7789py_mpy) or compatible driver on the board.
# Copy st7789py.py to the board and set DISPLAY_DRIVER below if using a different module.

import config
from machine import SPI, Pin

display = None


def init():
    global display
    try:
        from st7789py import ST7789
    except ImportError:
        try:
            import st7789
            ST7789 = st7789.ST7789
        except ImportError:
            # No driver: use dummy so animations still run (no-op draw)
            class Dummy:
                width = config.LCD_WIDTH
                height = config.LCD_HEIGHT
                def fill(self, c): pass
                def fill_rect(self, x, y, w, h, c): pass
                def pixel(self, x, y, c): pass
            display = Dummy()
            return display

    spi = SPI(
        config.SPI_ID,
        baudrate=20_000_000,
        sck=Pin(config.SPI_SCK),
        mosi=Pin(config.SPI_MOSI),
        miso=Pin(config.SPI_MISO) if hasattr(config, "SPI_MISO") else None,
    )
    dc = Pin(config.LCD_DC, Pin.OUT)
    rst = Pin(config.LCD_RST, Pin.OUT)
    cs = Pin(config.LCD_CS, Pin.OUT)
    bl = Pin(config.LCD_BL, Pin.OUT) if hasattr(config, "LCD_BL") else None
    display = ST7789(
        spi,
        width=config.LCD_WIDTH,
        height=config.LCD_HEIGHT,
        dc=dc,
        reset=rst,
        cs=cs,
        backlight=bl,
        rotation=0,
    )
    display.init()
    if bl is not None:
        bl.value(1)
    return display


def pixel(disp, x, y, color):
    """Set one pixel; use fill_rect if driver has no pixel()."""
    if hasattr(disp, "pixel"):
        disp.pixel(x, y, color)
    else:
        disp.fill_rect(x, y, 1, 1, color)
