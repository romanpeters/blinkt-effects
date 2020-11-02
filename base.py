#!/usr/bin/env python
import time
import random
try:
    import blinkt
except ImportError:
    import fake_blinkt as blinkt

blinkt.set_clear_on_exit()
OFF = (0, 0, 0)

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

def merge_frame(under_frame: list, over_frame: list) -> list:
    new_frame = under_frame
    for i in range(len(new_frame)):
        if type(over_frame[i]) != tuple or type(under_frame[i]) != tuple:
            pass
        elif over_frame[i] != OFF:
            new_frame[i] = over_frame[i]
    return new_frame

class EffectBase(object):
    def __init__(self, frames, fps=5, mirrored=False, overlay=None, underlay=None, brightness=None):
        self.brightness = 0.2 if not brightness else brightness
        self.fps = fps
        self.frames = frames
        self.frame_n = 0
        self.frame = None
        self.overwrite = []
        self.underlay = underlay if underlay else []
        self.underlay_n = 0
        self.overlay = overlay if overlay else []
        self.overlay_n = 0
        self.mirrored = False
        if mirrored:
            self.mirror()


    def mirror(self):
        self.frames = mirror_frames(self.frames)
        self.underlay = mirror_frames(self.underlay)
        self.overlay = mirror_frames(self.overlay)
        self.mirrored = not self.mirrored  # toggle

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
                print(action)
                raise FrameError(f"Unknown action {type(action)}")
        else:
            raise FrameError(f"Invalid frame number {len(self.frame)}, must be 1 or {blinkt.NUM_PIXELS}")
        self._custom_action()
        self._next_frame()

    def add_overwrite(self, frames):
        """Replace running frames with other frames"""
        self.overwrite = frames.copy() if not self.mirrored else mirror_frames(frames)

    def add_underlay(self, frames):
        """Merge running frames with other frames"""
        self.underlay = frames.copy() if not self.mirrored else mirror_frames(frames)

    def add_overlay(self, frames):
        """Merge running frames with other frames"""
        self.overlay = frames.copy() if not self.mirrored else mirror_frames(frames)

    def _custom_action(self):
        """Can be used in inherited classes"""
        pass

    def _next_frame(self):
        """Go to the next frame"""
        self.frame_n = self.frame_n + 1 if self.frame_n + 1 < len(self.frames) else 0
        self.frame = self.frames[self.frame_n]
        if self.overwrite:  # overwrites the frame
            self.frame = self.overwrite[0]
            self.overwrite.pop(0)
            return  # frame is overwritten, so no need for over-/underlays
        if self.underlay:  # adds another frame under the original frame
            self.frame = merge_frame(self.underlay[self.underlay_n], self.frame)
            self.underlay_n = self.underlay_n + 1 if self.underlay_n + 1 < len(self.underlay) else 0
        if self.overlay:  # adds another frome over the original frame
            self.frame = merge_frame(self.frame, self.overlay[self.overlay_n])
            self.overlay_n = self.overlay_n + 1 if self.overlay_n + 1 < len(self.overlay) else 0



    def loop(self):
        """Run through the frames until stopped"""
        if not self.frames:  # check if frames
            raise NotImplemented  # EffectBase must be inherited
        self.frame = self.frames[0]

        try:
            while True:
                self.step()
                time.sleep(1/self.fps)
        except KeyboardInterrupt:
            pass

class Effect(EffectBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class VariableDelay(object):
    def __init__(self, min=None, max=None):
        self.min = 0 if not min else min
        self.max = 3 if not max else max

    def frames_delay(self):
        return random.randint(self.min, self.max)


