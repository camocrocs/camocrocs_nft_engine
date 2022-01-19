import os.path
from multiprocessing import cpu_count

# Data structures shared between modules
class ImageOptions:
    def __init__(self, options):
        self.path = options["outputPath"]
        self.extn = f'.{options["format"]}'
        self.jpg_quality = int(options["jpgQuality"])
        self.width = int(options["width"])
        self.height = int(options["height"])

    def dump(self):
        print(f'Path: {self.path}')
        print(f'Extension: {self.extn}')
        if self.extn == '.jpg':
            print(f'JPG Quality: {self.jpg_quality}')
        print(f'Resolution: {self.width}x{self.height}')


class MetadataOptions:
    def __init__(self, options):
        self.path = options["outputPath"]
        self.format = options["format"]
        self.name = options["name"]
        self.description = options["description"]
        self.external_url = options["externalUrl"]
        self.extras = options["extras"]

    def dump(self):
        print(f'Path: {self.path}')
        print(f'Format: {self.format}')
        print(f'Name: {self.name}')
        print(f'Description: {self.description}')
        print(f'External URL: {self.external_url}')
        print(f'Extras: {self.extras}')


class MetadataUpdateOptions:
    def __init__(self, basepath, metapath, format, total_images, options):
        self.uri_file = os.path.join(basepath, options["imageUris"])
        self.meta_path = os.path.join(basepath, metapath)
        self.format = format
        self.count = total_images

    def dump(self):
        print(f'URI file: {self.uri_file}')
        print(f'Meta path: {self.meta_path}')
        print(f'Format: {self.format}')
        print(f'Count: {self.count}')


# Represents a single image and its rarity
# Format must be png
class Image:
    def __init__(self, filename, rarityDelimiter):
        self.filename = filename
        self.trait_value, self.rarity = self._parse_rarity(filename, rarityDelimiter)

    # Return (trait value, rarity)
    def _parse_rarity(self, filename, rarityDelimiter):
        basename, _ = os.path.splitext(filename)
        rarity = None
        t = basename.split(rarityDelimiter)
        traitval = os.path.basename(t[0])
        if len(t) > 1:
            rarity = float(t[1])
        return (traitval, rarity)

    def dump(self):
        print(f'Trait Value: {self.trait_value}')
        print(f'Rarity: {self.rarity}')
        print(f'Filename: {self.filename}')


# Represents a layer such as background or headgear
class Layer:
    def __init__(self, options):
        self.path = options["path"]
        try:
            self.trait_name = options["traitName"]
        except:
            self.trait_name = self.path
        try:
            self.opacity = options["opacity"]
        except:
            self.opacity = 255

    def dump(self):
        print(f'Path: {self.path}')
        print(f'Trait name: {self.trait_name}')
        print(f'Opacity: {self.opacity}')


class Runtime:
    def __init__(self, options):
        self.use_concurrency = bool(options["useConcurrency"])
        self.cores = cpu_count()
        self.use_random_seed = bool(options["useRandomSeed"])
        self.random_seed = int(options["randomSeed"]) if self.use_random_seed else 0


class Trait:
    # layer_image_map = {Layer: Image}
    def __init__(self, layer_image_map, token_id=0):
        self.token_id = token_id
        self.layer_image_map = layer_image_map


