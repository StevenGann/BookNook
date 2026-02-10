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
LED_COUNT = 10  # number of SK6812 LEDs in the strip
# Color order for your strip (common: "GRBW" or "RGBW")
LED_ORDER = "GRBW"
