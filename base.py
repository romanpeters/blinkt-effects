#!/usr/bin/env python
import time
import random
try:
    import blinkt
except ImportError:
    import fake_blinkt as blinkt

blinkt.set_clear_on_exit()

class FrameError(Exception):
    """Frame was corrupt"""
    pass

def mirror_frames(frames: list) -> list:
    mirrored = []
    for frame in frames:
        mirrored_frame = []
        for pixel in frame:
            mirrored_frame.insert(0, pixel)
        mirrored.append(mirrored_frame)
    return mirrored

class EffectBase(object):
    def __init__(self, frames, mirror=False, brightness=None):
        self.brightness = 0.2 if not brightness else brightness
        self.fps = 1
        self.frames = frames if not mirror else mirror_frames(frames)
        self.frame_n = 0
        self.frame = None
        self.overwrite = []
        self.mirror = mirror

    def step(self):
        """Execute frame"""
        if len(self.frame) == blinkt.NUM_PIXELS:  # check if normal frame
            for i in range(blinkt.NUM_PIXELS):
                blinkt.set_pixel(i, *self.frame[i])  #, brightness=self.brightness)
            blinkt.show()
        elif len(self.frame) == 1:  # check if special frame
            action = self.frame[0]
            if type(action) == VariableDelay:
                time.sleep(action.frames_delay() * (1/self.fps))
            else:
                raise FrameError
        else:
            print(len(self.frames))
            raise FrameError
        self._custom_action()
        self._next_frame()

    def add_overwrite(self, frames):
        "Replace running frames with other frames"
        self.overwrite = frames.copy() if not self.mirror else mirror_frames(frames)

    def _custom_action(self):
        pass

    def _next_frame(self):
        """Go to the next frame"""
        next = self.frame_n + 1
        if next >= len(self.frames):
            next = 0
        self.frame_n = next
        self.frame = self.frames[self.frame_n]
        if self.overwrite:
            self.frame = self.overwrite[0]
            self.overwrite.pop(0)

    def loop(self):
        if not self.frames:  # check if frames
            raise NotImplemented  # EffectBase must be inherited
        self.frame = self.frames[0]

        try:
            while True:
                self.step()
                time.sleep(1/self.fps)
        except KeyboardInterrupt:
            pass

class VariableDelay(object):
    def __init__(self, min=None, max=None):
        self.min = 0 if not min else min
        self.max = 3 if not max else max

    def frames_delay(self):
        return random.randint(self.min, self.max)


