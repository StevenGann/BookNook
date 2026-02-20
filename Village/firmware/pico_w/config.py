# Village – Pico W configuration
# Copy to the board and edit for your network and hardware.

# ----- WiFi -----
WIFI_SSID = "your_ssid"
WIFI_PASSWORD = "your_password"

# ----- MQTT -----
MQTT_BROKER = "192.168.1.100"  # or hostname
MQTT_PORT = 1883
MQTT_USER = None  # set to ("user", "pass") if needed
MQTT_CLIENT_ID = "booknook_village"
MQTT_TOPIC_PREFIX = "booknook/village"

# ----- LCD controllers (I2C) -----
# List of I2C slave addresses for each RP2350-Zero, in index order.
# LCD index 0 = first address, index 1 = second, etc. Add/remove addresses to change LCD count.
LCD_I2C_ADDRESSES = [0x20, 0x21, 0x22]

# I2C bus pins on Pico W (avoid GP23–25: used by CYW43)
I2C_SDA_PIN = 4
I2C_SCL_PIN = 5
I2C_FREQ = 100_000

# ----- SK6812 RGBW LEDs -----
LED_DATA_PIN = 0
LED_COUNT = 20  # number of SK6812 LEDs in the strip
# Color order for your strip (common: "GRBW" or "RGBW")
LED_ORDER = "RGBW"

# Hue-cycle test: if True, H increments each frame (no flicker); LEDs cycle through gamut.
# LED_TEST_HUE_STEP = degrees to add to H per frame (e.g. 3).
LED_TEST_HUE_CYCLE = False
LED_TEST_HUE_STEP = 3

# Per-LED HSV config: (h, s, v, dh, ds, dv)
# h: hue 0-360 (30=orange, 0=red, 60=yellow)
# s, v: saturation/value 0-255
# dh, ds, dv: max random variation added each update (±range). dh in degrees; ds, dv 0-255.
# One entry per LED. Shorter list is extended with defaults.
LED_HSV_CONFIG = [
    (20, 250, 128, 2, 10, 35),   # LED 0
    (15, 250, 128, 2, 10, 40),  # LED 1
    (20, 250, 128, 2, 10, 30),   # LED 2
    (15, 250, 128, 2, 10, 45),  # LED 3
    (20, 250, 128, 2, 10, 32),   # LED 4
    (15, 250, 128, 2, 10, 38),   # LED 5
    (20, 250, 128, 2, 10, 35),   # LED 6
    (15, 250, 128, 2, 10, 42),  # LED 7
    (20, 250, 128, 2, 10, 33),   # LED 8
    (15, 250, 128, 2, 10, 40),  # LED 9
    (20, 250, 128, 2, 10, 30),   # LED 10
    (15, 250, 128, 2, 10, 45),  # LED 11
    (20, 250, 128, 2, 10, 32),   # LED 12
    (15, 250, 128, 2, 10, 38),   # LED 13
    (20, 250, 128, 2, 10, 35),   # LED 14
    (15, 250, 128, 2, 10, 42),  # LED 15
    (20, 250, 128, 2, 10, 33),   # LED 16
    (15, 250, 128, 2, 10, 40),  # LED 17
    (20, 250, 128, 2, 10, 30),   # LED 18
    (15, 250, 128, 2, 10, 45),  # LED 19
]

# ----- Button (ambient sound trigger) -----
BUTTON_PIN = 10   # Momentary switch; typically active-low with internal pull-up
BUTTON_DEBOUNCE_MS = 50
# Avoid: GP0, GP4, GP5, GP8, GP9, GP23–25 (LED, I2C, MP3 UART, WiFi)

# Ambient audio behavior (button-triggered)
AMBIENT_TIMEOUT_SEC = 10
AMBIENT_FADE_IN_MS = 500
AMBIENT_FADE_OUT_MS = 500
AMBIENT_VOLUME = 20   # 0–30

# ----- MP3-TF-16P v3.0 / DFPlayer Mini -----
# UART1: Pico W TX → MP3 RX, Pico W RX → MP3 TX. Avoid GP0, GP4, GP5, GP23–25.
MP3_TX_PIN = 8   # Pico W UART1 TX → MP3 module RX
MP3_RX_PIN = 9   # Pico W UART1 RX ← MP3 module TX
MP3_BAUD = 9600
# Minimum ms between commands (MP3-TF-16P v3.0 needs ~100 ms; DFPlayer Mini tolerates less)
MP3_CMD_DELAY_MS = 120
# Default volume 0–30
MP3_DEFAULT_VOLUME = 20
