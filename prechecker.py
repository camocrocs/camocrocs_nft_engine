import os
from os.path import join
from pathlib import Path
import json
from configparser import FORMAT_SOLANA
from PIL import Image

ok = '\u2713'
notok = '\u2717'


class Prechecker:
    def __init__(self, config):
        self.config = config

    def validate(self):
        ret = True
        total = self.config.total_images
        width = self.config.input_width
        height = self.config.input_height
        # Check if all images are png and of correct resolution
        # {Layer: [Image]}
        print('Checking base layers')
        for layer, images in self.config.layer_images_map.items():
            for im in images:
                im = Image.open(im.filename)
                if im.width != width or im.height != height:
                    print(f'{notok} Expected {im.filename} to be of resolution {width}x{height} but it is {im.width}x{im.height}')
                    ret = ret and False
                if im.format != 'PNG':
                    print(f'{notok} Expected {im.filename} to be a PNG but it is {im.format}')
                    ret = ret and False

        if ret:
            print(f'{ok} All checks passed')
        else:
            print(f'{notok} Some checks failed')
        return ret


if __name__ == '__main__':
    from configparser import Config

    c = Config()
    v = Prechecker(c)
    v.validate()
