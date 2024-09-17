# DNAconvert

[![GitHub - Tests](https://img.shields.io/github/actions/workflow/status/iTaxoTools/DNAconvert/test.yml?label=tests)](
    https://github.com/iTaxoTools/DNAconvert/actions/workflows/test.yml)
[![GitHub - Windows](https://img.shields.io/github/actions/workflow/status/iTaxoTools/DNAconvert/windows.yml?label=windows)](
    https://github.com/iTaxoTools/DNAconvert/actions/workflows/windows.yml)
[![GitHub - macOS](https://img.shields.io/github/actions/workflow/status/iTaxoTools/DNAconvert/macos.yml?label=macos)](
    https://github.com/iTaxoTools/DNAconvert/actions/workflows/macos.yml)

Convert between different file formats containing genetic information.

## Installation
Install the latest version directly using pip (requires Python 3.8.6 or later):
```
pip install git+https://github.com/iTaxoTools/DNAconvert.git#egg=DNAconvert
```

## Executables
Download and run the standalone executables without installing Python.

[![Release](https://img.shields.io/badge/release-1.1.0-red?style=for-the-badge)](
    https://github.com/iTaxoTools/DNAconvert/releases/v1.1.0)
[![Windows](https://img.shields.io/badge/Windows-blue.svg?style=for-the-badge&logo=windows)](
    https://github.com/iTaxoTools/DNAconvert/releases/download/v1.1.0/DNAconvert-1.1.0-windows-x64.exe)
[![MacOS](https://img.shields.io/badge/macOS-slategray.svg?style=for-the-badge&logo=apple)](
    https://github.com/iTaxoTools/DNAconvert/releases/download/v1.1.0/DNAconvert-1.1.0-macos-universal2.dmg)

## Usage
    usage: DNAconvert [-h] [--cmd] [--allow_empty_sequences]
                      [--automatic_renaming] [--preserve_spaces]
                      [--informat INFORMAT] [--outformat OUTFORMAT]
                      [infile] [outfile]

    Converts between file formats with genetic information. Uses graphical
    interface by default.

    positional arguments:
      infile                the input file
      outfile               the output file

    optional arguments:
      -h, --help            show this help message and exit
      --cmd                 activates the command-line interface
      --allow_empty_sequences
                            set this to keep the empty sequences in the output
                            file
      --automatic_renaming  enables automatic renaming of sequences (to avoid
                            duplicate sequence names in Phylip and Nexus files)
      --preserve_spaces     preserve spaces in sequences
      --informat INFORMAT   format of the input file
      --outformat OUTFORMAT
                            format of the output file

### Batch processing

If `infile` is a directory, all files in it will be converted. In this case `informat` and `outformat` arguments are required.

Specifying names of the output files:
* `outfile` contains a '#' character: '#' will be replaced with the base names of input files.
* `outfile` is a directory: the output files will be written in it, with the same names as input files.

## Supported formats
* `tab`: [Internal tab format][1]
* `tab_noheaders`: [Internal tab format][1] without headers
* `fasta`: FASTA format
* `fasta_nogaps`: Output-only FASTA format with gaps removed
* `relaxed_phylip`: relaxed Phylip format
* `fasta_hapview`: FASTA format for Haplotype Viewer
* `phylip`: Phylip format
* `fastq`: FASTQ format
* `fasta_gbexport`: FASTA format for export into Genbank repository
* `nexus`: NEXUS format
* `nexml`: DnaCharacterMatrix in NeXML format
* `genbank`: Genbank flat file format
* `mold_fasta`: FASTA format with sequence name matching requirements for the tool MolD
* `ali_fasta`: Ali variant of the FASTA format

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
* `.xml`: NeXML format
* `.gb`: Genbank flat file format
* `.ali`: FASTA Ali format

Files with extension `.gz` are uncompressed automatically

## Adding new formats
[Link to documentation](docs/ADDING_FORMATS.md)

[1]: docs/TAB_FORMAT.md

## Options
DNAconvert uses two parsers for NEXUS format: internal (default) and the one from python-nexus package.

In the file `DNAconvert/config.json` (found in `%APPDATA%\iTaxoTools` or in `$XDG_CONFIG_HOME$/`) the key-value pair
```
"nexus_parser" : "(method)""
```
determines the parser. `(method)` is either `internal` or `python-nexus`.

## Generating an executable
Scripts for building Windows and macOS executables are included in the `tools` folder.
Executables are also built automatically using GitHub actions.

## Dependencies
Automatically installed when using pip:
* [python\-nexus](https://pypi.org/project/python-nexus/)
* [dendropy](https://pypi.org/project/DendroPy/)
