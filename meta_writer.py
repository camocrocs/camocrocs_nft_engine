import pathlib
import json
from os.path import join
from meta_formatter import SolMetaFormatter, EthMetaFormatter
from trait_generator import TOKENID

FORMAT_SOLANA = "solana"
FORMAT_ETH = "ethereum"


# Writes generated metadata to files
class MetaWriter:
    # options = MetadataOptions
    # trait = TraitGenerator.traits_for_meta
    # stats = TraitGenerator.stats
    def __init__(self, base_output_path, image_extn, options, traits, stats):
        self.traits = traits
        self.stats = stats
        self.base_output_path = base_output_path
        self.meta_path = join(base_output_path, options.path)
        self.options = options
        self.image_format = image_extn[1:] if image_extn.startswith('.') else image_extn

    def write(self):
        self._write_aggregate()
        self._write_individual_meta()

    def _write_aggregate(self):
        pathlib.Path(self.base_output_path).mkdir(parents=True, exist_ok=True)
        with open(join(self.base_output_path, '_metadata.json'), 'w') as fd:
            json.dump(self.traits, fd, indent=4)
        with open(join(self.base_output_path, '_stats.json'), 'w') as fd:
            json.dump(self.stats, fd, indent=4)

    def _write_individual_meta(self):
        pathlib.Path(self.meta_path).mkdir(parents=True, exist_ok=True)
        formatter = SolMetaFormatter(self.options, self.image_format) if self.options.format == FORMAT_SOLANA else EthMetaFormatter(self.options)
        for trait in self.traits:
            with open(join(self.meta_path, f'{trait[TOKENID]}.json'), 'w') as f:
                json.dump(formatter.format(trait), f, indent=2)


if __name__ == '__main__':
    from configparser import Config
    from meta_writer import MetaWriter
    from trait_generator import TraitGenerator

    c = Config()
    t = TraitGenerator(c.total_images, c.layer_images_map)
    m = MetaWriter(c.output_path, c.image_options.extn, c.metadata_options, t.traits_for_meta, t.stats)
    m.write()
