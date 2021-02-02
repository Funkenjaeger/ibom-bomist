import sys
import time
import argparse
from bomist.bomist import BomistApi

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--bomist', help="BOMIST project - syntax: MPN,REVCODE,BUILDCODE")
    args = parser.parse_args()

    bomist = BomistApi()
    build_tree = bomist.project_build_tree()

    print(build_tree)
