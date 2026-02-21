# Village – Book Nook Project

A diorama-style book nook with warm lighting (oil lamp / fireplace LEDs), ambient sound, and optional animated LCD displays. The Raspberry Pi Pico W acts as the central controller; optional RP2350-Zero boards drive individual ST7789V LCDs over I2C.

---

## Documentation

| Document | Description |
|----------|-------------|
| [docs/wiring.md](docs/wiring.md) | Pin assignments, wire list, and connection details for all hardware |
| [docs/leds_control.md](docs/leds_control.md) | SK6812 LED strip: HSV color model, flicker, lamp/fireplace effects |
| [docs/mp3_player.md](docs/mp3_player.md) | MP3-TF-16P / DFPlayer Mini: usage, formats, SD layout, API |
| [docs/mp3_commands.md](docs/mp3_commands.md) | Full serial command reference for the MP3 module |
| [docs/i2c_protocol.md](docs/i2c_protocol.md) | Pico W ↔ RP2350-Zero I2C register map and scene selection |
| [docs/mqtt_topics.md](docs/mqtt_topics.md) | MQTT topics for remote control (LEDs, LCD scenes) |
| [firmware/pico_w/README.md](firmware/pico_w/README.md) | Pico W firmware: files, config, dependencies |
| [firmware/rp2350_lcd/README.md](firmware/rp2350_lcd/README.md) | RP2350-Zero LCD controller firmware |
| [tools/README.md](tools/README.md) | `image_sequence_to_bitmap.py` – convert images to LCD animations |

---

## System Architecture

```mermaid
flowchart TB
    subgraph PicoW [Pico W – Central Controller]
        main[main.py]
        leds_mod[leds.py]
        ambient_mod[ambient.py]
        dfplayer_mod[dfplayer.py]
        button_mod[button.py]
        lcd_bus[lcd_bus.py]
    end

    subgraph Peripherals [Peripherals]
        LED[SK6812 RGBW LED Strip]
        MP3[MP3-TF-16P / DFPlayer Mini]
        BTN[Button]
    end

    subgraph Optional [Optional – I2C]
        Zero1[RP2350-Zero 1 + ST7789V]
        Zero2[RP2350-Zero 2 + ST7789V]
        ZeroN[RP2350-Zero N]
    end

    main --> leds_mod
    main --> ambient_mod
    ambient_mod --> dfplayer_mod
    ambient_mod --> button_mod
    main -.-> lcd_bus

    leds_mod -->|GP0| LED
    dfplayer_mod -->|GP8 GP9 UART| MP3
    button_mod -->|GP10| BTN
    lcd_bus -->|GP4 GP5 I2C| Zero1
    lcd_bus -->|GP4 GP5 I2C| Zero2
    lcd_bus -->|GP4 GP5 I2C| ZeroN
```

---

## Wiring Summary

| Pico W Pin | Function | Connects To |
|------------|----------|-------------|
| **GP0** | SK6812 data | LED strip DATA IN |
| **GP4** | I2C SDA | RP2350-Zero SDA, pull-up to 3.3 V |
| **GP5** | I2C SCL | RP2350-Zero SCL, pull-up to 3.3 V |
| **GP8** | UART1 TX | MP3 module pin 2 (RX) |
| **GP9** | UART1 RX | MP3 module pin 3 (TX) |
| **GP10** | Button | Momentary switch → GND |
| **GND** | Ground | All peripherals |
| **3V3** | 3.3 V | Shared rail |

**Do not use:** GP23, GP24, GP25 (onboard WiFi).

See [docs/wiring.md](docs/wiring.md) for full pinout, MP3 module details, and RP2350-Zero wiring.

---

## Bill of Materials (BOM)

### Core (required)

| Item | Qty | Notes |
|------|-----|-------|
| Raspberry Pi Pico W | 1 | MicroPython |
| SK6812 RGBW LED strip | 1 | Configurable count; typically 20 LEDs |
| MP3-TF-16P v3.0 or DFPlayer Mini | 1 | UART-controlled MP3 playback |
| Micro SD card | 1 | FAT16/FAT32, max 32 GB; MP3, WAV, WMA |
| Momentary push button | 1 | Ambient sound trigger |
| Speaker or amplifier | 1 | Connect to MP3 DAC (pins 4, 5) or SPK (6, 8) |

