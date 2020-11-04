from PIL import Image
import numpy as np


class Sprite(object):
    def __init__(self, path, gamma_correction=True, gamma=2.6, num_leds=8):
        self.path = path
        self.img = Image.open(path)
        self.num_leds = num_leds
        if self.img.size[1] == 1:  # image is height is 1 pixel
            self.scroll = True
        else:
            assert self.img.size[0] == num_leds, 'Image is a different width than the number of pixels'
            self.scroll = False
        if gamma_correction:
            corrected = np.array(255 * (np.array(self.img) / 255) ** gamma, dtype='uint8')
            self.img = Image.fromarray(corrected, 'RGB')
        self.data = self.img.getdata()
        self.red = [d[0] for d in self.data]
        self.green = [d[1] for d in self.data]
        self.blue = [d[2] for d in self.data]


    def get_frames(self):
        """Convert image data to a list of RGB values, parseable by FrameCollection"""
        result, line = [], []
        for (r, g, b) in zip(self.red, self.green, self.blue):
            pixel = (r, g, b)
            line.append(pixel)
            if len(line) == self.num_leds:  # image width reached
                result.append(line)
                if self.scroll:
                    line = line.copy()
                    line.pop(0)
                else:
                    line = []

        return result