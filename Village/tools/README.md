# Village – Tools

## image_sequence_to_bitmap.py

Converts **numbered folders** of images into one multi-scene RGB565 asset for RP2350 LCDs. All animations are bitmap-only; up to **255 scenes** (0–254) play at 24 fps and loop until another scene is triggered over I2C.

### Input layout

- **Root folder** containing subfolders named **0**, **1**, … **254** (any subset; missing folders = 0 frames = black on device).
- **Folder N** → **scene N** on the device.
- Each subfolder contains **numbered images** (e.g. `000.png`, `001.png`, `frame_001.jpg`). Frames are ordered by the first number in the filename.
- **1–120 frames** per scene (each scene can have a different count). At least one folder must have images.

Example:

```
my_animations/
  0/           → scene 0 (e.g. off/black – one or more frames)
    000.png
  1/           → scene 1
    000.png, 001.png, ...
  ...
  10/          → scene 10
    000.png .. 019.png
```

### Setup

```bash
pip install -r requirements.txt
```

### Usage

```text
python image_sequence_to_bitmap.py <input_root> [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--output-dir`, `-o` | same as input | Where to write generated files |
| `--width`, `-W` | 240 | Output width (pixels) |
| `--height`, `-H` | 320 | Output height (pixels) |
| `--name`, `-n` | bitmap_anim | Base name for output files |
| `--c-only` | — | Only emit C `.h`/`.c` files |
| `--bin-only` | — | Only emit `.bin` file |

### Outputs

- **Binary (default)**  
  `{name}.bin` – 518-byte header (magic `BANM`, width, height, 255× frame count), then all scenes’ RGB565 frames in order (scene 0, 1, … 254). Copy to the RP2350 as `bitmap_anim.bin` for MicroPython playback.

- **C (default)**  
  `{name}.h` and `{name}.c` – `{name}_frame_count[255]`, `{name}_data[]` (all frames concatenated). For C/C++ RP2350 builds. Note: with many scenes the .c file can be very large.

### Example

```bash
python image_sequence_to_bitmap.py ./my_animations --output-dir ../firmware/rp2350_lcd --name bitmap_anim
```

Then copy `bitmap_anim.bin` to each RP2350-Zero. Scenes 0–254 are selected over I2C (or MQTT via Pico W); each plays at 24 fps and loops until another scene is selected.
