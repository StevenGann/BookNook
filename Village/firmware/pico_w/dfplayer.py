"""Village – MP3-TF-16P v3.0 / DFPlayer Mini serial driver.

Drives the MP3 player module via UART using the standard 0x7E protocol.
Compatible with both DFPlayer Mini HW-247A and MP3-TF-16P v3.0 (often sold as
"DFmini"). The MP3-TF-16P v3.0 requires at least 100 ms between commands;
MP3_CMD_DELAY_MS enforces this.

Wiring:
    Pico W TX (GP8) → MP3 module RX
    Pico W RX (GP9) ← MP3 module TX
    Both MP3 GND pins → common ground
    Optional: 1K resistor in series on TX/RX if buzzing occurs

Config (in config.py):
    MP3_TX_PIN, MP3_RX_PIN: UART pins (default 8, 9)
    MP3_BAUD: 9600
    MP3_CMD_DELAY_MS: Minimum ms between commands (default 120)

SD card: FAT16 or FAT32, max 32 GB. Use FAT32 for cards >2 GB.
Audio formats: MP3, WAV, WMA (sampling rates 8–48 kHz).
Layout: Root (global index); mp3/ (0001.mp3 …); 01/, 02/, …; ADVERT/.

See Village/docs/mp3_player.md for full usage guide.
"""

import config
import time
from machine import UART, Pin

_START = 0x7E
_VERSION = 0xFF
_LEN = 0x06
_END = 0xEF

# Command codes (from DFPlayer Mini / MP3-TF-16P protocol)
CMD_NEXT = 0x01
CMD_PREVIOUS = 0x02
CMD_PLAY_TRACK = 0x03
CMD_VOLUME_UP = 0x04
CMD_VOLUME_DOWN = 0x05
CMD_SET_VOLUME = 0x06
CMD_SET_EQ = 0x07
CMD_LOOP_TRACK = 0x08
CMD_SELECT_SOURCE = 0x09
CMD_SLEEP = 0x0A
CMD_RESET = 0x0C
CMD_PLAY = 0x0D
CMD_PAUSE = 0x0E
CMD_PLAY_FOLDER = 0x0F
CMD_OUTPUT_SETTING = 0x10
CMD_LOOP_ALL = 0x11
CMD_PLAY_MP3_FOLDER = 0x12
CMD_PLAY_ADVERTISE = 0x13
CMD_PLAY_LARGE_FOLDER = 0x14
CMD_STOP_ADVERTISE = 0x15
CMD_STOP = 0x16
CMD_LOOP_FOLDER = 0x17
CMD_RANDOM_ALL = 0x18
CMD_LOOP_MODE = 0x19
CMD_DAC = 0x1A

# EQ presets
EQ_NORMAL = 0
EQ_POP = 1
EQ_ROCK = 2
EQ_JAZZ = 3
EQ_CLASSIC = 4
EQ_BASS = 5

# Playback sources
SOURCE_U_DISK = 0
SOURCE_SD = 1
SOURCE_AUX = 2
SOURCE_SLEEP = 3
SOURCE_FLASH = 4

# Inter-command delay (ms). MP3-TF-16P v3.0 needs ~100 ms between commands.
_CMD_DELAY_MS = getattr(config, "MP3_CMD_DELAY_MS", 120)

_uart = None


def _send_command(cmd, param=0, param_high=None, param_low=None):
    """Send a 10-byte command frame to the MP3 module.

    Uses the 0x7E protocol: Start, Version, Len, Cmd, FB, DH, DL, Checksum, End.
    param is packed as 16-bit (DH, DL); or pass param_high, param_low directly.
    Applies MP3_CMD_DELAY_MS after sending.
    """
    global _uart
    if _uart is None:
        return
    if param_high is not None and param_low is not None:
        dh, dl = param_high, param_low
    else:
        dh = (param >> 8) & 0xFF
        dl = param & 0xFF
    buf = bytearray([_START, _VERSION, _LEN, cmd, 0x01, dh, dl])
    checksum = -(buf[1] + buf[2] + buf[3] + buf[4] + buf[5] + buf[6])
    buf.append((checksum >> 8) & 0xFF)
    buf.append(checksum & 0xFF)
    buf.append(_END)
    _uart.write(buf)
    time.sleep_ms(_CMD_DELAY_MS)


def init():
    """Initialize UART1 for communication with the MP3 module.

    Opens UART, waits 500 ms, sends reset, waits 2 s for module to restart and
    scan SD. Call select_source(SOURCE_SD) after init (e.g. from ambient.init).
    """
    global _uart
    tx = getattr(config, "MP3_TX_PIN", 8)
    rx = getattr(config, "MP3_RX_PIN", 9)
    baud = getattr(config, "MP3_BAUD", 9600)
    _uart = UART(1, baudrate=baud, tx=Pin(tx), rx=Pin(rx))
    time.sleep_ms(500)
    reset()
    time.sleep_ms(2000)
    return _uart


# ---- Transport control ----
def next_track():
    """Play the next track in the current playlist."""
    _send_command(CMD_NEXT)


def previous_track():
    """Play the previous track in the current playlist."""
    _send_command(CMD_PREVIOUS)


def play():
    """Resume playback (from pause)."""
    _send_command(CMD_PLAY)


def pause():
    """Pause playback. Use play() to resume."""
    _send_command(CMD_PAUSE)


def stop():
    """Stop playback completely. Use play_track, random_all, etc. to start again."""
    _send_command(CMD_STOP)


# ---- Track / folder playback ----
def play_track(track_index):
    """Play a track by global index (1–2999). Order follows SD root copy order."""
    _send_command(CMD_PLAY_TRACK, min(2999, max(1, track_index)))


