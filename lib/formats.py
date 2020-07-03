import lib.tabfile as tabfile
import lib.fasta as fasta
import lib.phylip as phylip

formats = dict(
        tab = tabfile.Tabfile,
        fasta = fasta.Fastafile,
        relaxed_phylip = phylip.RelPhylipFile,
        fasta_hapview = fasta.HapviewFastafile,
        phylip = phylip.PhylipFile,
        fastq = fasta.FastQFile,
        fasta_genbank = fasta.GenbankFastaFile,
        )

extensions = {
        ".tab": tabfile.Tabfile,
        ".txt": tabfile.Tabfile,
        ".tsv": tabfile.Tabfile,
        ".fas": fasta.Fastafile,
        ".rel.phy": phylip.RelPhylipFile,
        ".hapv.fas": fasta.HapviewFastafile,
        ".phy": phylip.PhylipFile,
        ".fastq": fasta.FastQFile,
        ".fq": fasta.FastQFile,
        ".fastq.gz": fasta.FastQFile,
        ".fq.gz": fasta.FastQFile,
        ".gz": fasta.FastQFile,
        ".gb.fas": fasta.GenbankFastaFile,
        }
