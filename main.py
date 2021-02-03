import sys
import time
import argparse
from bomist.bomist import BomistApi

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
<<<<<<< Updated upstream
    parser.add_argument('-b', '--bomist', help="BOMIST project - syntax: MPN,REVCODE,BUILDCODE")
    args = parser.parse_args()

    bomist = BomistApi()
    build_tree = bomist.project_build_tree()

    print(build_tree)

    bomist = BomistApi()
    build = bomist.get_build_by_names(*tuple(args.bomist.split(',')))

    print(build)
>>>>>>> Stashed changes
