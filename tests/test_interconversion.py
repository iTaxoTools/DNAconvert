#!/usr/bin/env python

from pathlib import Path
from typing import Dict
from io import StringIO

import pytest

from itaxotools.DNAconvert import convertDNA  # type: ignore
from itaxotools.DNAconvert.library.formats import formats, informats_gui, outformats_gui  # type: ignore
from itaxotools.DNAconvert.library import tabfile  # type: ignore

testfiles_path: Path = Path(__file__).parent / "test_files"


format_names: Dict[str, str] = {
    "MolD_examplefile1_PontohedyleCOI_iTaxoTools_0_1.fas": "mold_fasta",
    "MolD_examplefile2_LophiotomaNICOI_iTaxoTools_0_1.fas": "mold_fasta",
    "ali_example_file_1.ali": "ali_fasta",
    "ali_example_file_2.ali": "ali_fasta",
}


@pytest.mark.parametrize("name, format_name", format_names.items())
def test_into_tab(name: str, format_name: str) -> None:
    if format_name not in informats_gui:
        return
    testfile = testfiles_path / name
    out_testfile = testfile
    while out_testfile != out_testfile.with_suffix(""):
        out_testfile = out_testfile.with_suffix("")
    out_testfile = out_testfile.with_suffix(".tab")
    with StringIO() as output, testfile.open() as input:
        convertDNA(
            input,
            output,
            formats[format_name],
            tabfile.Tabfile,
            allow_empty_sequences=False,
            automatic_renaming=False,
            preserve_spaces=False,
        )
        assert output.getvalue().splitlines() == out_testfile.read_text().splitlines()


@pytest.mark.parametrize("name, format_name", format_names.items())
def test_from_tab(name: str, format_name: str) -> None:
    if format_name not in outformats_gui:
        return
    testfile = testfiles_path / name
    in_testfile = testfile
    while in_testfile != in_testfile.with_suffix(""):
        in_testfile = in_testfile.with_suffix("")
    in_testfile = in_testfile.with_suffix(".tab")
    with StringIO() as output, in_testfile.open() as input:
        convertDNA(
            input,
            output,
            tabfile.Tabfile,
            formats[format_name],
            allow_empty_sequences=False,
            automatic_renaming=False,
            preserve_spaces=False,
        )
        if format_name == "ali_fasta":
            # todo: find a good way to compare `output` and `testfile` for Ali format
            return
        else:
            assert output.getvalue().splitlines() == testfile.read_text().splitlines()
