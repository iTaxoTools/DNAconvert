import lib.tabfile as tabfile
import lib.fasta as fasta
import lib.phylip as phylip

formats = dict(
        tab = tabfile.Tabfile,
        fasta = fasta.Fastafile,
        relaxed_phylip = phylip.RelPhylipFile,
        fasta_hapview = fasta.HapviewFastafile,
        )

extensions = {
        ".tab": tabfile.Tabfile,
        ".txt": tabfile.Tabfile,
        ".tsv": tabfile.Tabfile,
        ".fas": fasta.Fastafile,
        ".rel.phy": phylip.RelPhylipFile,
        ".hapv.fas": fasta.HapviewFastafile,
        }
