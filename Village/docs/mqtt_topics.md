# Village – MQTT Topics

The Pico W subscribes to these topics and controls LEDs.

## Topics

| Topic | Payload | Description |
|-------|---------|-------------|
| `booknook/village/leds/mode` | `lamp` \| `fireplace` \| `off` | LED effect mode |
| `booknook/village/leds/brightness` | 0–255 (decimal string or number) | Global LED brightness |

## Home Assistant

Use the MQTT integration to create entities that publish to these topics (e.g. light for LEDs).
