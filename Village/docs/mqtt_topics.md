# Village – MQTT Topics

The Pico W subscribes to these topics and controls LEDs and LCDs. LCD count is configurable; indices are 0-based and match the order of `lcd_i2c_addresses` in Pico W config.

## Topics

| Topic | Payload | Description |
|-------|---------|-------------|
| `booknook/village/leds/mode` | `lamp` \| `fireplace` \| `off` | LED effect mode |
| `booknook/village/leds/brightness` | 0–255 (decimal string or number) | Global LED brightness |
| `booknook/village/lcd/<index>/scene` | 0–254 (scene ID) | Set bitmap scene for LCD at `index` (up to 255 scenes) |
| `booknook/village/lcd/<index>/brightness` | 0–255 (optional) | Per-LCD brightness |

## Scene IDs (for `lcd/<index>/scene`)

Scenes are **bitmap-only**, from `bitmap_anim.bin` (see `village/tools/`). Folder N → scene N (0–254; up to 255 scenes). Each scene plays at **24 fps** and **loops** until another scene is set.

- `0`–`254` = scene 0–254 (bitmap animation; scene with 0 frames shows black)
- Any other value is clamped to 0–254 by the Pico W

## Home Assistant

Use the MQTT integration to create entities that publish to these topics (e.g. light for LEDs, select or number 0–7 for LCD scene).
