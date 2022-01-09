import random

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
        self.traits = list()
        # [{Layer : Image}]
        # Has more details, for image generation purposes
        self.traits_full = list()
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
            chosen = random.choices(images, rarities)[0]
            trait[layer.trait_name] = chosen.trait_value
            trait_full[layer] = chosen

        if trait in self.traits:
            return self._create_combo()
        else:
            return trait, trait_full

    # Function to double check if all traits are unique
    def _all_unique(self, x):
        seen = list()
        return not any(i in seen or seen.append(i) for i in x)

    def _generate_unique_traits(self):
        for i in range(self.total_images):
            combo = self._create_combo()
            self.traits.append(combo[0])
            self.traits_full.append(combo[1])

        print(f'Total Traits: {len(self.traits)}, Are Unique?: {self._all_unique(self.traits)}')

        # Add token id to traits - do this after the unique check because
        # everything will look unique otherwise due to the token id
        i = 0
        for item in self.traits:
            item[TOKENID] = i
            i = i + 1

    def _generate_stats(self):
        for name in self.traits[0]:
            if name != TOKENID:
                self.stats[name] = dict()

        # Get a grand total of each trait across all images
        for trait in self.traits:
            for name, value in trait.items():
                if name != TOKENID:
                    self.stats[name][value] = self.stats[name][value] + 1 if value in self.stats[name] else 1


def dump_traits(traits):
    for trait in traits:
        for name, value in trait.items():
            print(f'{name} : {value}')
        print()


def dump_traits_full(traits):
    for trait in traits:
        for name, value in trait.items():
            print(f'{name.trait_name} : {value.trait_value}')
        print()


def dump_stats(stats):
    for key, statset in stats.items():
        print(f'Stats for {key}')
        for name, value in statset.items():
            print(f'{name} : {value}')
        print()


if __name__ == '__main__':
    from configparser import Config

    c = Config()
    t = TraitGenerator(c.total_images, c.layer_images_map)
    dump_traits_full(t.traits_full)
    import json
    import os.path

    with open(f'{c.output_path}{os.path.sep}_metadata.json', 'w') as fd:
        json.dump(t.traits, fd, indent=4)
    with open(f'{c.output_path}{os.path.sep}_stats.json', 'w') as fd:
        json.dump(t.stats, fd, indent=4)