### Optional

| Item | Qty | Notes |
|------|-----|-------|
| Level shifter (74AHCT125) | 1 | If LED strip is 5 V logic |
| 2.2–4.7 kΩ resistors | 2 | I2C pull-ups (SDA, SCL) |
| 1 kΩ resistors | 1–2 | Optional; MP3 TX/RX if buzzing |
| Waveshare RP2350-Zero | 0–N | One per LCD display |
| ST7789V 240×320 display | 0–N | One per RP2350-Zero |

---

## Component Logic

### Pico W (main.py)

- **Role:** Central hub. Initializes LEDs, MP3 module, and button; runs main loop every ~50 ms.
- **Loop:** `leds.update()` → `ambient.update()` → `time.sleep_ms(50)`.
- **Optional:** WiFi + MQTT for remote control of LED mode, brightness, and LCD scenes (see [docs/mqtt_topics.md](docs/mqtt_topics.md)).

### LEDs (leds.py)

- **Role:** Warm lighting effects (oil lamp, fireplace) via SK6812 RGBW strip.
- **Modes:** `off`, `lamp` (orange), `fireplace` (redder, dimmer).
- **Logic:** Per-LED HSV base color + random flicker; converted to RGBW; global brightness; R/G swap for hardware. Throttled to ~35 ms per frame.

```mermaid
flowchart LR
    A[set_mode] --> B[update]
    C[LED_HSV_CONFIG] --> B
    B --> D[Sample HSV + flicker]
    D --> E[RGBW + show]
```

### Ambient audio (ambient.py + dfplayer.py + button.py)

- **Role:** Button-triggered ambient sound: random clips with fade-in, configurable timeout, fade-out.
- **Logic:** State machine IDLE → FADE_IN → PLAYING → FADE_OUT → IDLE. Second button press = immediate stop.

```mermaid
stateDiagram-v2
    [*] --> IDLE
    IDLE --> FADE_IN: button pressed
    FADE_IN --> PLAYING: fade complete
    FADE_IN --> IDLE: button pressed
    PLAYING --> FADE_OUT: timeout
    PLAYING --> IDLE: button pressed
    FADE_OUT --> IDLE: fade complete
```

- **Config:** `AMBIENT_TIMEOUT_SEC`, `AMBIENT_FADE_IN_MS`, `AMBIENT_FADE_OUT_MS`, `AMBIENT_VOLUME`, `BUTTON_PIN`.

### LCD displays (RP2350-Zero + lcd_bus.py)

- **Role:** Animated bitmap scenes on ST7789V displays. Pico W sends scene ID (0–254) and brightness over I2C.
- **Logic:** Each RP2350 runs a slave; receives scene/brightness; plays `bitmap_anim.bin` at 24 fps, looping until scene change.
- **Tools:** `image_sequence_to_bitmap.py` converts image folders into `bitmap_anim.bin`.

```mermaid
flowchart LR
    subgraph PicoW
        lcd_bus[lcd_bus.set_scene]
    end
    subgraph I2C
        bus[I2C bus]
    end
    subgraph Zero [RP2350-Zero]
        reg[registers]
        anim[animations 24fps]
    end
    lcd_bus --> bus --> reg --> anim
```

### MQTT (optional)

- **Topics:** `booknook/village/leds/mode`, `booknook/village/leds/brightness`, `booknook/village/lcd/<index>/scene`, `booknook/village/lcd/<index>/brightness`.
- **Use case:** Home Assistant or other controller for remote control.

---

## Quick Start

1. Clone/copy the firmware; edit `firmware/pico_w/config.py` (WiFi, pins, LED count, etc.).
2. Copy firmware to Pico W; add `neopixel.py` driver for SK6812.
3. Wire per [docs/wiring.md](docs/wiring.md); format SD card; add ambient clips.
4. Run `main.py` on the Pico W.

For LCDs: build `bitmap_anim.bin` with [tools/image_sequence_to_bitmap.py](tools/image_sequence_to_bitmap.py), flash each RP2350-Zero, and set unique I2C addresses.
