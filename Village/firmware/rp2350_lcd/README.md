# Village – RP2350-Zero LCD controller firmware

Runs on each Waveshare RP2350-Zero that drives one ST7789V display. Receives scene (0–254, up to 255 scenes) and brightness over I2C; plays bitmap animations from `bitmap_anim.bin` at 24 fps, looping until another scene is set.

## Files

- `config.py` – **I2C_SLAVE_ADDR** (unique per board, e.g. 0x20, 0x21, 0x22), ST7789 SPI pins, display size.
- `registers.py` – `current_scene`, `current_brightness`; updated when I2C master writes (see `i2c_slave`).
- `i2c_slave.py` – Starts hardware I2C slave if available; main loop calls `poll()` each frame.
- `i2c_slave_hw.py` – Hardware I2C slave (DesignWare peripheral, slave-only). Receives [reg, value] and calls `registers.set_register(reg, value)`.
- `display_driver.py` – Inits ST7789 via st7789py (or dummy if driver missing).
- `animations.py` – Bitmap-only: scenes 0–254 from `bitmap_anim.bin` (see `village/tools/`). 24 fps, loop until scene change.
- `main.py` – Init display and I2C slave; loop: poll I2C, track scene start time, draw current frame from bitmap at 24 fps, sleep.

## Dependencies

- **MicroPython** for RP2350 (or RP2040-compatible build).
- **st7789py** (e.g. [russhughes/st7789py_mpy](https://github.com/russhughes/st7789py_mpy)) – copy to board as `st7789py.py` (or adjust import in `display_driver.py`).

## I2C slave

A **hardware I2C slave** is included in `i2c_slave_hw.py` (DesignWare I2C in slave-only mode). It works on RP2040; RP2350 is often software-compatible (same register layout). Set `I2C_SDA_PIN`, `I2C_SCL_PIN`, and `I2C_BUS_ID` in `config.py` to match your wiring. The main loop calls `i2c_slave.poll()` each frame so received bytes `[reg, value]` from the Pico W update `registers`. If `i2c_slave_hw` fails to init (e.g. unsupported board), the firmware still runs with default scene (demo mode).

## Config

- Set **I2C_SLAVE_ADDR** to a different value on each board (e.g. 0x20, 0x21, 0x22) so the Pico W can address each LCD by index.
- Adjust **SPI_*** and **LCD_*** pins to match your Waveshare ST7789V module (see product wiki).

## Run

Copy all files to the RP2350-Zero, set `config.I2C_SLAVE_ADDR`, then run `main.py` (e.g. `import main` from REPL or name it `main.py` for auto-run).
