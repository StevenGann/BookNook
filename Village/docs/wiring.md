# Village – Wiring

## Pico W

| Function | GPIO | Notes |
|----------|------|--------|
| SK6812 data | Configurable (e.g. GP0) | PIO one-wire; 3.3 V or level-shift if strip is 5 V |
| I2C SDA | GP4 | Shared bus to all RP2350-Zero |
| I2C SCL | GP5 | 2.2 kΩ–4.7 kΩ pull-ups on SDA/SCL |
| 3.3 V / GND | — | Power to level shifter (if used) and bus |

**Avoid**: GP23, GP24, GP25 (reserved for CYW43 WiFi on Pico W).

## RP2350-Zero (per board)

| Function | Connection | Notes |
|----------|------------|--------|
| I2C SDA | Same bus as Pico W | Set I2C_SDA_PIN in config (e.g. 4) |
| I2C SCL | Same bus as Pico W | Set I2C_SCL_PIN in config (e.g. 5) |
| ST7789V | SPI + CS, DC, RST, BL | See Waveshare wiki for your module’s pinout |
| 3.3 V / GND | Shared supply | |

Assign each RP2350-Zero a different **I2C_SLAVE_ADDR** in `config.py` (e.g. 0x20, 0x21, 0x22). Same firmware; only the address changes.

## SK6812 RGBW

- Data from Pico W (PIO). If the strip is 5 V, use a level shifter (e.g. 74AHCT125) on the data line.
- Power the strip from an appropriate supply (5 V typical); do not feed high current through the Pico W.

## ST7789V 240×320

- Typically 3.3 V logic. Confirm from [Waveshare product page](https://www.waveshare.com/wiki/); level-shift only if the module is 5 V.
- SPI: one display per RP2350-Zero; each Zero uses one SPI bus for its LCD.

## Summary

- One I2C bus: Pico W (master) ↔ all RP2350-Zero (slaves, unique addresses).
- One GPIO from Pico W to SK6812 data.
- Each RP2350-Zero: I2C + one SPI to one ST7789V.
