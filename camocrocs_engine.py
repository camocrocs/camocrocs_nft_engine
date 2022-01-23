from configparser import Config
from meta_writer import MetaWriter
from trait_generator import TraitGenerator
from image_generator import ImageGenerator
from prechecker import Prechecker
from validator import Validator
from os.path import abspath

if __name__ == '__main__':
    print('Parsing config...')
    config = Config()

    print('Doing a sanity check on your inputs...')
    prechecker = Prechecker(config)
    ret = prechecker.validate()
    if not ret:
        print('Your input has problems. Check the output above and fix them first.')
        exit(1)

    print('\nGenerating unique traits...')
    traitgen = TraitGenerator(config)
    try:
        traitgen.generate()
    except Exception as ex:
        print(f'You have too few base images for a collection of {config.total_images}. Try something less than {ex}.')
        exit(1)
    print('\nWriting metadata...')
    metawriter = MetaWriter(traitgen.traits_for_meta, traitgen.stats, config)
    metawriter.write()
    print('\nGenerating images...')
    imagegen = ImageGenerator(traitgen.traits, config)
    imagegen.start()
    print(f'\nVerifying generated output...')
    validator = Validator(config)
    validator.validate()
    print(f'\nDone. Check {abspath(config.output_path)} for generated output.')
    print('\n**********************************************************************')
    print('Thanks for using Camo Crocs NFT engine. Good luck with your project!')
    print('**********************************************************************')
