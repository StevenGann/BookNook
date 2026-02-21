# Village – Pico W firmware

MicroPython code for the gateway: WiFi, MQTT, SK6812 LEDs, I2C master to LCD controllers.

## Files

- `config.py` – Edit for your WiFi, MQTT broker, `LCD_I2C_ADDRESSES`, LED pin/count/order.
- `lcd_bus.py` – I2C master: `set_scene(index, scene_id)`, `set_brightness(index, value)`.
- `leds.py` – SK6812 effects: `set_mode("off"|"lamp"|"fireplace")`, `set_brightness()`, `update()`.
- `main.py` – Drives LEDs and ambient audio; connects WiFi/MQTT when enabled.
- `ambient.py` – Button-triggered ambient audio: random clips with fade-in/out, 10 s timeout, stop on second press.
- `button.py` – Debounced button for ambient trigger.
- `dfplayer.py` – MP3-TF-16P v3.0 / DFPlayer Mini UART driver.

## Dependencies

- **MicroPython** for Pico W (with `network`, `machine`, `umqtt`).
- **umqtt**: `umqtt.simple` or `umqtt.robust` (often bundled or install via mip).
- **Neopixel (SK6812 RGBW)**: A driver that supports RGBW and your pin, e.g.:
  - [pi_pico_neopixel](https://github.com/blaz-r/pi_pico_neopixel) – save as `neopixel.py` on the board and use `Neopixel(n, 0, pin, "GRBW")` with `.fill()`, `.show()`.

## Config

- `LCD_I2C_ADDRESSES`: list of RP2350-Zero addresses in index order (e.g. `[0x20, 0x21, 0x22]`). Length = number of LCDs.
- `LED_COUNT`, `LED_DATA_PIN`, `LED_ORDER`: match your SK6812 strip.
- `BUTTON_PIN`, `AMBIENT_TRACK_COUNT`, `AMBIENT_TIMEOUT_SEC`, `AMBIENT_FADE_IN_MS`, `AMBIENT_FADE_OUT_MS`, `AMBIENT_VOLUME`: ambient audio behavior.

## Run

Copy all `.py` files to the Pico W, edit `config.py`, then run `main.py` (e.g. from REPL: `import main` or name it `main.py` for auto-run on boot).
