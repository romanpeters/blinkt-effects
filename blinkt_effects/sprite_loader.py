from PIL import Image


class Sprite(object):
    def __init__(self, path):
        self.path = path
        self.img = Image.open(path)
        self.data = self.img.getdata()
        self.red = [d[0] for d in self.data]
        self.green = [d[1] for d in self.data]
        self.blue = [d[2] for d in self.data]

    def get_frames(self):
        """Convert image data to a list of RGB values, parseable by FrameCollection"""
        result = []
        line = []
        for (r, g, b) in zip(self.red, self.green, self.blue):
            pixel = (r, g, b)
            line.append(pixel)
            if len(line) == self.img.size[0]:  # image width reached
                result.append(line)
                line = []
        return result