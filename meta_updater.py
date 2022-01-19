import csv
import json
from os.path import join


# Updates generated metadata files with image URI
# The URIs come from the file specified in metadataUpdateOptions.imageUris property
# The value is specified relative to base output folder. So if output folder is
# "output" and you have a file _imageuris.csv inside, just specify _imageuris.csv.
#
# The csv file must be of the format
# tokenId,<URI or IPFS hash>
# For example,
# 0,hash0
# 1,hash1
# ...
# You could also specify
# 0,https://arweave.net/<something>
# If the second token does not look like a URI, it is treated as IPFS hash and
# prefixed with https://ipfs.io/ipfs/

class MetaUpdater:
    # options = MetadataUpdateOptions
    def __init__(self, options):
        self.options = options
        self.db = self._load_uris()

    def start(self):
        for i in range(0, self.options.count):
            path = join(self.options.meta_path, f'{i}.json')
            meta = self._load_meta_file(path)
            meta = self._update(i, meta)
            self._save(path, meta)

    # Convert the csv file to dictionary {int_token:uri}
    def _load_uris(self):
        with open(self.options.uri_file, mode='r', newline='') as fd:
            reader = csv.reader(fd)
            return {int(rows[0]): rows[1] if '//' in rows[1] else f'https://ipfs.io/ipfs/{rows[1]}' for rows in reader}

    def _load_meta_file(self, path):
        with open(path, 'r') as fd:
            return json.load(fd)

    def _update(self, token_id, meta):
        pass

    def _save(self, path, meta):
        with open(path, 'w') as fd:
            json.dump(meta, fd, indent=4)


class SolMetaUpdater(MetaUpdater):
    def __init__(self, options):
        super().__init__(options)

    def _update(self, token_id, meta):
        meta["image"] = self.db[token_id]
        meta["properties"]["files"][0]["uri"] = self.db[token_id]
        return meta


class EthMetaUpdater(MetaUpdater):
    def __init__(self, options):
        super().__init__(options)

    def _update(self, token_id, meta):
        meta["image"] = self.db[token_id]
        return meta


if __name__ == '__main__':
    from configparser import Config, FORMAT_SOLANA

    c = Config()
    u = SolMetaUpdater(c.metadata_update_options) if \
        c.metadata_options.format == FORMAT_SOLANA else EthMetaUpdater(c.metadata_update_options)
    u.start()
