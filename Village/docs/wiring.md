# Village – Wiring

This page lists **which GPIO pin on each MCU** connects to what. Use the same numbers in firmware config.

---

## Pico W – pin assignment

| Pico W GPIO | Function | Connects to |
|-------------|----------|-------------|
| **GP0** | SK6812 data (PIO) | LED strip DATA IN (level-shift if strip is 5 V) |
| **GP4** | I2C SDA (master) | I2C bus SDA → **RP2350-Zero GP4** on every Zero; add 2.2–4.7 kΩ pull-up to 3.3 V |
| **GP5** | I2C SCL (master) | I2C bus SCL → **RP2350-Zero GP5** on every Zero; add 2.2–4.7 kΩ pull-up to 3.3 V |
| **3V3** | 3.3 V | Shared 3.3 V rail (optional for Zeros if USB-powered) |
| **GND** | Ground | Common GND with all RP2350-Zero and I2C bus |

**Do not use:** GP23, GP24, GP25 (onboard WiFi).

Config: `firmware/pico_w/config.py` — `LED_DATA_PIN`, `I2C_SDA_PIN`, `I2C_SCL_PIN`.

---

## RP2350-Zero – pin assignment (per board)

Each RP2350-Zero uses the pins below. Set **I2C_SLAVE_ADDR** to a unique value per board (e.g. 0x20, 0x21, 0x22). Config: `firmware/rp2350_lcd/config.py`.

### I2C (shared bus with Pico W and other Zeros)

| RP2350-Zero GPIO | Function | Connects to |
|------------------|----------|-------------|
| **GP4** | I2C SDA (slave) | **Pico W GP4** (SDA) and all other RP2350-Zero **GP4** |
| **GP5** | I2C SCL (slave) | **Pico W GP5** (SCL) and all other RP2350-Zero **GP5** |

### SPI and display (one ST7789V per Zero)

| RP2350-Zero GPIO | Function | Connects to |
|------------------|----------|-------------|
| **GP2** | SPI SCK | ST7789V SCL/SCK |
| **GP3** | SPI MOSI | ST7789V SDA/MOSI |
| **GP9** | LCD CS | ST7789V CS |
| **GP6** | LCD DC | ST7789V DC/RS |
| **GP7** | LCD RST | ST7789V RST/RESET |
| **GP8** | LCD backlight | ST7789V BL/LED |

Config names: `SPI_SCK`, `SPI_MOSI`, `LCD_CS`, `LCD_DC`, `LCD_RST`, `LCD_BL`. Match your Waveshare module’s pinout; see [Waveshare wiki](https://www.waveshare.com/wiki/).

### Power

| RP2350-Zero | Connects to |
|-------------|-------------|
| 3V3, GND | Shared 3.3 V and GND with Pico W |

---

## Wire list (summary)

| From | To |
|------|-----|
| Pico W **GP0** | SK6812 strip DATA IN |
| Pico W **GP4** | All RP2350-Zero **GP4** (SDA) + pull-up to 3.3 V |
| Pico W **GP5** | All RP2350-Zero **GP5** (SCL) + pull-up to 3.3 V |
| Pico W **GND** | All RP2350-Zero **GND** |
| Each Zero **GP2** | That Zero’s ST7789V SCK |
| Each Zero **GP3** | That Zero’s ST7789V MOSI |
| Each Zero **GP9** | That Zero’s ST7789V CS |
| Each Zero **GP6, GP7, GP8** | That Zero’s ST7789V DC, RST, BL |

---

## SK6812 RGBW

- **Data:** From Pico W **GP0**. If the strip is 5 V logic, use a level shifter (e.g. 74AHCT125) on the data line.
- **Power:** Use a separate 5 V supply for the strip; do not source high current from the Pico W.

---

## ST7789V 240×320

- 3.3 V logic typical; confirm on the [Waveshare product page](https://www.waveshare.com/wiki/).
- One display per RP2350-Zero; each Zero’s SPI (SCK, MOSI, CS, DC, RST, BL) goes to that display only.
