# Village – Pico W main: WiFi, MQTT, LEDs, I2C to LCD controllers.
# Copy config.py (and edit), lcd_bus.py, leds.py, main.py to the board.
# Requires: umqtt.simple (or umqtt.robust), neopixel driver for SK6812 RGBW.

import config
import time
import lcd_bus
import leds

# MQTT
try:
    from umqtt.simple import MQTTClient
except ImportError:
    from mqtt.simple import MQTTClient

MQTT_TOPIC_LEDS_MODE = config.MQTT_TOPIC_PREFIX + "/leds/mode"
MQTT_TOPIC_LEDS_BRIGHTNESS = config.MQTT_TOPIC_PREFIX + "/leds/brightness"
MQTT_TOPIC_LCD_SCENE = config.MQTT_TOPIC_PREFIX + "/lcd/{}/scene"
MQTT_TOPIC_LCD_BRIGHTNESS = config.MQTT_TOPIC_PREFIX + "/lcd/{}/brightness"

client = None
led_mode = "off"
led_brightness = 255
lcd_scenes = {}   # index -> scene_id
lcd_brightnesses = {}  # index -> 0-255


def wifi_connect():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        for _ in range(30):
            if wlan.isconnected():
                break
            time.sleep(0.5)
    if not wlan.isconnected():
        raise RuntimeError("WiFi failed")
    return wlan


def mqtt_callback(topic, msg):
    global led_mode, led_brightness
    t = topic.decode() if isinstance(topic, bytes) else topic
    m = msg.decode() if isinstance(msg, bytes) else msg
    if t == MQTT_TOPIC_LEDS_MODE:
        led_mode = m.strip().lower()
        if led_mode not in ("off", "lamp", "fireplace"):
            led_mode = "off"
        leds.set_mode(led_mode)
    elif t == MQTT_TOPIC_LEDS_BRIGHTNESS:
        try:
            led_brightness = max(0, min(255, int(m)))
            leds.set_brightness(led_brightness)
        except ValueError:
            pass
    elif t.startswith(config.MQTT_TOPIC_PREFIX + "/lcd/") and t.endswith("/scene"):
        try:
            idx = int(t.split("/")[-2])
            scene_id = max(0, min(254, int(m)))
            lcd_scenes[idx] = scene_id
            lcd_bus.set_scene(idx, scene_id)
        except (ValueError, IndexError):
            pass
    elif t.startswith(config.MQTT_TOPIC_PREFIX + "/lcd/") and t.endswith("/brightness"):
        try:
            idx = int(t.split("/")[-2])
            b = max(0, min(255, int(m)))
            lcd_brightnesses[idx] = b
            lcd_bus.set_brightness(idx, b)
        except (ValueError, IndexError):
            pass


def mqtt_connect():
    global client
    client = MQTTClient(
        config.MQTT_CLIENT_ID,
        config.MQTT_BROKER,
        port=config.MQTT_PORT,
        user=config.MQTT_USER[0] if config.MQTT_USER else None,
        password=config.MQTT_USER[1] if config.MQTT_USER else None,
    )
    client.set_callback(mqtt_callback)
    client.connect()
    client.subscribe(MQTT_TOPIC_LEDS_MODE)
    client.subscribe(MQTT_TOPIC_LEDS_BRIGHTNESS)
    for i in range(lcd_bus.lcd_count()):
        client.subscribe(MQTT_TOPIC_LCD_SCENE.format(i))
        client.subscribe(MQTT_TOPIC_LCD_BRIGHTNESS.format(i))
    return client


def main():
    wifi_connect()
    lcd_bus.init()
    leds.init()
    leds.set_mode(led_mode)
    leds.set_brightness(led_brightness)
    mqtt_connect()
    last_reconnect = time.ticks_ms()
    while True:
        try:
            client.check_msg()
        except OSError:
            try:
                client.connect()
            except Exception:
                pass
        leds.update()
        time.sleep_ms(50)


if __name__ == "__main__":
    main()
