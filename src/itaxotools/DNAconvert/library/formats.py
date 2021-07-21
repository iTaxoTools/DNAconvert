from typing import Dict, Type, Any
import os
import DNAconvert.library.tabfile as tabfile
import DNAconvert.library.fasta as fasta
import DNAconvert.library.phylip as phylip
import DNAconvert.library.nexus as nexus
import DNAconvert.library.genbank as genbank

cfg_dict = {}
for line in open(os.path.join("data", "cfg.tab")).readlines():
    option, _, value = line.strip().partition("\t")
    cfg_dict[option] = value

if cfg_dict["nexus_parser"] == "python-nexus":
    nexus_format = nexus.NexusFileSimple
elif cfg_dict["nexus_parser"] == "internal":
    nexus_format = nexus.NexusFile
else:
    raise ValueError(
        f"The value of 'nexus_parser' in {os.path.join('data', 'cfg.tab')} should be either 'python-nexus' or 'internal'"
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
    genbank=genbank.GenbankFile,
    moid_fas=fasta.MoidFastaFile,
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
    ".fasta": fasta.Fastafile,
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
}
