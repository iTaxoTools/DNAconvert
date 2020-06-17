# DNAconvert tool
This program can convert between different formats containing genetic information

## Installation
Installation is currently not intended. Downloading should be enough

## Usage
    DNAconvert.py [-h] [--informat INFORMAT] [--outformat OUTFORMAT]
                         [infile] [outfile]
    
    positional arguments:
      infile                the input file
      outfile               the output file
    
    optional arguments:
      -h, --help            show this help message and exit
      --informat INFORMAT   format of the input file
      --outformat OUTFORMAT
                            format of the output file

## Supported formats
* `tab`: [Internal tab format][1]
* `fasta`: FASTA format

## Recognised extension
If format is not provided, the program can infer it from the file extension

Currently recognised:
* `.tab`, `.txt`, `.tsv`: [Internal tab format][1]
* `.fas`: FASTA format

## Adding new formats
[Link to documentation](doc/ADDING_FORMATS.md)

[1]: doc/TAB_FORMAT.md
