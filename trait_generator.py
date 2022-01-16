import random
from model import Trait

# Trait name for token id
TOKENID = "tokenId"


# Generates unique traits
class TraitGenerator:
    def __init__(self, total_images, layer_images_map):
        self.total_images = total_images
        # {Layer:[Image]}
        self.layer_images_map = layer_images_map
        # [{trait_name : trait_value}]
        # For easier metadata writing purposes
        self.traits_for_meta = list()
        # [Trait]
        # Has more details, for image generation purposes
        self.traits = list()
        # {trait_name : {trait_value:num_occurrences_of_value}}
        # To track histogram of trait occurrences
        self.stats = dict()
        self._generate_unique_traits()
        self._generate_stats()

    # Function to generate a unique set of traits to create a single image
    # This checks the generated trait against member var traits list and regenerates
    # as many times required until unique
    def _create_combo(self):
        # Each layer is a trait. Select a random value for this layer using
        # the list of images available for that layer.
        trait = dict()
        trait_full = dict()
        for layer, images in self.layer_images_map.items():
            rarities = [i.rarity for i in images]
            chosen_img = random.choices(images, rarities)[0]
            trait[layer.trait_name] = chosen_img.trait_value
            trait_full[layer] = chosen_img

        if trait in self.traits_for_meta:
            return self._create_combo()
        else:
            return trait, Trait(trait_full)

    # Function to double check if all traits are unique
    def _all_unique(self, x):
        seen = list()
        return not any(i in seen or seen.append(i) for i in x)

    def _generate_unique_traits(self):
        for i in range(self.total_images):
            combo = self._create_combo()
            self.traits_for_meta.append(combo[0])
            self.traits.append(combo[1])

        if not self._all_unique(self.traits_for_meta):
            raise Exception('Found duplicates in generated traits. This should not have happened. Contact devs.')
        print(f'Generated {len(self.traits_for_meta)} traits and confirmed uniqueness')

        # Add token id to traits - do this after the unique check because
        # everything will look unique otherwise due to the token id
        i = 0
        for tr in self.traits_for_meta:
            # tr is {trait_name:trait_value}
            tr[TOKENID] = i
            i = i + 1
        i = 0
        for tr in self.traits:
            # tr is a Trait
            tr.token_id = i
            i = i + 1

    def _generate_stats(self):
        for name in self.traits_for_meta[0]:
            if name != TOKENID:
                self.stats[name] = dict()

        # Get a grand total of each trait across all images
        for trait in self.traits_for_meta:
            for name, value in trait.items():
                if name != TOKENID:
                    self.stats[name][value] = self.stats[name][value] + 1 if value in self.stats[name] else 1


def dump_traits_for_meta(traits):
    for trait in traits:
        for name, value in trait.items():
            print(f'{name} : {value}')
        print()


def dump_traits(traits):
    for trait in traits:
        print(f'Token {trait.token_id}')
        for name, value in trait.layer_image_map.items():
            print(f'{name.trait_name} - {value.trait_value}')
        print()


def dump_stats(stats):
    for key, statset in stats.items():
        print(f'Stats for {key}')
        for name, value in statset.items():
            print(f'{name} : {value}')
        print()


if __name__ == '__main__':
    from configparser import Config
    from meta_writer import MetaWriter

    c = Config()
    t = TraitGenerator(c.total_images, c.layer_images_map)
    dump_traits(t.traits)

    m = MetaWriter(c.output_path, c.metadata_options, t.traits_for_meta, t.stats)
    m.write()

