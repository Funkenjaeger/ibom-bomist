import sys
import os
import argparse
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from cmd import Cmd
from bomist.bomist import BuildParser
from ibom.ibom import IbomParser

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
        description='InteractiveHtmlBom-BOMIST interface tool CLI',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    argparser.add_argument('-p', '--pcb', nargs='?', const=None, default=None, help='JSON board file')
    argparser.add_argument('build', nargs='?', help="BOMIST build - exported JSON file")

    args = argparser.parse_args()

    class MainPrompt(Cmd):
        pcb_json_file = args.pcb
        build_json_file = args.build
        ibom_extra_args = '--dnp-field dnp --extra-fields MPN,Source'

        prompt = '\nPlease enter a command'

        def set_intro(self):
            self.intro = "**************************************"
            self.intro += '\nCurrent board: ' + self.pcb_json_file.__str__()
            self.intro += '\nCurrent build: ' + self.build_json_file.__str__()
            self.intro += '\nExtra IBOM args: ' + self.ibom_extra_args
            self.intro += "\n\nAuto-discovered boards: "
            for idx, file in enumerate(self.pcb_json_files):
                self.intro += "\n" + (idx + 1).__str__() + ') ' + file.as_posix()
            if len(self.pcb_json_files) == 0:
                self.intro += "\n(No boards discovered)"

        def __init__(self):
            super().__init__()
            home = os.path.expanduser("~")

            self.pcb_json_files = list(
                Path(os.path.join(home, "AppData\\Local\\Temp\\Neutron"
                                        "\\ElectronFileOutput\\")).rglob(
                    "*.[jJ][sS][oO][nN]"))
            self.set_intro()

        def do_board(self, arg):
            """BOARD - select an auto-discovered board, or browse for one"""
            if arg == '':
                root = tk.Tk()
                root.withdraw()
                self.pcb_json_file = filedialog.askopenfilename(title='Select board file',
                                                                filetypes=[('JSON', '.json')])
            else:
                idx = int(arg)-1
                self.pcb_json_file = self.pcb_json_files[idx].as_posix()
            self.set_intro()
            print(self.intro)

        def do_build(self, arg):
            root = tk.Tk()
            root.withdraw()
            self.build_json_file = filedialog.askopenfilename(title='Select BOMIST build file',
                                                              filetypes=[('JSON', '.json')])
            self.set_intro()
            print(self.intro)

        def do_menu(self, arg):
            """MENU - print the menu again"""
            print(self.intro)

        def do_run(self, arg):
            """RUN - process the files"""
            bp = BuildParser()
            bp.parse(self.build_json_file)

            ip = IbomParser(argparser)
            ip.parse(self.pcb_json_file, self.ibom_extra_args)
            ip.reconcile(bp)
            (dir, _) = os.path.split(self.build_json_file)
            (_, pcb_filename) = os.path.split(self.pcb_json_file)
            (base, _) = os.path.splitext(pcb_filename)
            output_filename = os.path.join(dir, base + '.html')
            ip.generate(output_filename)
            return True

    p = MainPrompt()
    p.cmdloop()

    print("Finished generating Interactive HTML BOM")
