import time
from frame_collection import FrameCollection
from sprite_loader import Sprite

try:
    import blinkt
except ImportError:
    import fake_blinkt as blinkt


blinkt.set_clear_on_exit()


OFF = (0, 0, 0)

def merge_frame(under_frame: list, over_frame: list) -> list:
    new_frame = under_frame
    for i in range(len(new_frame)):
        if type(over_frame[i]) != tuple or type(under_frame[i]) != tuple:
            pass
        elif over_frame[i] != OFF:
            new_frame[i] = over_frame[i]
    return new_frame



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
        self._next_frame()

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

    def play(self):
        self.step()
        time.sleep(1 / self.fps)

    def loop(self):
        """Run through the frames until stopped"""
        try:
            while True:
                self.play()
        except KeyboardInterrupt:
            pass



class Effect(EffectBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)