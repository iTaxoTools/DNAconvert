#!/usr/bin/env python3
import argparse
import io
import sys
from .library import formats
import os
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
import tkinter.font as tkfont
from tkinter import ttk
import warnings
import gzip
from .library import fasta
from typing import Tuple, Type, Optional, TextIO, Any
from .library import guiutils
from .library import utils
from .library.resources import get_resource


def splitext(name: str) -> Tuple[str, str]:
    """
    Returns the two-part extension and the one-part extension of a file name

    Example:
        splitext("abc.fas.gb.gz") == (".gb.gz", ".gz")
    """
    name, ext2 = os.path.splitext(name)
    _, ext1 = os.path.splitext(name)
    return (ext1 + ext2, ext2)


def parse_format(name: Optional[str], ext_pair: Tuple[str, str]) -> Optional[Type[Any]]:
    """
    Lookups the format class based on the format name or the extensions.

    Only checks the extensions, if the name is None.
    Two-part extension has the priority

    Examples:
        parse_format("fasta", ext_pair) == library.fasta.Fastafile

        parse_format(None, (".hapv.fas", ".fas") == library.fasta.HapviewFastafile

        parse_format(None, (".txt.fas", ".fas") == library.fasta.Fastafile
    """
    # destruct the ext_pair
    d_ext, ext = ext_pair

    try:
        # lookup the format name, or the two-part extension, if it doesn't exist
        return formats.formats[name] if name else formats.extensions[d_ext.lower()]
    except KeyError:
        # both the format name and the two-part extension are unknown
        try:
            # lookup the one-part extension
            return formats.extensions[ext]
        except KeyError:
            # all the lookups failed
            return None


def convertDNA(
    infile: TextIO,
    outfile: TextIO,
    informat: Type[Any],
    outformat: Type[Any],
    **options: bool,
) -> None:
    """
    Converts infile of format informat to outfile of format outformat with given options

    Possible options:
        allow_empty_sequences: if set, the records with empty sequences are also recorded in the outfile.
           By default, records with empty sequences are discarded
        automatic_renaming: if set, enables automatic renaming of sequence names
        preserve_spaces: if set, the spaces in sequences are not removed
    """
    utils.GLOBAL_OPTION_DISABLE_AUTOMATIC_RENAMING = not options["automatic_renaming"]
    # take a shortcut for convertion FastQ into FASTA
    if informat is fasta.FastQFile and outformat is fasta.Fastafile:
        fasta.FastQFile.to_fasta(infile, outfile)
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
        if not options["preserve_spaces"]:
            record["sequence"] = record["sequence"].replace(" ", "")
        # when 'allow_empty_sequences' is set, the condition is always true and the record is passed to the writer
        # otherwise only the records with non-empty sequences are passed
        if record["sequence"] or options["allow_empty_sequences"]:
            writer.send(record)
        else:
            skipped += 1

    # finish the writing
    writer.close()

    # inform the user about the number of skipped records
    if skipped > 0:
        warnings.warn(
            f"{skipped} records did not contain a sequence and are therefore not included in the converted file.\n If you would like to keep the empty sequences, check 'Allow empty sequences' or pass the option '- -allow_empty_sequences"
        )


def convert_wrapper(
    infile_path: str,
    outfile_path: str,
    informat_name: str,
    outformat_name: str,
    **options: bool,
) -> None:
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
                outfile_path_curr = (
                    outfile_path.replace("#", basename, 1)
                    if "#" in outfile_path
                    else os.path.join(outfile_path, infile_curr.name)
                )
                convert_wrapper(
                    infile_curr.path,
                    outfile_path_curr,
                    informat_name,
                    outformat_name,
                    **options,
                )
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
        infile: TextIO = gzip.open(infile_path, mode="rt", errors="replace")
    else:
        infile = open(infile_path, errors="replace")

    # do the conversion
    with infile, open(outfile_path, mode="w") as outfile:
        convertDNA(infile, outfile, informat=informat, outformat=outformat, **options)


