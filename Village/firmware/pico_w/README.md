# Village – Pico W firmware

MicroPython code for the gateway: WiFi, MQTT, SK6812 LEDs, I2C master to LCD controllers.

## Files

- `config.py` – Edit for your WiFi, MQTT broker, `LCD_I2C_ADDRESSES`, LED pin/count/order.
- `lcd_bus.py` – I2C master: `set_scene(index, scene_id)`, `set_brightness(index, value)`.
- `leds.py` – SK6812 effects: `set_mode("off"|"lamp"|"fireplace")`, `set_brightness()`, `update()`.
- `main.py` – Connects WiFi and MQTT, subscribes to village topics, drives LEDs and I2C.

## Dependencies

- **MicroPython** for Pico W (with `network`, `machine`, `umqtt`).
- **umqtt**: `umqtt.simple` or `umqtt.robust` (often bundled or install via mip).
- **Neopixel (SK6812 RGBW)**: A driver that supports RGBW and your pin, e.g.:
  - [pi_pico_neopixel](https://github.com/blaz-r/pi_pico_neopixel) – save as `neopixel.py` on the board and use `Neopixel(n, 0, pin, "GRBW")` with `.fill()`, `.show()`.

## Config

- `LCD_I2C_ADDRESSES`: list of RP2350-Zero addresses in index order (e.g. `[0x20, 0x21, 0x22]`). Length = number of LCDs.
- `LED_COUNT`, `LED_DATA_PIN`, `LED_ORDER`: match your SK6812 strip.

## Run

Copy all `.py` files to the Pico W, edit `config.py`, then run `main.py` (e.g. from REPL: `import main` or name it `main.py` for auto-run on boot).