def play_mp3_folder(file_num):
    """Play file from mp3/ or MP3/: 0001.mp3 … 09999.mp3. file_num: 0–65535."""
    _send_command(CMD_PLAY_MP3_FOLDER, min(65535, max(0, file_num)))


def play_folder(folder, file_num):
    """Play SD:/{folder}/{file:03d}.mp3. folder: 1–99, file_num: 1–255."""
    folder = min(99, max(1, folder))
    file_num = min(255, max(1, file_num))
    _send_command(CMD_PLAY_FOLDER, 0, folder, file_num)


def play_large_folder(folder, file_num):
    """Play from large-folder layout: folder 1–10, file 1–1000."""
    folder = min(10, max(1, folder))
    file_num = min(1000, max(1, file_num))
    _send_command(CMD_PLAY_LARGE_FOLDER, (folder << 12) | file_num)


def loop_track(track_index):
    """Loop a single track by global index (1–2999)."""
    _send_command(CMD_LOOP_TRACK, min(2999, max(1, track_index)))


def loop_folder(folder):
    """Loop all tracks in folder (1–99). Plays SD:/{folder}/ repeatedly."""
    _send_command(CMD_LOOP_FOLDER, min(99, max(1, folder)))


def loop_all_enable():
    """Enable looping of the entire SD playlist."""
    _send_command(CMD_LOOP_ALL, 0x01)


def loop_all_disable():
    """Disable playlist loop (stop after last track)."""
    _send_command(CMD_LOOP_ALL, 0x00)


def random_all():
    """Shuffle and play all tracks on SD in random order, one after another."""
    _send_command(CMD_RANDOM_ALL)


def loop_mode_enable():
    """Enable single-track loop (repeat current track until next command)."""
    _send_command(CMD_LOOP_MODE, 0x00)


def loop_mode_disable():
    """Disable single-track loop (advance to next when track ends)."""
    _send_command(CMD_LOOP_MODE, 0x01)


# ---- Advertising (interrupt main playback for a clip) ----
def play_advertise(file_num):
    """Play from ADVERT/ folder; main track pauses and resumes after."""
    _send_command(CMD_PLAY_ADVERTISE, min(65535, max(0, file_num)))


def stop_advertise():
    """Stop advertising playback and resume main track."""
    _send_command(CMD_STOP_ADVERTISE)


# ---- Volume ----
def set_volume(level):
    """Set volume level 0–30 (30 = max)."""
    _send_command(CMD_SET_VOLUME, min(30, max(0, level)))


def volume_up():
    """Increase volume by one step (0–30 range)."""
    _send_command(CMD_VOLUME_UP)


def volume_down():
    """Decrease volume by one step (0–30 range)."""
    _send_command(CMD_VOLUME_DOWN)


# ---- EQ ----
def set_eq(preset):
    """Set EQ preset: EQ_NORMAL(0), EQ_POP(1), EQ_ROCK(2), EQ_JAZZ(3), EQ_CLASSIC(4), EQ_BASS(5)."""
    _send_command(CMD_SET_EQ, min(5, max(0, preset)))


# ---- Source ----
def select_source(source):
    """Select playback source: SOURCE_U_DISK(0), SOURCE_SD(1), SOURCE_AUX(2), SOURCE_SLEEP(3), SOURCE_FLASH(4)."""
    _send_command(CMD_SELECT_SOURCE, min(4, max(0, source)))
    time.sleep_ms(200)  # source switch needs extra settling


# ---- Power / DAC ----
def sleep():
    """Enter low-power standby. Use select_source or reset to wake."""
    _send_command(CMD_SLEEP)


def reset():
    """Reset the MP3 module. Wait ~2 s before sending further commands."""
    _send_command(CMD_RESET)


def dac_enable():
    """Enable the DAC output."""
    _send_command(CMD_DAC, 0x00)


def dac_disable():
    """Disable the DAC output (mute)."""
    _send_command(CMD_DAC, 0x01)


def output_setting(enable, gain=15):
    """Enable or disable output; set gain 0–31 when enabling."""
    dh = 1 if enable else 0
    dl = min(31, max(0, gain))
    _send_command(CMD_OUTPUT_SETTING, 0, dh, dl)


# Response: track finished (0x3C or 0x3D)
_RX_BUF = bytearray(10)
_RX_IDX = 0


def poll_track_finished():
    """Non-blocking: return True if a track-finished (0x3C/0x3D) response was received.
    Use with play_track() for random/sequential playback; random_all() does not work on MP3-TF-16P."""
    global _uart, _RX_IDX
    if _uart is None:
        return False
    while _uart.any():
        b = _uart.read(1)
        if b is None:
            break
        _RX_BUF[_RX_IDX] = b[0]
        if _RX_IDX == 0:
            if b[0] != _START:
                continue
        _RX_IDX += 1
        if _RX_IDX >= 10:
            _RX_IDX = 0
            if _RX_BUF[9] != _END:
                continue
            checksum = -(_RX_BUF[1] + _RX_BUF[2] + _RX_BUF[3] + _RX_BUF[4] + _RX_BUF[5] + _RX_BUF[6])
            if (_RX_BUF[7] << 8 | _RX_BUF[8]) != (checksum & 0xFFFF):
                continue
            cmd = _RX_BUF[3]
            if cmd in (0x3C, 0x3D):
                return True
    return False


# ---- Query commands (require reading serial response) ----
def _query(cmd, param=0):
    """Send query and return response parameter. Blocks. Response format may vary."""
    _send_command(cmd, param)
    # For full query support, caller would parse UART response. Stub for now.
    return None
