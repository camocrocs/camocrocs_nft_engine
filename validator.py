import os
from os.path import join
from pathlib import Path
import json
from configparser import FORMAT_SOLANA

ok = '\u2713'
notok = '\u2717'


# Verifies that the output matches the configuration
def _compare(total, extn, path):
    expected_files = []
    for i in range(0, total):
        expected_files.append(f'{i}{extn}')

    found_files = []
    for root, dirs, files in os.walk(path):
        for name in files:
            found_files.append(name)

    ec = len(expected_files)
    fc = len(found_files)
    ret = False
    if ec >= fc:
        diff = [item for item in expected_files if item not in found_files]
    else:
        diff = [item for item in found_files if item not in expected_files]
    if ec == fc:
        if len(diff) == 0:
            print(f'{ok} Expected number of files ({ec}) and file names matched')
            ret = True
        else:
            print(f'{notok} Expected number of files ({ec}) found but content differs. Expected list has the following items that were not found: {diff}')
    elif ec > fc:
        print(f'{notok} Expected {ec} files but found {fc}. Expected list has the following items that were not found: {diff}')
    else:
        print(f'{notok} Expected {ec} files but found {fc}. Found list has the following items that were not expected: {diff}')
    return ret


def _exists(file):
    if Path(file).is_file():
        print(f'{ok} {file} exists')
        return True
    print(f'{notok} Expected to find {file} but it is missing')
    return False


def _matches(expected, found, file):
    if expected != found:
        print(f'{notok} Expected {expected} in {file} but found {found}')
        return False
    return True


class Validator:
    def __init__(self, config):
        self.config = config

    def validate(self):
        ret = True
        total = self.config.total_images
        # Validate image count
        print('Checking images')
        imagepath = join(self.config.output_path, self.config.image_options.path)
        ret = ret and _compare(total, self.config.image_options.extn, imagepath)

        # Validate metadata count
        print('Checking metadata')
        metapath = join(self.config.output_path, self.config.metadata_options.path)
        ret = ret and _compare(total, '.json', metapath)

        # Validate presence of metadata and stats files
        aggmeta = join(self.config.output_path, '_metadata.json')
        ret = ret and _exists(aggmeta)
        ret = ret and _exists(join(self.config.output_path, '_stats.json'))

        # Check if aggregate meta has entries for expected number of files
        with open(aggmeta, 'r') as fd:
            meta = json.load(fd)
        if len(meta) == total:
            print(f'{ok} Found {total} entries in {aggmeta} as expected')
        else:
            print(f'{notok} Expected {total} entries in {aggmeta} but found {len(meta)}')

        # Verify that metadata files have expected name, description etc.
        print(f'Checking if each metadata file has the expected name, description and all that crap')
        for i in range(0, total):
            file = join(metapath, f'{i}.json')
            with open(file, 'r') as fd:
                meta = json.load(fd)
                ret = ret and _matches(f'{self.config.metadata_options.name} #{i}', meta["name"], file)
                ret = ret and _matches(self.config.metadata_options.description, meta["description"], file)
                ret = ret and _matches(self.config.metadata_options.external_url, meta["external_url"], file)
                # Check blockchain specifics
                if self.config.metadata_options.format == FORMAT_SOLANA:
                    ret = ret and _matches(f'{self.config.metadata_options.extras["symbol"]}', meta["symbol"], file)
                    ret = ret and _matches(str(f'{self.config.metadata_options.extras["edition"]}'), str(meta["edition"]), file)
                    ret = ret and _matches(int(f'{self.config.metadata_options.extras["seller_fee_basis_points"]}'), int(meta["seller_fee_basis_points"]), file)
                    expected = self.config.metadata_options.extras["creators"]
                    found = meta["properties"]["creators"]
                    ret = ret and _matches(expected, found, file)

                # Check if attribute counts match

        # Verify if images are the expected resolution

        if ret:
            print(f'{ok} All checks passed')
        else:
            print(f'{notok} Some checks failed')


if __name__ == '__main__':
    from configparser import Config

    c = Config()
    v = Validator(c)
    v.validate()
