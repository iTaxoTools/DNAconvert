# DNAconvert tool
This program can convert between different formats containing genetic information

## Installation
Installation is currently not intended. Downloading should be enough

## Generating an executable
Using [PyInstaller](http://www.pyinstaller.org) is recommended. After the following instruction a directory `dist` will be created (among other) and the executable will be inside it.

### Linux
Install PyInstaller from PyPI:

    pip install pyinstaller

Then run

    pyinstaller --onefile DNAconvert.py

### Windows
Install PyInstaller:

[Installing on Windows](https://pyinstaller.readthedocs.io/en/stable/installation.html#installing-in-windows)

Then run

    pyinstaller --onefile --windowed DNAconvert.py

## Usage
    usage: DNAconvert.py [-h] [--cmd] [--informat INFORMAT]
                         [--outformat OUTFORMAT]
                         [infile] [outfile]
           DNAconvert.py
    
    positional arguments:
      infile                the input file
      outfile               the output file
    
    optional arguments:
      -h, --help            show this help message and exit
      --cmd                 activates the command-line interface
      --informat INFORMAT   format of the input file
      --outformat OUTFORMAT
                            format of the output file

## Supported formats
* `tab`: [Internal tab format][1]
* `fasta`: FASTA format
* `relaxed_phylip`: relaxed Phylip format
* `fasta_hapview`: FASTA format for Haplotype Viewer

## Recognised extension
If format is not provided, the program can infer it from the file extension

Currently recognised:
* `.tab`, `.txt`, `.tsv`: [Internal tab format][1]
* `.fas`: FASTA format
* `.rel.phy`: relaxed Phylip format
* `.hapv.fas`: FASTA format for Haplotype Viewer

## Adding new formats
[Link to documentation](doc/ADDING_FORMATS.md)

[1]: doc/TAB_FORMAT.md
