from configparser import Config
from meta_writer import MetaWriter
from trait_generator import TraitGenerator
from image_generator import ImageGenerator
from os.path import abspath

if __name__ == '__main__':
    print('Parsing config...')
    config = Config()
    print('\nGenerating unique traits...')
    traitgen = TraitGenerator(config.total_images, config.layer_images_map)
    print('\nWriting metadata...')
    metawriter = MetaWriter(traitgen.traits_for_meta, traitgen.stats, config)
    metawriter.write()
    print('\nGenerating images...')
    imagegen = ImageGenerator(traitgen.traits, config)
    imagegen.start()
    print(f'\nDone. Check {abspath(config.output_path)} for generated output.')
    print('\n**********************************************************************')
    print('Thanks for using Camo Crocs NFT engine. Good luck with your project!')
    print('**********************************************************************')
