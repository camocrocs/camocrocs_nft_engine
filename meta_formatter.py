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
        # data['attributes'] = extract_attributes(imgdata)
        data['name'] = data['name'].substitute({'name': self.options.name, 'id': trait[TOKENID]})
        data['symbol'] = data['symbol'].substitute({'symbol': self.options.symbol})
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
            }
        }
        return data


class EthMetaFormatter(MetaFormatter):
    def __init__(self, options):
        super().__init__(options)


"""
def meta_template():
    data = {
        'name': Template('Camo Crocs #$id'),
        'symbol': 'CROC',
        'description': "Officers! We have confirmed that thousands of naughty crocodiles are crawling around the blockchain. Intel has it that they are masters of camouflage and can blend in with anything. The environment, other animals, humans ... it is suspected that they even impersonate different cultures. Don't get too close, they bite worse than people. Your mission is to catch them all and assign owners bold enough to tame them.",
        'seller_fee_basis_points': 500,
        'image': Template('http://ipfs.io/ipfs/$uri'),
        'external_url': 'https://www.camocrocsnft.com',
        'edition': 0,
        'attributes': None,
        'properties': {
            'files': [
                {
                    'uri': Template('http://ipfs.io/ipfs/$uri'),
                    'type': 'image/jpg'
                }
            ],
            'category': 'image',
            'creators': [
                {
                    'address': 'F8dgEJPJCtroKb6ykozT6n9y1xPoNx7j3Uo3eeBYZASo',
                    'share': 100
                }
            ]
        }
    }
    return data
"""
