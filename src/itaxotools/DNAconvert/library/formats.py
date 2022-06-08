from typing import Dict, Type, Any
from . import tabfile
from . import fasta
from . import phylip
from . import nexus
from . import genbank
from . import nexml
from .config import get_config


config = get_config()
if config.nexus_parser == "python-nexus":
    nexus_format = nexus.NexusFileSimple
elif config.nexus_parser == "internal":
    nexus_format = nexus.NexusFile
else:
    raise ValueError(
        "The value of 'nexus_parser' in 'config.json' should be either 'python-nexus' or 'internal'"
    )

# formats' names dictionary
formats: Dict[str, Type[Any]] = dict(
    tab=tabfile.Tabfile,
    tab_noheaders=tabfile.NoHeaderTab,
    fasta=fasta.Fastafile,
    relaxed_phylip=phylip.RelPhylipFile,
    fasta_hapview=fasta.HapviewFastafile,
    phylip=phylip.PhylipFile,
    fastq=fasta.FastQFile,
    fasta_gbexport=fasta.GenbankFastaFile,
    nexus=nexus_format,
    nexml=nexml.NeXMLFile,
    genbank=genbank.GenbankFile,
    mold_fasta=fasta.MolDFastaFile,
)

informats_gui = list(formats.keys())
informats_gui.remove("fasta_hapview")

outformats_gui = list(formats.keys())
outformats_gui.remove("fasta_hapview")
outformats_gui.remove("genbank")

# extensions' dictionary
extensions = {
    ".tab": tabfile.Tabfile,
    ".txt": tabfile.Tabfile,
    ".tsv": tabfile.Tabfile,
    ".fas": fasta.Fastafile,
    ".fna": fasta.Fastafile,
    ".fasta": fasta.Fastafile,
    ".rel.phy": phylip.RelPhylipFile,
    ".hapv.fas": fasta.HapviewFastafile,
    ".phy": phylip.PhylipFile,
    ".fastq": fasta.FastQFile,
    ".fq": fasta.FastQFile,
    ".fastq.gz": fasta.FastQFile,
    ".fq.gz": fasta.FastQFile,
    ".gz": fasta.FastQFile,
    ".gb.fas": fasta.GenbankFastaFile,
    ".nex": nexus_format,
    ".gb": genbank.GenbankFile,
    ".xml": nexml.NeXMLFile,
}
