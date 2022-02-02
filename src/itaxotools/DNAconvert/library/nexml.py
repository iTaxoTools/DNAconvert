#!/usr/bin/env python3

from typing import List, Tuple, Callable, Iterator, TextIO, Generator, Dict

from dendropy import DnaCharacterMatrix

from .record import Record
from .utils import NameAssembler


class NeXMLFile:
    """Class for NeXML files"""

    @staticmethod
    def write(file: TextIO, fields: List[str]) -> Generator:
        """NeXML writer method"""

        name_assembler = NameAssembler(fields)
        sequence_dict: Dict[str, str] = {}

        while True:
            try:
                record = yield
            except GeneratorExit:
                break
            sequence_dict[name_assembler.name(record)] = record["sequence"]

        data = DnaCharacterMatrix.from_dict(sequence_dict)
        data.write_to_stream(file, schema="nexml", markup_as_sequences=True)

    @staticmethod
    def read(file: TextIO) -> Tuple[List[str], Callable[[], Iterator[Record]]]:
        """NeXML reader method"""

        # NeXML always have the same fields
        fields = ["seqid", "sequence"]

        def record_generator() -> Iterator[Record]:
            data = DnaCharacterMatrix.get_from_stream(file, schema="nexml")
            for taxon, char_sequence in data.items():
                yield Record(
                    seqid=taxon.label, sequence=char_sequence.symbols_as_string()
                )

        return fields, record_generator
