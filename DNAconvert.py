#!/usr/bin/env python3
import argparse
import sys
import lib.formats
import os
import tkinter as tk
from tkinter import ttk

def parse_format(name, ext):
    try:
        return lib.formats.formats[name] if name else lib.formats.extensions[ext]
    except KeyError:
        return None

def convertDNA(infile, outfile, informat, outformat):
    fields, records = informat.read(infile)
    
    writer = outformat.write(outfile, fields)
    next(writer)

    for record in records():
        writer.send(record)

    writer.close()

def launch_gui():
    root = tk.Tk()
    root.title("DNAconvert")
    mainframe = ttk.Frame(root)
    mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

    root.mainloop()
    sys.exit()

# configure the argument parser
parser = argparse.ArgumentParser(description="Converts between file formats with genetic information")
parser.add_argument('--gui', help="activates the graphical interface", action='store_true')
parser.add_argument('--informat', help="format of the input file")
parser.add_argument('--outformat', help="format of the output file")
parser.add_argument('infile', nargs='?', help="the input file")
parser.add_argument('outfile', nargs='?', help="the output file")

# parse the arguments
args=parser.parse_args()

# goto into the gui version
if args.gui:
    launch_gui()

# detect extensions
_, in_ext = os.path.splitext(args.infile)
_, out_ext = os.path.splitext(args.outfile)

# parse the formats
informat = parse_format(args.informat, in_ext)
outformat = parse_format(args.outformat, out_ext)

# check that everything is okay
if not informat:
    sys.exit(f"Unknown format {args.informat or in_ext}")
if not outformat:
    sys.exit(f"Unknown format {args.outformat or out_ext}")
if not os.path.exists(args.infile):
    sys.exit(f"Can't find file {args.infile}")

# do the conversion
with open(args.infile) as infile, open(args.outfile, mode="w") as outfile:
    convertDNA(infile, outfile, informat = informat, outformat = outformat)

