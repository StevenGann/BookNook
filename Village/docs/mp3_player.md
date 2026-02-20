# MP3-TF-16P v3.0 / DFPlayer Mini – Module Usage Guide

This document describes how to use the `dfplayer` module with the MP3-TF-16P v3.0 or DFPlayer Mini in the Village book nook firmware.

---

## Overview

The `dfplayer` module drives the MP3 player via UART using the standard 0x7E serial protocol. It supports transport control (play, pause, stop), track and folder playback, volume, EQ, and power management. The module is compatible with both:

- **DFPlayer Mini HW-247A** (chip: MH2024K-24SS)
- **MP3-TF-16P v3.0** (chip: GT3200B, often sold as "DFmini")

Both use the same pinout and command set. The MP3-TF-16P v3.0 requires at least 100 ms between commands; `MP3_CMD_DELAY_MS` enforces this automatically.

---

## Hardware Wiring

| Pico W GPIO | Function | Connects to |
|-------------|----------|-------------|
| **GP8** | UART1 TX | MP3 module RX |
| **GP9** | UART1 RX | MP3 module TX |
| **GND** | Ground | Both MP3 GND pins |

- **Baud rate:** 9600, 8N1
- **Optional:** 1K resistor in series on TX/RX if you hear buzzing
- **Power:** Module runs on 3.2–5 V; ensure common ground with Pico W

See [wiring.md](wiring.md) for full pin assignments.

---

## Configuration

Edit `firmware/pico_w/config.py`:

```python
MP3_TX_PIN = 8    # Pico W UART1 TX → MP3 RX
MP3_RX_PIN = 9    # Pico W UART1 RX ← MP3 TX
MP3_BAUD = 9600
MP3_CMD_DELAY_MS = 120   # Minimum ms between commands (MP3-TF-16P needs ~100)
MP3_DEFAULT_VOLUME = 20  # 0–30
```

---

## Basic Usage

```python
import dfplayer

dfplayer.init()
dfplayer.select_source(dfplayer.SOURCE_SD)
dfplayer.set_volume(20)
dfplayer.play_track(1)
```

Always call `init()` before any other `dfplayer` function. The module needs ~500 ms to stabilize after init.

---

## SD Card Format and Capacity

| Spec | Supported |
|------|-----------|
| **File system** | FAT16, FAT32 |
| **Max capacity** | 32 GB |
| **exFAT (SDXC >32 GB)** | Not supported |

- Use **FAT32** for cards larger than 2 GB.
- Cards above 32 GB (SDXC) are typically exFAT and will not work.
- On Windows: right-click → Format → FAT32. For cards >32 GB, use a tool such as Rufus or SD Formatter to force FAT32 if needed.
- On macOS: avoid hidden files (`.DS_Store`, `._*`); run `dot_clean /Volumes/YourSDVolume` after copying files.

---

## Supported Audio Formats

| Format | Supported |
|--------|-----------|
| **MP3** | Yes |
| **WAV** | Yes |
| **WMA** | Yes |

- **Sampling rates:** 8, 11.025, 12, 16, 22.05, 24, 32, 44.1, 48 kHz
- **DAC:** 24-bit output, ~90 dB dynamic range, ~85 dB SNR
- MP3 is the most widely tested format; use it for best compatibility.

---

## SD Card Layout

### Root folder
Files at the SD root are playable by global index (1–N). Order = copy order.

- `play_track(1)` → first file, `play_track(2)` → second, etc.

### mp3/ or MP3/ folder
Use four-digit filenames: `0001.mp3`, `0002.mp3`, … `09999.mp3`.

- `play_mp3_folder(1)` → `mp3/0001.mp3`
- `play_mp3_folder(42)` → `mp3/0042.mp3`

### Numeric folders (01/, 02/, …)
Each folder can hold up to 255 files with three-digit names: `001.mp3`, `002.mp3`, etc.

- `play_folder(1, 5)` → `01/005.mp3`
- `loop_folder(2)` → loop all files in `02/`

### ADVERT/ folder
For “advertising” mode: a short clip interrupts the main track, then playback resumes.

