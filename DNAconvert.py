#!/usr/bin/env python3
import argparse
import sys
import lib.formats
import os
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
from tkinter import ttk

# splits two component extension
def splitext(name):
   name, ext2 = os.path.splitext(name)
   _, ext1 = os.path.splitext(name)
   return (ext1 + ext2, ext2)

def parse_format(name, ext_pair):
    d_ext = ext_pair[0]
    ext = ext_pair[1]
    try:
        return lib.formats.formats[name] if name else lib.formats.extensions[d_ext]
    except KeyError:
        try:
            return lib.formats.extensions[ext]
        except KeyError:
            return None

def convertDNA(infile, outfile, informat, outformat):
    fields, records = informat.read(infile)
    
    writer = outformat.write(outfile, fields)
    next(writer)

    for record in records():
        writer.send(record)

    writer.close()

def convert_wrapper(infile, outfile, informat_name, outformat_name):
    # detect extensions
    in_ext = splitext(infile)
    out_ext = splitext(outfile)

    # parse the formats
    informat = parse_format(informat_name, in_ext)
    outformat = parse_format(outformat_name, out_ext)

    # check that everything is okay
    if not infile:
        raise ValueError(f"No input file name")
    if not outfile:
        raise ValueError(f"No output file name")
    if not informat:
        raise ValueError(f"Unknown format {informat_name or in_ext[0]}")
    if not outformat:
        raise ValueError(f"Unknown format {outformat_name or out_ext[0]}")

    # do the conversion
    with open(infile) as infile, open(outfile, mode="w") as outfile:
        convertDNA(infile, outfile, informat = informat, outformat = outformat)



def launch_gui():
    # create window
    root = tk.Tk()
    root.title("DNAconvert")
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    mainframe = ttk.Frame(root, padding=(3,3,3,3))
    mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
    mainframe.rowconfigure(5, weight=1)
    mainframe.columnconfigure(2, weight=1)
    
    # create labels
    infile_lbl = ttk.Label(mainframe, text="Input File")
    informat_lbl = ttk.Label(mainframe, text="Format")
    outfile_lbl = ttk.Label(mainframe, text="Output File")
    outformat_lbl = ttk.Label(mainframe, text="Format")

    # create file entries
    infile_name = tk.StringVar()
    infile_entry = ttk.Entry(mainframe, textvariable=infile_name)
    outfile_name = tk.StringVar()
    outfile_entry = ttk.Entry(mainframe, textvariable=outfile_name)

    # create format comboboxes
    format_list = list(lib.formats.formats.keys())
    informat = tk.StringVar()
    outformat = tk.StringVar()
    informatBox = ttk.Combobox(mainframe, textvariable=informat, values=format_list)
    outformatBox = ttk.Combobox(mainframe, textvariable=outformat, values=format_list)

    # command for the input "Browse" button
    def browse_infile():
        name = os.path.relpath(tkinter.filedialog.askopenfilename())
        infile_name.set(name)

    # command for the output "Browse" button
    def browse_outfile():
        name = os.path.relpath(tkinter.filedialog.asksaveasfilename())
        outfile_name.set(name)

    # command for the convert button
    def gui_convert():
        try:
            convert_wrapper(infile_name.get(), outfile_name.get(), informat.get(), outformat.get())
        except ValueError as ex:
            tkinter.messagebox.showerror("Error", str(ex))
        except FileNotFoundError as ex:
            tkinter.messagebox.showerror("Error", str(ex))
            

    # buttons
    infile_browse = ttk.Button(mainframe, text="Browse", command=browse_infile)
    outfile_browse = ttk.Button(mainframe, text="Browse", command=browse_outfile)
    convert_btn = ttk.Button(mainframe, text="Convert", command=gui_convert)

    # place input widget group
    infile_lbl.grid(column=0, row=0, sticky=tk.W)
    infile_entry.grid(column=0, row=1, sticky=tk.W)
    informat_lbl.grid(column=0, row=2, sticky=tk.W)
    informatBox.grid(column=0, row=3, sticky=tk.W)
    infile_browse.grid(column=1, row=1, sticky=tk.W)

    # place output widget group
    outfile_lbl.grid(column=3, row=0, sticky=tk.W)
    outfile_entry.grid(column=3, row=1, sticky=tk.W)
    outformat_lbl.grid(column=3, row=2, sticky=tk.W)
    outformatBox.grid(column=3, row=3, sticky=tk.W)
    outfile_browse.grid(column=4, row=1, sticky=tk.W)

    # place the convert button
    convert_btn.grid(column=2, row=4)

    # run the gui
    root.mainloop()

# configure the argument parser
parser = argparse.ArgumentParser(description="Converts between file formats with genetic information. Uses graphical interface by default.")
parser.add_argument('--cmd', help="activates the command-line interface", action='store_true')
parser.add_argument('--informat', help="format of the input file")
parser.add_argument('--outformat', help="format of the output file")
parser.add_argument('infile', nargs='?', help="the input file")
parser.add_argument('outfile', nargs='?', help="the output file")

# parse the arguments
args=parser.parse_args()

# launch gui or convert the file
if not args.cmd:
    launch_gui()
else:
    try:
        convert_wrapper(args.infile, args.outfile, args.informat, args.outformat)
    except ValueError as ex:
        sys.exit(ex)
    except FileNotFoundError as ex:
        sys.exit(ex)
