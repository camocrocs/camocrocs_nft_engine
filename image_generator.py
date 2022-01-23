from PIL import Image
from math import floor
from concurrent.futures import ProcessPoolExecutor
from os.path import join
import pathlib


# Generates images based on traits
class ImageGenerator:
    # layers_in_order = [Layer] in the order to be rendered
    # traits_full = [{Layer:Image}]
    def __init__(self, traits_full, config):
        self.traits = traits_full
        self.layers = config.layers
        self.image_options = config.image_options
        self.generate_thumbnails = config.generate_thumbnails
        self.thumbnail_options = config.thumbnail_options
        self.image_path = join(config.output_path, 'images')
        self.thumbnail_path = join(config.output_path, 'thumbnails')
        self.runtime = config.runtime

    def start(self):
        pathlib.Path(self.image_path).mkdir(parents=True, exist_ok=True)
        pathlib.Path(self.thumbnail_path).mkdir(parents=True, exist_ok=True)

        if self.runtime.use_concurrency:
            with ProcessPoolExecutor() as executor:
                executor.map(self._create_an_image, self.traits, chunksize=floor(len(self.traits)/self.runtime.cores))
        else:
            for t in self.traits:
                self._create_an_image(t)

    def _create_an_image(self, trait):
        # This is called once per trait
        blend = None
        for i, layer in enumerate(self.layers):
            # For each layer, render the chosen trait
            chosen_im = trait.layer_image_map[layer]
            im = Image.open(chosen_im.filename).convert('RGBA')
            blend = Image.alpha_composite(blend, im) if blend else im

        # Resize
        blend = blend.convert('RGB').resize((self.image_options.width, self.image_options.height), Image.LANCZOS)
        # Save final image
        file_name = f'{trait.token_id}{self.image_options.extn}'
        blend.save(f'{self.image_path}/{file_name}', quality=self.image_options.jpg_quality)
        # And thumbnail if enabled
        if self.thumbnail_options:
            thumb = blend.convert('RGB').resize((self.thumbnail_options.width, self.thumbnail_options.height))
            thumb_file = f'{trait.token_id}{self.thumbnail_options.extn}'
            thumb.save(f'{self.thumbnail_path}/{thumb_file}', quality=self.thumbnail_options.jpg_quality)
        print(f'{trait.token_id} generated')


if __name__ == '__main__':
    from configparser import Config
    from trait_generator import TraitGenerator

    c = Config()
    t = TraitGenerator(c)
    t.generate()
    i = ImageGenerator(t.traits, c)
    i.start()
