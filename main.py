import sys
import time
import os
import argparse
from bomist.bomist import BomistApi
from pcb.genericjson import GenericJsonPcbData

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='JSON board file')
    parser.add_argument('-b', '--bomist',
                        help="BOMIST project - syntax: MPN,REVCODE,BUILDCODE")
    args = parser.parse_args()

    filename_in = args.filename
    print("Processing {}".format(filename_in))
    print("Using BOMIST Project {}, Rev {}, Build {}".format(
          *tuple(args.bomist.split(','))))

    bomist = BomistApi()
    # build_tree = bomist.project_build_tree()

    bomist = BomistApi()
    build = bomist.get_build_by_names(*tuple(args.bomist.split(',')))
    bom_entries = []
    build_items = [b['project_build_item'] for b in build]
    for build_item in build_items:
        designators = build_item['bom_entry']['designators']
        for d in designators:
            if build_item['source'] != '':
                source = bomist.get_storage(build_item['source'])
                source = source[0]['storage']['fullName']
            else:
                source = ''
            mpn = '' if 'part' not in build_item else build_item['part']['mpn']
            bom_entries.append({'ref': d,
                                'source': source,
                                'dnp': build_item['bom_entry']['dnp'],
                                'value': build_item['bom_entry']['value'],
                                'mpn': mpn,
                                'package': build_item['bom_entry']['package']
                                })
    foo = GenericJsonPcbData(filename_in)

    for c in foo.component_data:
        index = [b['ref'] for b in bom_entries].index(c.ref)
        b = bom_entries[index]
        c.val = b['value']
        c.mpn = b['mpn']
        c.bomist_source = b['source']
        c.footprint = b['package']
        c.dnp = b['dnp']

    path, file = os.path.split(filename_in)
    root, ext = os.path.splitext(file)
    filename_out = os.path.join(path, "{r}_bomist{e}".format(r=root, e=ext))
    foo.save(filename_out)
    print("Finished processing, saved {}".format(filename_out))
