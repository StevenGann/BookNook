# Village – Wiring

This page lists **which GPIO pin on each MCU** connects to what. Use the same numbers in firmware config.

---

## Pico W – pin assignment

| Pico W GPIO | Function | Connects to |
|-------------|----------|-------------|
| **GP0** | SK6812 data (PIO) | LED strip DATA IN (level-shift if strip is 5 V) |
| **3V3** | 3.3 V | Shared 3.3 V rail |
| **GND** | Ground | Common GND |
| **GP8** | UART1 TX (MP3) | MP3 pin 2 (RX) |
| **GP9** | UART1 RX (MP3) | MP3 pin 3 (TX) |
| **GP10** | Button | Momentary switch (other side → GND) |

**Do not use:** GP23, GP24, GP25 (onboard WiFi).

Config: `firmware/config.py` — `LED_DATA_PIN`, `MP3_TX_PIN`, `MP3_RX_PIN`, `BUTTON_PIN`.

---

## Wire list (summary)

| From | To |
|------|-----|
| Pico W **GP0** | SK6812 strip DATA IN |
| Pico W **GP8** | MP3 pin 2 (RX); optional 1K in series if buzzing |
| Pico W **GP9** | MP3 pin 3 (TX) |
| Pico W **GND** | MP3 pins 7 and 10 (GND) |
| Pico W **GP10** | Button one leg |
| Button other leg | GND |

---

## SK6812 RGBW

- **Data:** From Pico W **GP0**. If the strip is 5 V logic, use a level shifter (e.g. 74AHCT125) on the data line.
- **Power:** Use a separate 5 V supply for the strip; do not source high current from the Pico W.

---

## Button (ambient sound trigger)

- **Pico W GP10** → one leg of momentary switch; other leg → **GND**
- Use internal pull-up: pressed = low, released = high
- Config: `config.BUTTON_PIN`

---

## MP3-TF-16P v3.0 / DFPlayer Mini

### Module pinout (16 pins, left to right)

| Pin | Name | Connect to |
|-----|------|------------|
| 1 | VCC | 3.3 V or 5 V |
| 2 | RX | Pico W **GP8** (UART1 TX) |
| 3 | TX | Pico W **GP9** (UART1 RX) |
| 4 | DAC_R | Amp/speaker (audio right) |
| 5 | DAC_L | Amp/speaker (audio left) |
| 6 | SPK2 | Speaker − (or use DAC) |
| 7 | GND | Common GND |
| 8 | SPK1 | Speaker + (or use DAC) |
| 9 | IO1 | (optional I/O) |
| 10 | GND | Common GND |
| 11–16 | IO2, ADKEY1, ADKEY2, USB, BUSY | (optional) |

### Pico W ↔ MP3 connections

| From | To |
|------|-----|
| Pico W **GP8** | MP3 pin 2 (RX) |
| Pico W **GP9** | MP3 pin 3 (TX) |
| Pico W **GND** | MP3 pins 7 and 10 (GND) |
| 3V3 or 5V | MP3 pin 1 (VCC) |

- **UART:** 9600 baud, 8N1. Optional 1K resistor in series on GP8→RX if buzzing.
- **Power:** 3.2–5 V. Level-shift UART if using 5 V (module is often 5 V tolerant).
- **SD card:** FAT16 or FAT32, max 32 GB. Audio: MP3, WAV, WMA. See [mp3_player.md](mp3_player.md) for format and layout.
- **Ambient clips:** Put in `mp3/` or SD root. `random_all()` plays all files in random order.
