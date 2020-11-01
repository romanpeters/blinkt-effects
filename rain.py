from base import EffectBase, VariableDelay
import random

class Drip(EffectBase):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.frames = raindrop_falling
        self.fps = 3

class Rain(EffectBase):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.frames = raindrop_falling
        self.fps = 5

class ThunderRain(EffectBase):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.frames = raindrop_falling
        self.fps = 5

    def _custom_action(self):
        if random.randint(0, 10) == 1:
            self.overwrite = thunder_flash.copy()

raindrop_falling = [
    [(0, 0, 255), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)],
    [(VariableDelay(1, 3))],
    [(0, 0, 0), (0, 0, 255), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)],
    [(0, 0, 0), (0, 0, 0), (0, 0, 255), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)],
    [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 255), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)],
    [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 255), (0, 0, 0), (0, 0, 0), (0, 0, 0)],
    [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 255), (0, 0, 0), (0, 0, 0)],
    [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 255), (0, 0, 0)],
    [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 255)],
    [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)],
    [(VariableDelay(0, 2))]
]

thunder_flash = [
    [(100, 100, 100), (100, 100, 100), (100, 100, 100), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)],
    [(255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255)],
]

if __name__=="__main__":
    rain = Rain().loop()