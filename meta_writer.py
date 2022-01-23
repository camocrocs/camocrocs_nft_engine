import pathlib
import json
from concurrent.futures import ProcessPoolExecutor
from os.path import join
from meta_formatter import SolMetaFormatter, EthMetaFormatter
from configparser import FORMAT_SOLANA
from trait_generator import TOKENID
from functools import partial
from math import floor


# Writes generated metadata to files
class MetaWriter:
    # options = MetadataOptions
    # trait = TraitGenerator.traits_for_meta
    # stats = TraitGenerator.stats
    def __init__(self, traits, stats, config):
        self.traits = traits
        self.stats = stats
        self.base_output_path = config.output_path
        self.meta_path = join(config.output_path, config.metadata_options.path)
        self.options = config.metadata_options
        extn = config.image_options.extn
        self.image_format = extn[1:] if extn.startswith('.') else extn
        self.runtime = config.runtime

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
        formatter = SolMetaFormatter(self.options, self.image_format) if self.options.format == FORMAT_SOLANA else EthMetaFormatter(self.options, self.image_format)
        if self.runtime.use_concurrency:
            with ProcessPoolExecutor() as executor:
                executor.map(partial(self._write_a_trait, formatter), self.traits, chunksize=floor(len(self.traits) / self.runtime.cores))
        else:
            for t in self.traits:
                self._write_a_trait(formatter, t)

    def _write_a_trait(self, formatter, trait):
        with open(join(self.meta_path, f'{trait[TOKENID]}.json'), 'w') as f:
            print(f'Writing {trait[TOKENID]}.json')
            json.dump(formatter.format(trait), f, indent=2)


if __name__ == '__main__':
    from configparser import Config
    from meta_writer import MetaWriter
    from trait_generator import TraitGenerator

    c = Config()
    t = TraitGenerator(c)
    t.generate()
    m = MetaWriter(t.traits_for_meta, t.stats, c)
    m.write()
