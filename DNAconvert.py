#!/usr/bin/env python3
import argparse
import io
import sys
import lib.formats
import os
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
from tkinter import ttk
import warnings
import gzip
import lib.fasta
from typing import Tuple, Type, Optional, TextIO, cast, Any
import lib.guiutils as guiutils


def splitext(name: str) -> Tuple[str, str]:
    """
    Returns the two-part extension and the one-part extension of a file name

    Example:
        splitext("abc.fas.gb.gz") == (".gb.gz", ".gz")
    """
    name, ext2 = os.path.splitext(name)
    _, ext1 = os.path.splitext(name)
    return (ext1 + ext2, ext2)


def parse_format(name: Optional[str], ext_pair: Tuple[str, str]) -> Optional[Type]:
    """
    Lookups the format class based on the format name or the extensions.

    Only checks the extensions, if the name is None.
    Two-part extension has the priority

    Examples:
        parse_format("fasta", ext_pair) == lib.fasta.Fastafile

        parse_format(None, (".hapv.fas", ".fas") == lib.fasta.HapviewFastafile

        parse_format(None, (".txt.fas", ".fas") == lib.fasta.Fastafile
    """
    # destruct the ext_pair
    d_ext = ext_pair[0]
    ext = ext_pair[1]

    try:
        # lookup the format name, or the two-part extension, if it doesn't exist
        return lib.formats.formats[name] if name else lib.formats.extensions[d_ext]
    except KeyError:
        # both the format name and the two-part extension are unknown
        try:
            # lookup the one-part extension
            return lib.formats.extensions[ext]
        except KeyError:
            # all the lookups failed
            return None


def convertDNA(infile: TextIO, outfile: TextIO, informat: Type, outformat: Type, **options: bool) -> None:
    """
    Converts infile of format informat to outfile of format outformat with given options

    Possible options:
        allow_empty_sequnces: if set, the records with empty sequences are also recorded in the outfile.
           By default, records with empty sequences are discarded
    """
    # take a shortcut for convertion FastQ into FASTA
    if informat is lib.fasta.FastQFile and outformat is lib.fasta.Fastafile:
        lib.fasta.FastQFile.to_fasta(infile, outfile)
        return

    # initialize reading the file
    fields, records = informat.read(infile)

    # start the writer
    writer = outformat.write(outfile, fields)
    next(writer)

    # keep track of the number of skipped records
    skipped = 0
    # iterate over the records in infile
    for record in records():
        # when 'allow_empty_sequences' is set, the condition is always true and the record is passed to the writer
        # otherwise only the records with non-empty sequences are passed
        if record['sequence'] or options['allow_empty_sequences']:
            writer.send(record)
        else:
            skipped += 1

    # finish the writing
    writer.close()

    # inform the user about the number of skipped records
    if skipped > 0:
        warnings.warn(
            f"{skipped} records did not contain a sequence and are therefore not included in the converted file.\n If you would like to keep the empty sequences, check 'Allow empty sequences' or pass the option '- -allow_empty_sequences")


def convert_wrapper(infile_path: str, outfile_path: str, informat_name: str, outformat_name: str, **options: bool) -> None:
    """
    This the wrapper for convertDNA. It parses the arguments and deals with the errors.

    Detects formats based on informat_name, outformat_name and extensions
    Passes options to the convertDNA
    """
    # if infile_path is a directory, convert all files in it
    if os.path.isdir(infile_path):
        with os.scandir(infile_path) as files:
            for infile_curr in files:
                basename, _ = os.path.splitext(infile_curr.name)
                outfile_path_curr = outfile_path.replace(
                    '#', basename, 1) if '#' in outfile_path else os.path.join(outfile_path, infile.name)
                convert_wrapper(infile_curr.path, outfile_path_curr,
                                informat_name, outformat_name, **options)
        return

    # detect extensions
    in_ext = splitext(infile_path)
    out_ext = splitext(outfile_path)

    # parse the formats
    informat = parse_format(informat_name, in_ext)
    outformat = parse_format(outformat_name, out_ext)

    # check that everything is okay
    if not infile_path:
        raise ValueError("No input file name")
    if not outfile_path:
        raise ValueError("No output file name")
    if not informat:
        raise ValueError(f"Unknown format {informat_name or in_ext[0]}")
    if not outformat:
        raise ValueError(f"Unknown format {outformat_name or out_ext[0]}")

    # open the input file
    if in_ext[1] == ".gz":
        # if the input file is a gz archive, unpack it
        infile: TextIO = cast(TextIO, gzip.open(infile_path, mode='rt'))
    else:
        infile = open(infile_path)

    # do the conversion
    with infile, open(outfile_path, mode="w") as outfile:
        convertDNA(infile, outfile, informat=informat,
                   outformat=outformat, **options)


