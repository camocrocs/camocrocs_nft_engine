import json

class ImageOptions:
    def __init__(self, options):
        self.path = options["outputPath"]
        self.extn = f'.{options["format"]}'
        self.jpg_quality = int(options["jpgQuality"])
        self.width = int(options["width"])
        self.height = int(options["height"])

class Config:
    def __init__(self):
        with open('config.json') as fd:
            self.config = json.load(fd)
        self.total_images = int(self.config["totalImages"])
        self.layers_path = self.config["layersBasePath"]
        self.output_path = self.config["outputBasePath"]
        self.total_images = self.config["totalImages"]
        self.image_options = ImageOptions(self.config["imageOptions"])
        self.thumbnail_options = ImageOptions(self.config["thumbnailOptions"])
        self.metadata_path = self.config["metadataOptions"]["outputPath"]
