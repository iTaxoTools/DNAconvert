#!/usr/bin/env python3
import argparse
import sys

# configure the argument parser
parser = argparse.ArgumentParser(description="Converts between file formats with genetic information")
parser.add_argument('--informat', help="format of the input file")
parser.add_argument('--outformat', help="format of the output file")
parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), help="the input file")
parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout, help="the output file")

# parse the arguments
args=parser.parse_args()
print(vars(args))
