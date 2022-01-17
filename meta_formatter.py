# Format metadata for specific blockchain
from string import Template

from trait_generator import TOKENID


def _extract_attributes(trait):
    attr = []
    for k, v in trait.items():
        if k == TOKENID:
            continue
        attr.append({
            "trait_type": k,
            "value": v
        })
    return attr


class MetaFormatter:
    def __init__(self, options, image_format):
        self.options = options
        self.image_format = image_format

    # Return json for the given trait
    def format(self, trait):
        pass


class SolMetaFormatter(MetaFormatter):
    def __init__(self, options, image_format):
        super().__init__(options, image_format)

    def format(self, trait):
        data = self._template()
        data['name'] = data['name'].substitute({'name': self.options.name, 'id': trait[TOKENID]})
        data['symbol'] = data['symbol'].substitute({'symbol': self.options.extras['symbol']})
        data['description'] = data['description'].substitute({'description': self.options.description})
        data['external_url'] = data['external_url'].substitute({'external_url': self.options.external_url})
        data['image'] = data['image'].substitute({'extn': self.image_format})
        data['properties']['files'][0]['uri'] = data['properties']['files'][0]['uri'].substitute({'extn': self.image_format})
        data['properties']['files'][0]['type'] = data['properties']['files'][0]['type'].substitute({'extn': self.image_format})
        data['seller_fee_basis_points'] = self.options.extras['seller_fee_basis_points']
        data['edition'] = self.options.extras['edition']
        data['attributes'] = _extract_attributes(trait)
        data['properties']['creators'] = self.options.extras['creators']
        return data

    def _template(self):
        data = {
            'name': Template('$name #$id'),
            'symbol': Template('$symbol'),
            'description': Template('$description'),
            'seller_fee_basis_points': 0,
            'image': Template('image.$extn'),
            'external_url': Template('$external_url'),
            'edition': 0,
            'attributes': None,
            'properties': {
                'files': [
                    {
                        'uri': Template('image.$extn'),
                        'type': Template('image/$extn')
                    }
                ],
                'category': 'image',
                'creators': None
            },
            'compiler': 'Camo Crocs NFT Engine'
        }
        return data


class EthMetaFormatter(MetaFormatter):
    def __init__(self, options, image_format):
        super().__init__(options, image_format)

    def format(self, trait):
        data = self._template()
        data['name'] = data['name'].substitute({'name': self.options.name, 'id': trait[TOKENID]})
        data['description'] = data['description'].substitute({'description': self.options.description})
        data['external_url'] = data['external_url'].substitute({'external_url': self.options.external_url})
        data['image'] = data['image'].substitute({'extn': self.image_format})
        data['attributes'] = _extract_attributes(trait)
        return data

    def _template(self):
        data = {
            'name': Template('$name #$id'),
            'description': Template('$description'),
            'image': Template('image.$extn'),
            'external_url': Template('$external_url'),
            'attributes': None,
            'compiler': 'Camo Crocs NFT Engine'
        }
        return data