def launch_gui() -> None:
    """
    This function runs the graphical interface

    It is used when DNAconvert is launched without arguments
    """
    # create window
    root = tk.Tk()
    root.title("DNAconvert")
    if os.name == "nt":
        root.wm_iconbitmap(os.path.join('data', 'DNAconvert_transparent.ico'))
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    mainframe = ttk.Frame(root, padding=(3, 3, 3, 3))
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
    informatBox = ttk.Combobox(
        mainframe, textvariable=informat, values=format_list)
    outformatBox = ttk.Combobox(
        mainframe, textvariable=outformat, values=format_list)

    # create input boxes for small conversions
    box_frame = ttk.Frame(mainframe)
    box_frame.rowconfigure(0, weight=1)
    box_frame.columnconfigure(0, weight=1)
    box_frame.columnconfigure(1, weight=1)
    input_box = guiutils.ScrolledText(
        box_frame, label="Instead of specifying an file name, your data can also be pasted here\n(recommended only for small data sets)")
    output_box = guiutils.ScrolledText(
        box_frame, label="If data have been pasted into the window on the left, the converted output will be shown here\n")
    input_box.grid(row=0, column=0, sticky='nsew')
    output_box.grid(row=0, column=1, sticky='nsew')

    def enable_boxes(*args: Any) -> None:
        """
        Enables input_box and output_box if infile_name is empty, disables otherwise
        """
        if infile_name.get():
            input_box.text.configure(state=tk.DISABLED)
            output_box.text.configure(state=tk.DISABLED)
            input_box.label.configure(state=tk.DISABLED)
            output_box.label.configure(state=tk.DISABLED)
        else:
            input_box.text.configure(state=tk.NORMAL)
            output_box.text.configure(state=tk.NORMAL)
            input_box.label.configure(state=tk.NORMAL)
            output_box.label.configure(state=tk.NORMAL)

    infile_name.trace_add("write", enable_boxes)

    # command for the input "Browse" button
    def browse_infile() -> None:
        if (newpath := tkinter.filedialog.askopenfilename()):
            try:
                newpath = os.path.relpath(newpath)
            except:
                newpath = os.path.abspath(newpath)
            infile_name.set(newpath)

    # command for the output "Browse" button
    def browse_outfile() -> None:
        if (newpath := os.path.relpath(tkinter.filedialog.asksaveasfilename())):
            try:
                newpath = os.path.relpath(newpath)
            except:
                newpath = os.path.abspath(newpath)
            outfile_name.set(newpath)

    def small_convert() -> None:
        if not (informat.get() and outformat.get()):
            raise ValueError(
                "For small conversions both format need to be specified")
        input_data = io.StringIO(input_box.text.get("1.0", "end"))
        output_data = io.StringIO()
        input_format = parse_format(informat.get(), ("", ""))
        output_format = parse_format(outformat.get(), ("", ""))
        assert(input_format is not None)
        assert(output_format is not None)
        convertDNA(input_data, output_data, input_format, output_format,
                   allow_empty_sequences=allow_empty_sequences.get())
        output_box.text.delete("1.0", "end")
        output_box.text.insert("1.0", output_data.getvalue())

    # command for the convert button

    def gui_convert() -> None:
        try:
            # catch all warnings
            with warnings.catch_warnings(record=True) as warns:
                if not infile_name.get():
                    small_convert()
                else:
                    convert_wrapper(infile_name.get(), outfile_name.get(),
                                    informat.get(), outformat.get(), allow_empty_sequences=allow_empty_sequences.get())
                # display the warnings generated during the conversion
                for w in warns:
                    tkinter.messagebox.showwarning("Warning", str(w.message))
            # notify the user that the converions is finished
            tkinter.messagebox.showinfo(
                "Done.", "The conversion has been completed")
        # show the ValueErrors and FileNotFoundErrors
        except ValueError as ex:
            tkinter.messagebox.showerror("Error", str(ex))
        except FileNotFoundError as ex:
            tkinter.messagebox.showerror("Error", str(ex))

    def browse_indir() -> None:
        if (newpath := os.path.relpath(tkinter.filedialog.askdirectory())):
            try:
                newpath = os.path.relpath(newpath)
            except:
                newpath = os.path.abspath(newpath)
            infile_name.set(newpath)

    # buttons
    infile_browse = ttk.Button(mainframe, text="Browse", command=browse_infile)
    indir_browse = ttk.Button(
        mainframe, text="Browse Dir", command=browse_indir)
    outfile_browse = ttk.Button(
        mainframe, text="Browse", command=browse_outfile)
    convert_btn = ttk.Button(mainframe, text="Convert", command=gui_convert)

    # checkbox to allow empty sequences
    allow_empty_sequences = tk.BooleanVar()
    allow_es_chk = ttk.Checkbutton(
        mainframe, text="Allow empty sequences", variable=allow_empty_sequences)

    # place input widget group
    infile_lbl.grid(column=0, row=0, sticky=tk.W)
    infile_entry.grid(column=0, row=1, sticky=tk.W)
    informat_lbl.grid(column=0, row=2, sticky=tk.W)
    informatBox.grid(column=0, row=3, sticky=tk.W)
    infile_browse.grid(column=1, row=1, sticky=tk.W)
    indir_browse.grid(column=1, row=2, sticky="w")

    # place output widget group
    outfile_lbl.grid(column=3, row=0, sticky=tk.W)
    outfile_entry.grid(column=3, row=1, sticky=tk.W)
    outformat_lbl.grid(column=3, row=2, sticky=tk.W)
    outformatBox.grid(column=3, row=3, sticky=tk.W)
    outfile_browse.grid(column=4, row=1, sticky=tk.W)

    # place the convert button and the checkbox
    convert_btn.grid(column=2, row=4)
    allow_es_chk.grid(column=2, row=5)

    # place the boxes
    mainframe.rowconfigure(6, weight=1)
    box_frame.grid(column=0, row=6, columnspan=5, sticky='nsew')

    # run the gui
    root.mainloop()


# configure the argument parser
parser = argparse.ArgumentParser(
    description="Converts between file formats with genetic information. Uses graphical interface by default.")
parser.add_argument(
    '--cmd', help="activates the command-line interface", action='store_true')
parser.add_argument('--allow_empty_sequences', action='store_true',
                    help="set this to keep the empty sequences in the output file")
parser.add_argument('--informat', default="", help="format of the input file")
parser.add_argument('--outformat', default="",
                    help="format of the output file")
parser.add_argument('infile', default="", nargs='?', help="the input file")
parser.add_argument('outfile', default="", nargs='?', help="the output file")

# parse the arguments
args = parser.parse_args()

# launch gui or convert the file
if not args.cmd:
    launch_gui()
else:
    # launch in the command-line mode
    try:
        # catch the warnging
        with warnings.catch_warnings(record=True) as warns:
            convert_wrapper(args.infile, args.outfile,
                            args.informat, args.outformat, allow_empty_sequences=args.allow_empty_sequences)

            # display the warnings generated during the conversion
            for w in warns:
                print(w.message)
    # show the ValueErrors and FileNotFoundErrors
    except ValueError as ex:
        sys.exit(ex)
    except FileNotFoundError as ex:
        sys.exit(ex)
