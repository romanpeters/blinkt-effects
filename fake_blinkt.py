"""
Simulate Blinkt! in the terminal for testing purposes
"""

import sys
from colr import color

NUM_PIXELS = 8
frame = ['\u25A0'] * 8


def set_clear_on_exit():
    pass


def set_pixel(x, r, g, b, brightness=None):
    global frame
    for i in range(len(frame)):
        if i == x:
            frame[i] = color('\u25A0', fore=(r, g, b))


def show():
    print("\r" + ' '.join(frame), end="")
    sys.stdout.flush()
