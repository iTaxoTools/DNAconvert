import lib.tabfile as tabfile
import lib.fasta as fasta

formats = dict(
        tab = tabfile.Tabfile,
        fasta = fasta.Fastafile
        )

extensions = {
        ".tab": tabfile.Tabfile,
        ".txt": tabfile.Tabfile,
        ".tsv": tabfile.Tabfile,
        ".fas": fasta.Fastafile
        }
