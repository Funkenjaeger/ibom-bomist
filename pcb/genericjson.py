import io
import json
import jsonschema


class GenericJsonPcbData:
    """Data object representing PCB data imported from JSON."""
    def __init__(self, filename):
        self.filename = filename
        self._pcb = None
        self.load(self.filename)

    def _process_components(self, components):
        self.component_data = []
        for c in components:
            self.component_data.append(Component(c))

    def load(self, filename):
        with io.open(filename, 'r') as f:
            self._pcb = json.load(f)
        self._process_components(self._pcb['components'])

    def to_table(self):
        return [c.as_dict_row() for c in self.component_data]


class Component(object):
    """Simple data object to store component data needed for bom table."""

    def __init__(self, c):
        self.ref = c['ref']
        self.val = c['val']
        self.footprint = c['footprint']
        self.layer = c['layer']
        self.attr = c.get('attr', '')
        self.extra_fields = c.get('extra_fields',{})
        self.mpn = self.extra_fields.pop('mpn', '')
        self.bomist_source = self.extra_fields.pop('bomist_source', '')

    def as_genericjson(self):
        # TODO: implement exporting more stuff, especially location
        extra_fields = self.extra_fields
        extra_fields['mpn'] = self.mpn
        extra_fields['bomist_id'] = self.bomist_id
        return {'attr': self.attr, 'footprint': self.footprint,
                'layer': self.layer, 'ref': self.ref, 'val': self.val,
                'extra_fields': extra_fields}

    def as_dict_row(self):
        return {'ref': self.ref, 'footprint': self.footprint, 'val': self.val,
                'mpn': self.mpn, 'source': self.bomist_source}
