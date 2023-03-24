import sys
import os

import wx

class IbomParser(object):
    ibom_dir = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
    ibom_dir = os.path.split(ibom_dir)[0]
    ibom_dir = os.path.join(ibom_dir, 'InteractiveHtmlBom')
    ibom_dir = os.path.join(ibom_dir, 'InteractiveHtmlBom')
    sys.path.insert(0, os.path.dirname(ibom_dir))
    os.environ['INTERACTIVE_HTML_BOM_CLI_MODE'] = 'True'

    def __init__(self, argparser, local_dir):
        wx.DisableAsserts()
        from InteractiveHtmlBom.core import ibom
        from InteractiveHtmlBom.core.config import Config
        from InteractiveHtmlBom.version import version
        self._config = Config(version, local_dir)
        self._config.add_options(argparser, self._config.FILE_NAME_FORMAT_HINT)
        self._argparser = argparser
        self.pcbdata = None
        self.components = None
        self._logger = ibom.Logger(cli=True)

    def parse(self, file_path, extra_args=None):
        from InteractiveHtmlBom.core import ibom
        from InteractiveHtmlBom.errors import (ExitCodes,
                                               ParsingException,
                                               exit_error)
        from InteractiveHtmlBom.ecad import get_parser_by_extension
        if not os.path.isfile(file_path):
            exit_error(logger, ExitCodes.ERROR_FILE_NOT_FOUND,
                       "File %s does not exist." % file_path)
        print("Loading %s" % file_path)
        ibom_parser = get_parser_by_extension(os.path.abspath(file_path),
                                              self._config, self._logger)
        if extra_args is not None:
            sys.argv.extend(extra_args.split())
        args = self._argparser.parse_args()
        self._config.set_from_args(args)

        self.pcbdata, self.components = ibom_parser.parse()
        if not self.pcbdata and not self.components:
            raise ParsingException('Parsing failed.')

    def reconcile(self, build_parser):
        from InteractiveHtmlBom.core import ibom

        match_count = 0
        no_match_count = 0
        for c in self.components:
            '''index = [b['ref'] for b in bom_entries].index(c.ref)
            b = bom_entries[index]'''
            b = build_parser.get_entry(c.ref)
            if b is None:
                print('No match found for ' + c.ref)
                no_match_count += 1
            else:
                c.val = b.value
                c.mpn = b.mpn
                c.extra_fields['Source'] = b.source
                c.extra_fields['MPN'] = b.mpn
                c.footprint = b.package
                c.dnp = b.dnp
                match_count += 1

        print(f"Matched {match_count} of {len(self.components)} components "
              f"({no_match_count} not matched)")

        self.pcbdata["bom"] = ibom.generate_bom(self.components, self._config)
        self.pcbdata["ibom_version"] = self._config.version

    def generate(self, file_path):
        from InteractiveHtmlBom.core import ibom
        from InteractiveHtmlBom.core.ibom import generate_file
        ibom.log = self._logger
        pcb_file_name = os.path.basename(file_path)
        pcb_file_dir = os.path.dirname(file_path)
        # build BOM
        bom_file = generate_file(pcb_file_dir,
                                 pcb_file_name,
                                 self.pcbdata,
                                 self._config)

        if self._config.open_browser:
            self._logger.info("Opening file in browser")
            ibom.open_file(bom_file)
