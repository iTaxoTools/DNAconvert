#!/usr/bin/env python3

from typing import List, Tuple, Callable, Iterator, TextIO

from dendropy import DnaCharacterMatrix

from .record import Record


class NeXMLFile:
    """Class for NeXML files"""

    @staticmethod
    def read(file: TextIO) -> Tuple[List[str], Callable[[], Iterator[Record]]]:

        # NeXML always have the same fields
        fields = ["seqid", "sequence"]

        def record_generator() -> Iterator[Record]:
            data = DnaCharacterMatrix.get_from_stream(file, schema="nexml")
            for taxon, char_sequence in data.items():
                yield Record(
                    seqid=taxon.label, sequence=char_sequence.symbols_as_string()
                )

        return fields, record_generator