- `play_advertise(3)` → play `ADVERT/0003.mp3`, then resume
- `stop_advertise()` → end the ad and resume immediately

---

## API Reference

### Initialization
| Function | Description |
|----------|-------------|
| `init()` | Initialize UART to the MP3 module. Call once before other functions. |

### Transport control
| Function | Description |
|----------|-------------|
| `play()` | Resume playback (from pause) |
| `pause()` | Pause playback |
| `stop()` | Stop playback completely |
| `next_track()` | Play next track |
| `previous_track()` | Play previous track |

### Track and folder playback
| Function | Description |
|----------|-------------|
| `play_track(n)` | Play by global index (1–2999) |
| `play_mp3_folder(n)` | Play `mp3/{n:04d}.mp3` (0–65535) |
| `play_folder(folder, file)` | Play `{folder}/{file:03d}.mp3` (folder 1–99, file 1–255) |
| `play_large_folder(folder, file)` | Large-folder layout (folder 1–10, file 1–1000) |
| `loop_track(n)` | Loop single track by index |
| `loop_folder(folder)` | Loop all tracks in folder |
| `random_all()` | Shuffle and play all SD tracks in random order |
| `loop_all_enable()` | Loop entire playlist |
| `loop_all_disable()` | Stop after last track |
| `loop_mode_enable()` | Repeat current track until next command |
| `loop_mode_disable()` | Advance to next when track ends |

### Advertising
| Function | Description |
|----------|-------------|
| `play_advertise(n)` | Play ad clip; main track pauses and resumes after |
| `stop_advertise()` | Stop ad and resume main track |

### Volume
| Function | Description |
|----------|-------------|
| `set_volume(level)` | Set volume 0–30 |
| `volume_up()` | Increase by one step |
| `volume_down()` | Decrease by one step |

### EQ
| Function | Description |
|----------|-------------|
| `set_eq(preset)` | `EQ_NORMAL`, `EQ_POP`, `EQ_ROCK`, `EQ_JAZZ`, `EQ_CLASSIC`, `EQ_BASS` |

### Source
| Function | Description |
|----------|-------------|
| `select_source(source)` | `SOURCE_U_DISK`, `SOURCE_SD`, `SOURCE_AUX`, `SOURCE_SLEEP`, `SOURCE_FLASH` |

### Power
| Function | Description |
|----------|-------------|
| `sleep()` | Low-power standby |
| `reset()` | Reset module (wait ~2 s before further commands) |
| `dac_enable()` / `dac_disable()` | Enable or disable DAC output |
| `output_setting(enable, gain)` | Enable output and set gain 0–31 |

---

## Ambient Audio Integration

The Village firmware uses `dfplayer` from the `ambient` module for button-triggered ambient sound:

1. Button press → `random_all()` starts playback
2. Fade-in via stepped `set_volume(0)` … `set_volume(AMBIENT_VOLUME)`
3. After `AMBIENT_TIMEOUT_SEC` → fade-out, then `stop()`
4. Second button press while playing → `stop()` immediately

See [ambient.py](../firmware/pico_w/ambient.py) and `config.AMBIENT_*` for behavior configuration.

---

## Command Timing

The MP3-TF-16P v3.0 has a smaller command buffer than the DFPlayer Mini. Sending commands too quickly can cause dropped or corrupted commands. The module enforces `MP3_CMD_DELAY_MS` (default 120) between each command. When implementing fades or rapid sequences, space `set_volume()` and other calls accordingly.

---

## Troubleshooting

| Symptom | Possible cause |
|---------|----------------|
| No sound | Check wiring; verify SD card inserted and formatted FAT16/FAT32; confirm source with `select_source(dfplayer.SOURCE_SD)` |
| Buzzing or distortion | Add 1K resistor in series on TX and/or RX |
| Commands ignored | Increase `MP3_CMD_DELAY_MS`; ensure 100+ ms between commands |
| Wrong track plays | Verify SD file layout (mp3/ vs root vs folders) |
| Module unresponsive | Power cycle; try `reset()` and wait 2 s |

---

## See Also

- [mp3_commands.md](mp3_commands.md) – Full protocol command reference
- [wiring.md](wiring.md) – Pin assignments and connections