def launch_gui() -> None:
    """
    This function runs the graphical interface

    It is used when DNAconvert is launched without arguments
    """
    # create window
    root = tk.Tk()
    root.title("DNAconvert")
    if os.name == "nt":
        root.wm_iconbitmap(get_resource("dnaconvert.ico"))
    root.rowconfigure(2, weight=1)
    root.columnconfigure(0, weight=1)

    style = ttk.Style()
    style.configure("ConvertButton.TButton", background="blue")
    mainframe = ttk.Frame(root, padding=(3, 3, 3, 3))
    mainframe.grid(column=0, row=2, sticky="nsew")
    mainframe.columnconfigure(2, weight=1)

    # banner frame
    banner_frame = ttk.Frame(root)
    banner_img = tk.PhotoImage(
        file=get_resource("iTaxoTools Digital linneaeus MICROLOGO.png")
    )
    banner_image = ttk.Label(banner_frame, image=banner_img)
    banner_image.grid(row=0, column=0, rowspan=3, sticky="nsw")
    program_name = ttk.Label(banner_frame, text="DNAconvert", font=tkfont.Font(size=20))
    program_name.grid(row=1, column=1, sticky="sw")
    program_description = ttk.Label(
        banner_frame, text="A versatile  DNA sequence format converter"
    )
    author = ttk.Label(
        banner_frame,
        text="DNAconvert code by Vladimir Kharchev: https://github.com/iTaxoTools/DNAconvert",
        font=tkfont.Font(size=8),
    )
    author.grid(row=2, column=1, columnspan=2, sticky="nsw")
    program_description.grid(row=1, column=2, sticky="sw", ipady=4, ipadx=15)
    banner_frame.grid(column=0, row=0, sticky="nsw")

    # frame for convert button and checkboxes
    middle_frame = ttk.Frame(mainframe)

    banner_sep = ttk.Separator(root)
    banner_sep.grid(row=1, column=0, sticky="nsew")

    # create labels
    infile_lbl = ttk.Label(mainframe, text="Input File")
    informat_lbl = ttk.Label(mainframe, text="Input Format")
    outfile_lbl = ttk.Label(mainframe, text="Output File")
    outformat_lbl = ttk.Label(mainframe, text="Output Format")

    # create file entries
    infile_name = tk.StringVar()
    infile_entry = ttk.Entry(mainframe, textvariable=infile_name)
    outfile_name = tk.StringVar()
    outfile_entry = ttk.Entry(mainframe, textvariable=outfile_name)

    # create format comboboxes
    informat = tk.StringVar()
    outformat = tk.StringVar()
    informatBox = ttk.Combobox(
        mainframe, textvariable=informat, values=formats.informats_gui
    )
    outformatBox = ttk.Combobox(
        mainframe, textvariable=outformat, values=formats.outformats_gui
    )

    # create input boxes for small conversions
    box_frame = ttk.Frame(root)
    box_frame.rowconfigure(0, weight=1)
    box_frame.columnconfigure(0, weight=1)
    box_frame.columnconfigure(1, weight=1)
    input_box = guiutils.ScrolledText(
        box_frame,
        label="Instead of specifying an file name, your data can also be pasted here\n(recommended only for small data sets)",
        width=30,
        height=12,
    )
    input_box.label.configure(wraplength=500)
    output_box = guiutils.ScrolledText(
        box_frame,
        label="If data have been pasted into the window on the left, the converted output will be shown here",
        width=30,
        height=12,
    )
    output_box.label.configure(wraplength=500)
    input_box.grid(row=0, column=0, sticky="nsew")
    output_box.grid(row=0, column=1, sticky="nsew")

    def enable_boxes(*_: Any) -> None:
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
        newpath: Optional[str] = tkinter.filedialog.askopenfilename()
        if newpath:
            try:
                newpath = os.path.relpath(newpath)
            except:
                newpath = os.path.abspath(newpath)
            infile_name.set(newpath)

    # command for the output "Browse" button
    def browse_outfile() -> None:
        newpath: Optional[str] = tkinter.filedialog.asksaveasfilename()
        if newpath:
            try:
                newpath = os.path.relpath(newpath)
            except:
                newpath = os.path.abspath(newpath)
            outfile_name.set(newpath)

    def small_convert() -> None:
        if not (informat.get() and outformat.get()):
            raise ValueError("For small conversions both format need to be specified")
        input_data = io.StringIO(input_box.text.get("1.0", "end"))
        output_data = io.StringIO()
        input_format = parse_format(informat.get(), ("", ""))
        output_format = parse_format(outformat.get(), ("", ""))
        assert input_format is not None
        assert output_format is not None
        convertDNA(
            input_data,
            output_data,
            input_format,
            output_format,
            allow_empty_sequences=allow_empty_sequences.get(),
            automatic_renaming=automatic_renaming.get(),
            preserve_spaces=preserve_spaces.get(),
        )
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
                    convert_wrapper(
                        infile_name.get(),
                        outfile_name.get(),
                        informat.get(),
                        outformat.get(),
                        allow_empty_sequences=allow_empty_sequences.get(),
                        automatic_renaming=automatic_renaming.get(),
                        preserve_spaces=preserve_spaces.get(),
                    )
                # display the warnings generated during the conversion
                for w in warns:
                    tkinter.messagebox.showwarning("Warning", str(w.message))
            # notify the user that the converions is finished
            tkinter.messagebox.showinfo("Done.", "The conversion has been completed")
        # show the ValueErrors and FileNotFoundErrors
        except Exception as ex:
            tkinter.messagebox.showerror("Error", str(ex))

    def browse_indir() -> None:
        newpath: Optional[str] = tkinter.filedialog.askdirectory()
        if newpath:
            try:
                newpath = os.path.relpath(newpath)
            except:
                newpath = os.path.abspath(newpath)
            infile_name.set(newpath)

    # buttons
    infile_browse = ttk.Button(mainframe, text="Browse", command=browse_infile)
    indir_browse = ttk.Button(
        mainframe,
        text="Browse input directory\n(for batch conversions)",
        command=browse_indir,
    )
    outfile_browse = ttk.Button(mainframe, text="Browse", command=browse_outfile)
    convert_btn = ttk.Button(
        middle_frame, text="Convert", command=gui_convert, style="ConvertButton.TButton"
    )

    # checkbox to allow empty sequences
    allow_empty_sequences = tk.BooleanVar()
    allow_es_chk = ttk.Checkbutton(
        middle_frame, text="Allow empty sequences", variable=allow_empty_sequences
    )

    # checkbox to enable automatic renaming
    dar_frame = ttk.Frame(middle_frame)
    automatic_renaming = tk.BooleanVar()
    automatic_renaming_chk = ttk.Checkbutton(dar_frame, variable=automatic_renaming)
    dar_lbl = ttk.Label(
        dar_frame,
        text="Check to enable automatic renaming of sequences\n(to avoid duplicate sequence names in Phylip and Nexus files)",
    )

    # checkbox to preserve spaces in sequences
    preserve_spaces = tk.BooleanVar()
    preserve_spaces_chk = ttk.Checkbutton(
        middle_frame, text="Preserve spaces in sequences", variable=preserve_spaces
    )

    # place input widget group
    infile_lbl.grid(column=0, row=0, sticky=tk.W)
    infile_entry.grid(column=0, row=1, sticky=tk.W)
    informat_lbl.grid(column=0, row=3, sticky=tk.W)
    informatBox.grid(column=0, row=4, sticky=tk.W)
    infile_browse.grid(column=1, row=1, sticky=tk.W)
    indir_browse.grid(column=1, row=2, sticky="w")

    # place output widget group
    outfile_lbl.grid(column=3, row=0, sticky=tk.W)
    outfile_entry.grid(column=3, row=1, sticky=tk.W)
    outformat_lbl.grid(column=3, row=3, sticky=tk.W)
    outformatBox.grid(column=3, row=4, sticky=tk.W)
    outfile_browse.grid(column=4, row=1, sticky=tk.W)

    # place the convert button and the checkboxes
    middle_frame.grid(column=2, row=0, rowspan=5)
    convert_btn.grid(column=0, row=1)
    allow_es_chk.grid(column=0, row=2, sticky="w")
    dar_frame.grid(column=0, row=3, sticky="w")
    automatic_renaming_chk.grid(column=0, row=0, sticky="n")
    dar_lbl.grid(column=1, row=0)
    preserve_spaces_chk.grid(column=0, row=4, sticky="w")

    # place a separator above boxes
    ttk.Separator(root).grid(column=0, row=3, sticky="nsew", ipady=10)

    # place the boxes
    box_frame.grid(column=0, row=4, sticky="nsew", padx=5)

    # run the gui
    root.mainloop()


