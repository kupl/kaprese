import argparse
import sys


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser()

    args = parser.parse_args(argv)

    print("Not implemented yet.")
