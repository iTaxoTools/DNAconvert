#!/usr/bin/env python3

from PyInstaller.utils.hooks import collect_data_files
datas = collect_data_files('itaxotools.DNAconvert', subdir='resources')
