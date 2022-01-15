import json
import os
import os.path
from os.path import join
from model import Image, ImageOptions, MetadataOptions, Layer, Runtime


# Parses config.json and converts to data structures
class Config:
    def __init__(self):
        with open('config.json') as fd:
            self.config = json.load(fd)
        self.total_images = int(self.config["totalImages"])
        self.output_path = self.config["outputBasePath"]
        self.image_options = ImageOptions(self.config["imageOptions"])
        self.thumbnail_options = ImageOptions(self.config["thumbnailOptions"])
        self.metadata_options = MetadataOptions(self.config["metadataOptions"])
        self.layers_path = self.config["layers"]["layersBasePath"]
        self.rarity_delimiter = self.config["layers"]["rarityDelimiter"]
        self.layers = []
        for layer_options in self.config["layers"]["layersInOrder"]:
            self.layers.append(Layer(layer_options))
        self.layer_images_map = self._load_images_from_layers(self.layers, self.layers_path)
        # Purge layers that have no images
        self._remove_empty_layers()

        self.runtime = Runtime(self.config["runtime"])

    def _remove_empty_layers(self):
        for layer in self.layers:
            if layer not in self.layer_images_map:
                self.layers.remove(layer)

    # Return a dict {Layer : [Image]}
    def _load_images_from_layers(self, layers, layer_base):
        out = dict()
        for layer in layers:
            out[layer] = []
            relpath = join(layer_base, layer.path)
            for root, dirs, files in os.walk(relpath):
                for name in files:
                    if not name.startswith('.'):
                        out[layer].append(Image(join(root, name), self.rarity_delimiter))
            if len(out[layer]) == 0:
                # No images for this layer, remove the layer
                del out[layer]
            else:
                # Find which images don't have rarities set and give them one
                self._assign_rarities_if_missing(out[layer])

        return out

    def _assign_rarities_if_missing(self, images):
        total_prob = 0.0
        images_missing_rarity = 0
        for image in images:
            if image.rarity:
                total_prob = total_prob + image.rarity
            else:
                images_missing_rarity = images_missing_rarity + 1
        rarity_per_remaining = (100 - total_prob) / images_missing_rarity
        for image in images:
            if not image.rarity:
                image.rarity = rarity_per_remaining

    def dump(self):
        print(f'Total images: {self.total_images}')
        print(f'Output base path: {self.output_path}')
        print('\nMetadata options:')
        self.metadata_options.dump()
        print(f'\nLayers path: {self.layers_path}')
        print(f'Rarity delimiter: {self.rarity_delimiter}')
        print('\nImage Options:')
        self.image_options.dump()
        print('\nLayer Options:')
        for i,layer in enumerate(self.layers):
            print(f'Layer {i}:')
            layer.dump()
            print()
            images = self.layer_images_map[layer]
            print(f'{len(images)} images in this layer:')
            for image in images:
                image.dump()
                print()


if __name__ == '__main__':
    c = Config()
    c.dump()
