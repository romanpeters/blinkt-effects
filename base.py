#!/usr/bin/env python
import time
import random
import colorsys
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

            # actions usually modify the previous frame
            if result:  # action is not in frame #0
                previous_frame = result[-1]
            else:  # action is in frame #0
                raise FrameError("First frame can't be an action frame")

            # VariableDelay
            if type(action) == VariableDelay:
                for j in range(action.frames_delay()):
                    result.append(previous_frame)

            # BrightnessAdjust
            elif type(action) == LightnessAdjust:
                for j in range(action.repeat):
                    action.set_frame(previous_frame)
                    action.adjust()
                    frame = action.get_frame()
                    result.append(frame)
                    previous_frame = frame

            else:
                raise FrameError(f"Unknown action {type(action)}")
        else:
            raise FrameError(f"Invalid frame number {frame_length}, must be 1 or {blinkt.NUM_PIXELS}")
    return result


class FrameCollection(object):
    def __init__(self, frames:list, mirrored=False, loop=True):
        self.source_frames = frames
        self.frames = self.source_frames.copy()
        self.length = len(self.frames)  # set after compiling
        self.mirrored = mirrored
        self.is_dynamic = False
        self.is_loop = loop
        self._analyse()
        if self.is_dynamic:
            self.compile()
        if self.mirrored:
            self.mirror()
        self.cursor = 0

    def get_frame(self):
        frame = self.frames[self.cursor]
        self.next()
        return frame

    def next(self):
        if self.is_loop:
            self.cursor = self.cursor + 1
            if self.cursor >= self.length:
                if self.is_dynamic:
                    self.compile()
                self.cursor = 0
        else:
            self.frames.pop(0)

    def _analyse(self):
        for frame in self.source_frames:
            if len(frame) != blinkt.NUM_PIXELS:
                self.is_dynamic = True
                break

    def mirror(self):
        self.source_frames = mirror_frames(self.source_frames)
        self.frames = mirror_frames(self.frames)
        self.mirrored = not self.mirrored

    def compile(self):
        self.frames = compile_frames(self.source_frames)
        self.length = len(self.frames)


class EffectBase(object):
    def __init__(self, frames, fps=5, brightness=None, mirrored=False,
                 overlay=None, underlay=None):
        self.fps = fps
        self.brightness = 0.2 if not brightness else brightness
        self.mirrored = mirrored
        self.frame_collection = FrameCollection(frames=frames, mirrored=mirrored)
        self.underlay = FrameCollection(frames=underlay, mirrored=mirrored) if underlay else None
        self.overlay = FrameCollection(frames=overlay, mirrored=mirrored) if overlay else None
        self.overwrite = None  # can only be set after initialization
        self.current_frame = None

    def step(self):
        """Execute frame"""
        for i in range(blinkt.NUM_PIXELS):
            blinkt.set_pixel(i, *self.current_frame[i], brightness=self.brightness)
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

        if self.underlay:  # adds another frame under the original frame
            self.current_frame = merge_frame(self.underlay.get_frame(), self.current_frame)
        if self.overlay:  # adds another frome over the original frame
            self.current_frame = merge_frame(self.current_frame, self.overlay.get_frame())
        if self.overwrite:  # overwrites all of the above
            self.current_frame = self.overwrite.get_frame()

    def loop(self):
        """Run through the frames until stopped"""
        self._next_frame()
        try:
            while True:
                self.step()
                time.sleep(1/self.fps)
        except KeyboardInterrupt:
            pass


class Effect(EffectBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ActionBase(object):
    def __init__(self):
        self.frame = None
        self.hls = None

    def set_frame(self, frame):
        self.frame = frame

    def get_frame(self):
        return self.frame

class VariableDelay(ActionBase):
    def __init__(self, min_=0, max_=3):
        super().__init__()
        self.min = min_
        self.max = max_

    def frames_delay(self):
        return random.randint(self.min, self.max)


def rgb_to_hls(r, g, b) -> tuple:
    # https://stackoverflow.com/questions/15442285/converting-rgb-to-hls-and-back
    r, g, b = [x / 255.0 for x in (r, g, b)]
    print(f"RGB {r},{g},{b} = HLS {colorsys.rgb_to_hls(r, g, b)}")
    return colorsys.rgb_to_hls(r, g, b)


def hls_to_rgb(h, l, s) -> tuple:
    r, g, b = colorsys.hls_to_rgb(h, l, s)

    def limit(x):
        if x > 255:
            return 255
        elif x < 0:
            return 0
        return x
    print(f"HLS {h},{l},{s} = RGB {tuple([limit(x * 255.0) for x in (r, g, b)])}")
    return tuple([limit(x * 255.0) for x in (r, g, b)])


class HueAdjust(ActionBase):
    def __init__(self, increase, repeat):
        super().__init__()
        self.increase = increase
        self.repeat = repeat

    def adjust(self):
        for i in range(len(self.frame)):
            pixel = self.frame[i]
            if pixel != OFF:
                h, l, s = rgb_to_hls(*pixel)
                h += self.increase
                adjusted_pixel = hls_to_rgb(h, l, s)
                if adjusted_pixel != OFF:
                    self.frame[i] = adjusted_pixel

class LightnessAdjust(ActionBase):
    def __init__(self, increase, repeat):
        super().__init__()
        self.increase = increase
        self.repeat = repeat

    def adjust(self):
        for i in range(len(self.frame)):
            pixel = self.frame[i]
            if pixel != OFF:
                h, l, s = rgb_to_hls(*pixel)
                l += self.increase
                adjusted_pixel = hls_to_rgb(h, l, s)
                if adjusted_pixel != OFF:
                    self.frame[i] = adjusted_pixel


class SaturationAdjust(ActionBase):
    def __init__(self, increase, repeat):
        super().__init__()
        self.increase = increase
        self.repeat = repeat

    def adjust(self):
        for i in range(len(self.frame)):
            pixel = self.frame[i]
            if pixel != OFF:
                h, l, s = rgb_to_hls(*pixel)
                s += self.increase
                adjusted_pixel = hls_to_rgb(h, l, s)
                if adjusted_pixel != OFF:
                    self.frame[i] = adjusted_pixel





