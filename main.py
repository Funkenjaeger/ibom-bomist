import sys
import os
import argparse

from bomist.bomist import BomistApi

if __name__ == '__main__':
    ibom_dir = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
    ibom_dir = os.path.join(ibom_dir, 'InteractiveHtmlBom')
    ibom_dir = os.path.join(ibom_dir, 'InteractiveHtmlBom')
    sys.path.insert(0, os.path.dirname(ibom_dir))
    os.environ['INTERACTIVE_HTML_BOM_CLI_MODE'] = 'True'

    import InteractiveHtmlBom
    from InteractiveHtmlBom.core.config import Config
    from InteractiveHtmlBom.core import ibom
    from InteractiveHtmlBom.core.ibom import generate_file
    from InteractiveHtmlBom.ecad import get_parser_by_extension
    from InteractiveHtmlBom.version import version
    from InteractiveHtmlBom.errors import (ExitCodes,
                                           ParsingException,
                                           exit_error)

    parser = argparse.ArgumentParser(
        description='IndependentHtmlBom-BOMIST interface tool CLI',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('file', help='JSON board file')
    parser.add_argument('-b', '--bomist',
                        help="BOMIST project - syntax: MPN,REVCODE,BUILDCODE")
    config = Config(version)
    config.add_options(parser, config.FILE_NAME_FORMAT_HINT)
    args = parser.parse_args()
    logger = ibom.Logger(cli=True)
    if not os.path.isfile(args.file):
        exit_error(logger, ExitCodes.ERROR_FILE_NOT_FOUND,
                   "File %s does not exist." % args.file)
    print("Loading %s" % args.file)
    parser = get_parser_by_extension(os.path.abspath(args.file), config, logger)
    config.set_from_args(args)

    pcbdata, components = parser.parse()
    if not pcbdata and not components:
        raise ParsingException('Parsing failed.')

    print("Using BOMIST Project {}, Rev {}, Build {}".format(
          *tuple(args.bomist.split(','))))

    bomist = BomistApi()

    bomist = BomistApi()
    build = bomist.get_build_by_names(*tuple(args.bomist.split(',')))
    bom_entries = []
    build_items = [b['project_build_item'] for b in build]
    for build_item in build_items:
        designators = build_item['bom_entry']['designators']
        for d in designators:
            if build_item['sources']:
                inventory = bomist.get_storage(build_item['sources'][0]['inventory'])
                source = bomist.get_storage(inventory[0]['inventory']['storage'])
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

    for c in components:
        index = [b['ref'] for b in bom_entries].index(c.ref)
        b = bom_entries[index]
        c.val = b['value']
        c.mpn = b['mpn']
        c.extra_fields['Source'] = b['source']
        c.footprint = b['package']
        c.dnp = b['dnp']

    pcbdata["bom"] = ibom.generate_bom(components, config)
    pcbdata["ibom_version"] = config.version

    ibom.log = logger
    pcb_file_name = os.path.basename(parser.file_name)
    pcb_file_dir = os.path.dirname(parser.file_name)
    # build BOM
    bom_file = generate_file(pcb_file_dir, pcb_file_name, pcbdata, config)

    if config.open_browser:
        logger.info("Opening file in browser")
        ibom.open_file(bom_file)

    print("Finished generating Interactive HTML BOM")
