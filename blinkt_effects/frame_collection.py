#!/usr/bin/env python

try:
    import blinkt
except ImportError:
    import fake_blinkt as blinkt
from sprite_loader import Sprite

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
            if action.action_type == "variable_delay":
                for j in range(action.frames_delay()):
                    result.append(previous_frame)
            else:
                raise FrameError(f"Unknown action {type(action)}")
        else:
            raise FrameError(f"Invalid frame number {frame_length}, must be 1 or {blinkt.NUM_PIXELS}")
    return result


class FrameCollection(object):
    def __init__(self, frames:list or str, mirrored=False, loop=True):
        if type(frames) == str:
            if frames.lower().endswith('.png'):
                frames = Sprite(frames).get_frames()
            else:
                FrameError("Frames path doesn't look like it's a PNG file")

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



