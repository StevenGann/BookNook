# MP3-TF-16P v3.0 / DFPlayer Mini – Command Reference

Complete list of serial commands supported by the MP3-TF-16P v3.0 and DFPlayer Mini. Use these to plan button behavior and ambient sound logic.

---

## Protocol

- **Baud:** 9600
- **Frame:** 10 bytes – Start(0x7E), Version(0xFF), Len(0x06), Cmd, FB(0x01), DH, DL, Checksum, End(0xEF)
- **Checksum:** `-(Version + Len + Cmd + FB + DH + DL)` as 2 bytes
- **Timing:** Use ≥100 ms delay between commands (MP3-TF-16P v3.0 has smaller buffer than DFPlayer Mini)

---

## Transport Control

| Cmd | Hex | Function | Params | Notes |
|-----|-----|----------|--------|-------|
| Next | 0x01 | Play next track | — | |
| Previous | 0x02 | Play previous track | — | |
| Play | 0x0D | Resume (from pause) | — | |
| Pause | 0x0E | Pause playback | — | |
| Stop | 0x16 | Stop playback | — | |

---

## Track & Folder Playback

| Cmd | Hex | Function | Params | Notes |
|-----|-----|----------|--------|-------|
| Play track | 0x03 | Play by global index | 1–2999 | Order = copy order on SD root |
| Play MP3 folder | 0x12 | Play from mp3/ or MP3/ | 0–65535 | File: 0001.mp3 … 09999.mp3 |
| Play folder | 0x0F | Play folder+file | Folder 1–99, File 1–255 | SD:/{folder}/{file:03d}.mp3 |
| Play large folder | 0x14 | Play folder+file (large) | Folder 1–10, File 1–1000 | DH=folder, DL=file (combined) |
| Loop track | 0x08 | Loop single track | 1–2999 | |
| Loop folder | 0x17 | Loop all in folder | 1–99 | |
| Loop all | 0x11 | Loop all on SD | DH=0x01 enable, 0x00 disable | |
| Loop mode | 0x19 | Enable/disable single-loop | DH=0x00 enable, 0x01 disable | |
| Random all | 0x18 | Shuffle & play all | — | |

---

## Advertising (Interrupt Main Playback)

| Cmd | Hex | Function | Params | Notes |
|-----|-----|----------|--------|-------|
| Play advertise | 0x13 | Play from ADVERT/ | 0–65535 | Pauses main track, resumes after |
| Stop advertise | 0x15 | End advertise playback | — | |

---

## Volume

| Cmd | Hex | Function | Params | Notes |
|-----|-----|----------|--------|-------|
| Set volume | 0x06 | Set level | 0–30 | 30 = max |
| Volume up | 0x04 | Increment by 1 | — | |
| Volume down | 0x05 | Decrement by 1 | — | |

---

## EQ

| Cmd | Hex | Function | Params | Notes |
|-----|-----|----------|--------|-------|
| Set EQ | 0x07 | Select preset | 0–5 | 0=Normal, 1=Pop, 2=Rock, 3=Jazz, 4=Classic, 5=Bass |

---

## Source & Output

| Cmd | Hex | Function | Params | Notes |
|-----|-----|----------|--------|-------|
| Select source | 0x09 | Choose playback device | 0–4 | 0=U_DISK, 1=SD, 2=AUX, 3=SLEEP, 4=FLASH |
| Output setting | 0x10 | Enable output, set gain | DH=enable 0/1, DL=gain 0–31 | |
| DAC | 0x1A | Enable/disable DAC | DH=0x00 enable, 0x01 disable | |

---

## Power

| Cmd | Hex | Function | Params | Notes |
|-----|-----|----------|--------|-------|
| Sleep | 0x0A | Low power standby | — | |
| Reset | 0x0C | Reset module | — | Wait ~2 s after reset |

---

## Query Commands (Read Response)

| Cmd | Hex | Function | Response |
|-----|-----|----------|----------|
| Query status | 0x42 | Current playback state | State value |
| Query volume | 0x43 | Current volume | 0–30 |
| Query EQ | 0x44 | Current EQ preset | 0–5 |
| Query TF file count | 0x48 | Total files on SD | Count |
| Query current file (SD) | 0x4C | Currently playing file | Index |
| Query folder file count | 0x4E | Files in folder | Params: folder 1–99 |
| Query folder count | 0x4F | Number of folders | Count |

---

## Response Codes (Feedback)

| Byte 3 | Meaning |
|--------|---------|
| 0x3C, 0x3D | Track finished |
| 0x3E, 0x42–0x4F | Query feedback (param in bytes 5–6) |
| 0x3F | Storage online (0x01 USB, 0x02 SD, 0x03 both) |
| 0x3A | Storage inserted |
| 0x3B | Storage removed |
| 0x40 | Error (param = error code) |
| 0x41 | ACK (command received) |

---

## dfplayer.py Function Mapping

| Function | Command |
|----------|---------|
| `next_track()` | 0x01 |
| `previous_track()` | 0x02 |
| `play()` | 0x0D |
| `pause()` | 0x0E |
| `stop()` | 0x16 |
| `play_track(n)` | 0x03 |
| `play_mp3_folder(n)` | 0x12 |
| `play_folder(folder, file)` | 0x0F |
| `play_large_folder(folder, file)` | 0x14 |
| `loop_track(n)` | 0x08 |
| `loop_folder(folder)` | 0x17 |
| `loop_all_enable()` / `loop_all_disable()` | 0x11 |
| `loop_mode_enable()` / `loop_mode_disable()` | 0x19 |
| `random_all()` | 0x18 |
| `play_advertise(n)` | 0x13 |
| `stop_advertise()` | 0x15 |
| `set_volume(0–30)` | 0x06 |
| `volume_up()` / `volume_down()` | 0x04 / 0x05 |
| `set_eq(0–5)` | 0x07 |
| `select_source(0–4)` | 0x09 |
| `output_setting(enable, gain)` | 0x10 |
| `dac_enable()` / `dac_disable()` | 0x1A |
| `sleep()` | 0x0A |
| `reset()` | 0x0C |
