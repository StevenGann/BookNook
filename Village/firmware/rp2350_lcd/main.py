# Village – RP2350-Zero LCD controller main.
# Scenes 0–7: bitmap animations from bitmap_anim.bin at 24 fps. Scene change over I2C.

import time
import config
import registers
import display_driver
import animations
import i2c_slave

# When current_scene changes, we set scene_start_ticks so playback runs at 24 fps from that moment.
_last_scene = -1
_scene_start_ticks = 0


def main():
    global _last_scene, _scene_start_ticks
    display_driver.init()
    i2c_slave.start()
    while True:
        i2c_slave.poll()
        scene = registers.get_scene()
        now = time.ticks_ms()
        if scene != _last_scene:
            _last_scene = scene
            _scene_start_ticks = now
        animations.run_frame(
            display_driver.display,
            scene,
            now,
            _scene_start_ticks,
        )
        time.sleep_ms(20)


if __name__ == "__main__":
    main()