def main() -> None:
    # configure the argument parser
    parser = argparse.ArgumentParser(
        description="Converts between file formats with genetic information. Uses graphical interface by default."
    )
    parser.add_argument(
        "--cmd", help="activates the command-line interface", action="store_true"
    )
    parser.add_argument(
        "--allow_empty_sequences",
        action="store_true",
        help="set this to keep the empty sequences in the output file",
    )
    parser.add_argument(
        "--automatic_renaming",
        action="store_true",
        help="enables automatic renaming of sequences (to avoid duplicate sequence names in Phylip and Nexus files)",
    )
    parser.add_argument(
        "--preserve_spaces", action="store_true", help="preserve spaces in sequences"
    )
    parser.add_argument("--informat", default="", help="format of the input file")
    parser.add_argument("--outformat", default="", help="format of the output file")
    parser.add_argument("infile", default="", nargs="?", help="the input file")
    parser.add_argument("outfile", default="", nargs="?", help="the output file")

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
                convert_wrapper(
                    args.infile,
                    args.outfile,
                    args.informat,
                    args.outformat,
                    allow_empty_sequences=args.allow_empty_sequences,
                    automatic_renaming=args.automatic_renaming,
                    preserve_spaces=args.preserve_spaces,
                )

                # display the warnings generated during the conversion
                for w in warns:
                    print(w.message)
        # show the ValueErrors and FileNotFoundErrors
        except ValueError as ex:
            sys.exit(ex)
        except FileNotFoundError as ex:
            sys.exit(ex)
