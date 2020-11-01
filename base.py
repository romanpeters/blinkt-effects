#!/usr/bin/env python
import time
try:
    import blinkt
except ImportError:
    import fake_blinkt as blinkt

blinkt.set_clear_on_exit()

class EffectBase():
    def __init__(self, brightness=None, speed=None):
        self.brightness = 0.2 if not brightness else brightness
        self.speed = 1.0 if not speed else speed
        self.fps = 2 * self.speed
        self.sleep = 1 / self.fps
        self.frames = []
        self.frame_n = 0

    def step(self):
        if not self.frames:
            raise NotImplemented
        for i in range(blinkt.NUM_PIXELS):
            blinkt.set_pixel(i, *self.frames[self.frame_n][i], brightness=self.brightness)
        blinkt.show()
        self._next_frame()

    def _next_frame(self):
        next = self.frame_n + 1
        if next >= len(self.frames):
            next = 0
        self.frame_n = next

    def loop(self):
        try:
            while True:
                self.step()
                time.sleep(self.sleep)
        except KeyboardInterrupt:
            pass


