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


def compile_frames(frames: list) -> list:
    result = []
    for i in range(len(frames)):
        frame_length = len(frames[i])

        # normal frame - continue
        if frame_length == blinkt.NUM_PIXELS:
            result.append(frames[i])

        # action frame
        elif frame_length == 1:  # check if special frame
            action = frames[i][0]

            # VariableDelay
            if type(action) == VariableDelay:
                if result:  # delay is not in frame #0
                    freeze_frame = result[-1]
                else:  # delay is in frame #0
                    freeze_frame = frames[-1]
                for j in range(action.frames_delay()):
                    result.append(freeze_frame)
            else:
                raise FrameError(f"Unknown action {type(action)}")
        else:
            raise FrameError(f"Invalid frame number {frame_length}, must be 1 or {blinkt.NUM_PIXELS}")
    return result


class FrameCollection(object):
    def __init__(self, frames:list = None, mirrored=False, loop=True):
        self.input_frames = frames if frames else []
        self.frames = frames.copy() if frames else None
        self.length = len(self.frames) if frames else 0 # set after compiling
        self.mirrored = mirrored
        self.is_dynamic = False
        self.is_loop = loop
        self.is_empty = False if frames else True
        self._analyse()
        if self.is_dynamic:
            self.compile()
        if self.mirrored:
            self.mirror()
        self.frame_n = 0

    def get_frame(self):
        return self.frames[self.frame_n]

    def next(self):
        if self.is_loop:
            self.frame_n = self.frame_n + 1
            if self.frame_n >= self.length:
                if self.is_dynamic:
                    self.compile()
                self.frame_n = 0
        else:
            self.frames.pop(0)

    def _analyse(self):
        print("analyzing")
        for frame in self.input_frames:
            if len(frame) != blinkt.NUM_PIXELS:
                self.is_dynamic = True
                break

    def mirror(self):
        self.frames = mirror_frames(self.frames)
        self.mirrored = not self.mirrored

    def compile(self):
        print("compiling")
        self.frames = compile_frames(self.input_frames)
        self.length = len(self.frames)




class EffectBase(object):
    def __init__(self, frames, fps=5, mirrored=False, overlay=None, underlay=None, brightness=None):
        self.brightness = 0.2 if not brightness else brightness
        self.fps = fps
        self.frames = frames
        self.overwrite = FrameCollection()
        self.underlay = FrameCollection(frames=underlay, mirrored=mirrored) if underlay else FrameCollection()
        self.underlay_n = 0
        self.overlay = FrameCollection(frames=overlay, mirrored=mirrored) if overlay else FrameCollection()
        self.overlay_n = 0
        self.mirrored = mirrored
        self.frame_collection = FrameCollection(frames=frames, mirrored=mirrored)
        self.current_frame = self.frame_collection.get_frame()

    def mirror(self):
        self.frames.mirror()
        self.underlay.mirror()
        self.overlay.mirror()
        self.mirrored = not self.mirrored  # toggle

    def step(self):
        """Execute frame"""
        for i in range(blinkt.NUM_PIXELS):
            blinkt.set_pixel(i, *self.current_frame[i])  #, brightness=self.brightness)
        blinkt.show()
        self.custom_action()
        self._next_frame()

    def add_overwrite(self, frames):
        """Replace running frames with other frames"""
        self.overwrite = FrameCollection(frames=frames, mirrored=self.mirrored, loop=False)

    def add_underlay(self, frames):
        """Merge running frames with other frames"""
        self.underlay = FrameCollection(frames=frames, mirrored=self.mirrored)

    def add_overlay(self, frames):
        """Merge running frames with other frames"""
        self.overlay = FrameCollection(frames=frames, mirrored=self.mirrored)

    def custom_action(self):
        """Can be used in inherited classes"""
        pass

    def _next_frame(self):
        """Go to the next frame"""
        self.current_frame = self.frame_collection.get_frame()
        self.frame_collection.next()

        if not self.overwrite.is_empty:  # overwrites the frame
            self.current_frame = self.overwrite.get_frame()
            self.overwrite.next()
            return  # frame is overwritten, so no need for over-/underlays
        if not self.underlay.is_empty:  # adds another frame under the original frame
            self.current_frame = merge_frame(self.underlay.get_frame(), self.current_frame)
            self.underlay.next()
        if not self.overlay.is_empty:  # adds another frome over the original frame
            self.current_frame = merge_frame(self.current_frame, self.overlay.get_frame())
            self.overlay.next()

    def loop(self):
        """Run through the frames until stopped"""
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


