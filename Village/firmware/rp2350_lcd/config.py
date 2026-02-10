# Village – RP2350-Zero LCD controller configuration
# Set I2C_SLAVE_ADDR to a unique value per board (e.g. 0x20, 0x21, 0x22).
# Same firmware on all boards; only this address changes.

I2C_SLAVE_ADDR = 0x20

# I2C slave bus (for receiving commands from Pico W). RP2350-Zero: check pinout for SDA/SCL.
I2C_BUS_ID = 0  # 0 or 1
I2C_SDA_PIN = 4
I2C_SCL_PIN = 5
# Optional: if your chip uses different I2C base addresses, set them here (i2c_slave_hw uses RP2040 defaults).
# I2C0_BASE = 0x40044000
# I2C1_BASE = 0x40048000

# ST7789V SPI pins – adjust for your Waveshare module (see wiki).
# Typical: one SPI bus, CS/DC/RST/backlight per display.
SPI_ID = 0
SPI_SCK = 2
SPI_MOSI = 3
SPI_MISO = 4  # optional for display
LCD_CS = 5
LCD_DC = 6
LCD_RST = 7
LCD_BL = 8    # backlight PWM

# Display size (Waveshare ST7789V 240x320 – may be rotated in driver)
LCD_WIDTH = 240
LCD_HEIGHT = 320
