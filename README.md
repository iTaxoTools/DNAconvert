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
    usage: DNAconvert.py [-h] [--cmd] [--allow_empty_sequences]
                     [--informat INFORMAT] [--outformat OUTFORMAT]
                     [infile] [outfile]
           DNAconvert.py
    
    positional arguments:
      infile                the input file
      outfile               the output file
    
    optional arguments:
      -h, --help            show this help message and exit
      --cmd                 activates the command-line interface
      --allow_empty_sequences
                            set this to keep the empty sequences in the output
                            file
      --informat INFORMAT   format of the input file
      --outformat OUTFORMAT
                            format of the output file

## Supported formats
* `tab`: [Internal tab format][1]
* `fasta`: FASTA format
* `relaxed_phylip`: relaxed Phylip format
* `fasta_hapview`: FASTA format for Haplotype Viewer
* `phylip`: Phylip format
* `fastq`: FASTQ format
* `fasta_gbexport`: FASTA format for export into Genbank repository
* `nexus`: NEXUS format
* `genbank`: Genbank flat file format

## Recognised extension
If format is not provided, the program can infer it from the file extension

Currently recognised:
* `.tab`, `.txt`, `.tsv`: [Internal tab format][1]
* `.fas`, `.fasta`, `.fna`: FASTA format
* `.rel.phy`: relaxed Phylip format
* `.hapv.fas`: FASTA format for Haplotype Viewer
* `.phy`: Phylip format
* `.fastq`, `.fq`: FASTQ format
* `.fastq.gz`, `.fq.gz`: FASTQ format compressed with Gzip
* `.gb.fas`: FASTA format for export into Genbank repository
* `.nex`: NEXUS format
* `.gb`: Genbank flat file format

Files with extension `.gz` are uncompressed automatically

## Adding new formats
[Link to documentation](doc/ADDING_FORMATS.md)

[1]: doc/TAB_FORMAT.md
