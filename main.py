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
    argparser.add_argument('-b', '--board', nargs='?', const=None, default=None,
                           help='JSON board file')
    argparser.add_argument('-i', '--ibom', nargs='?', const=None, default=None,
                           help="BOMIST build - exported JSON file")
    argparser.add_argument('-r', '--run', action='store_true')

    args = argparser.parse_args()

    class MainPrompt(Cmd):
        board_file = args.board
        ibom_json_file = args.ibom
        ibom_extra_args = '--dnp-field dnp --extra-fields MPN,Source'

        prompt = '\nPlease enter a command (valid commands: board, ibom, run, quit)\n>'

        def set_intro(self):
            self.intro = "**************************************"
            self.intro += '\nCurrent board: ' + self.board_file.__str__()
            self.intro += '\nCurrent ibom project: ' + self.ibom_json_file.__str__()
            self.intro += '\nExtra ibom args: ' + self.ibom_extra_args
            self.intro += "\n\nAuto-discovered boards: "
            for idx, file in enumerate(self.pcb_json_files):
                self.intro += "\n" + (idx + 1).__str__() + ') ' \
                              + file.as_posix()
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
            """BOARD - select a Board file (Eagle .BRD, Fusion 360 Electronics .FBRD, or IBOM Generic JSON .JSON)
        Pass an integer argument to select one from the auto-discovered list (e.g. 'board 1')
        Or, omit an argument to browse for one (e.g. 'board')"""
            if arg == '':
                root = tk.Tk()
                root.withdraw()
                self.board_file = \
                    filedialog.askopenfilename(title='Select board file',
                                               filetypes=[('All board files', '.brd .fbrd .json'),
                                                          ('Eagle/Fusion', '.brd .fbrd'),
                                                          ('Generic JSON', '.json')])
            else:
                idx = int(arg)-1
                self.board_file = self.pcb_json_files[idx].as_posix()
            self.set_intro()
            print(self.intro)

        def do_ibom(self, arg):
            """IBOM - browse for an IBOM project JSON file exported from BOMIST"""
            root = tk.Tk()
            root.withdraw()
            self.ibom_json_file = \
                filedialog.askopenfilename(title='Select BOMIST build file',
                                           filetypes=[('JSON', '.json')])
            self.set_intro()
            print(self.intro)

        def do_menu(self, arg):
            """MENU - print the menu again"""
            print(self.intro)
        @staticmethod
        def do_quit(arg):
            return True

        @staticmethod
        def do_exit(arg):
            return True

        def do_run(self, arg):
            """RUN - process the files"""
            if self.ibom_json_file is None:
                print("Can't run - no Build file selected")
                return False
            if self.board_file is None:
                print("Can't run - no Board file selected")
                return False

            bp = BuildParser()
            bp.parse(self.ibom_json_file)

            local_dir = os.path.dirname(self.ibom_json_file)
            ip = IbomParser(argparser, local_dir)
            ip.parse(self.board_file, self.ibom_extra_args)
            ip.reconcile(bp)
            (dir, _) = os.path.split(self.ibom_json_file)
            (_, pcb_filename) = os.path.split(self.board_file)
            (base, _) = os.path.splitext(pcb_filename)
            output_filename = os.path.join(dir, base + '.html')
            ip.generate(output_filename)
            print("Finished generating Interactive HTML BOM")
            return True

    p = MainPrompt()
    if args.run:
        p.do_run(None)
    else:
        p.cmdloop()
