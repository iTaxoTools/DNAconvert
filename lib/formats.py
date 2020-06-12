import lib.tabfile as tabfile

formats = dict(
        tab = tabfile.Tabfile
        )

extensions = {
        ".tab": tabfile.Tabfile,
        ".txt": tabfile.Tabfile,
        ".tsv": tabfile.Tabfile
        }
