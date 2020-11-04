"""
CLI bindings
"""

import click
from effects_base import Effect
from effects import weather, other

available_frames = {'raindrop_falling': weather.raindrop_falling,
                    'raindrop_dripping': weather.raindrop_dripping,
                    'flood': weather.flood,
                    'thunder_flash': weather.thunder_flash,
                    'snow_falling': weather.snow_falling,
                    'snow_layer': weather.snow_layer,
                    'knight_rider': other.knight_rider}


@click.command()
@click.option('--frames', prompt='Which frames?',
              help=', '.join(available_frames.keys()) + ', or specify the path to a PNG sprite')
@click.option('--fps', default=5, help='Frames per second')
@click.option('--brightness', default=0.2, help='LED brightness')
@click.option('--mirrored', default=False, help='Mirror all frames')
@click.option('--overlay', default=None, help='Put other frames over the frames')
@click.option('--underlay', default=None, help='Put other frames under the frames')

def run(frames, fps, brightness, mirrored, overlay, underlay):
    try:
        frames_obj = available_frames[frames]
    except KeyError:
        frames_obj = frames  # Let's just try it, and see if it's a file path
    if overlay:
        overlay = available_frames[overlay]
    if underlay:
        underlay = available_frames[underlay]
    effect = Effect(frames_obj, fps=fps, brightness=brightness, mirrored=mirrored, overlay=overlay, underlay=underlay)
    effect.loop()

run()