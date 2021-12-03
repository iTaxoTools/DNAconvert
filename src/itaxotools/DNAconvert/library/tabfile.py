from typing import TextIO, List, Tuple, Callable, Iterator, Generator
from .utils import *
from .record import *


class Tabfile:
    """Class for reading and writing tab-separated files with genetic information"""

    @staticmethod
    def write(file: TextIO, fields: List[str]) -> Generator:
        """
        the writer method for tab format
        """
        if 'seqid' not in fields:
            raise ValueError("Tab format expects a 'seqid'")

        # write the heading
        file.write('\t'.join(fields) + '\n')

        while True:
            # receive a record
            try:
                record = yield
            except GeneratorExit:
                break
            # enforce name uniqueness
            unicifier = Unicifier()
            record['seqid'] = unicifier.unique(record['seqid'])

            # collect record fields in a list and join them with tabs
            file.writelines('\t'.join([record[field]
                                       for field in fields]) + '\n')

    @staticmethod
    def read(file: TextIO) -> Tuple[List[str], Callable[[], Iterator[Record]]]:
        """
        the reader method for tab format
        """
        # read the heading for the list of fields
        fields = file.readline().rstrip('\n').split('\t')
        fields = list(map(str.casefold, fields))
        if 'seqid' not in fields and len(fields) >= 2:
            warnings.warn(
                "The column 'seqid' is missing. Conversion will proceed, but please check the converted file for correctness.")
        if 'sequence' not in fields:
            sequence_candidates = [i for i, field in enumerate(
                fields) if 'sequence' in field]
            if len(sequence_candidates) == 1:
                warnings.warn("The column 'sequence' is missing, but another column header containing the same term was found and is interpreted as containing the sequences. Conversion will proceed, but please check the converted file for correctness")
                i = sequence_candidates[0]
                fields[i] = 'sequence'
            elif len(sequence_candidates) > 1:
                i = sequence_candidates[0]
                warnings.warn(
                    f"The column 'sequence' is missing, the column '{fields[i]}' is interpreted as containing the sequences. Conversion will proceed, but please check the converted file for correctness")
                fields[i] = 'sequence'
            else:
                warnings.warn(
                    f"The column 'sequence' is missing, the last column '{fields[-1]}' is interpreted as containing the sequences. Conversion will proceed, but please check the converted file for correctness")
                fields[-1] = 'sequence'

        # closure that will iterate over the subsequent lines and yield the records

        def record_generator() -> Iterator[Record]:
            for line in file:
                line = line.rstrip('\n')
                # skip blank lines
                if line.isspace() or line == "":
                    continue
                # split line into values
                values = line.split('\t')
                # pair them with fiels and send
                yield Record(**{field: value for field, value in zip(fields, values)})

        # return the list of fields and the generator closure
        return fields, record_generator


class NoHeaderTab:
    """Class for reading and writing tab-separated files without headers with genetic information"""

    dna_characters = set("ATGCRYMKSWBDHVNUatgcrymkswbdhvnu-?")

    @staticmethod
    def is_sequence(s: str) -> bool:
        return all(map(lambda c: c in NoHeaderTab.dna_characters, s))

    @staticmethod
    def write(file: TextIO, fields: List[str]) -> Generator:
        """
        the writer method for 'tab-no headers' format
        """

        while True:
            # receive a record
            try:
                record = yield
            except GeneratorExit:
                break

            # collect record fields in a list and join them with tabs
            file.writelines('\t'.join([record[field]
                                       for field in fields]) + '\n')

    @staticmethod
    def read(file: TextIO) -> Tuple[List[str], Callable[[], Iterator[Record]]]:
        """
        the reader method for 'tab-no headers' format
        """
        # always the same heading
        fields = ['seqid', 'sequence']

        # closure that will iterate over the subsequent lines and yield the records

        def record_generator() -> Iterator[Record]:
            sequence_index = -1
            first_line = True

            for line in file:
                line = line.rstrip('\n')
                # skip blank lines
                if line.isspace() or line == "":
                    continue
                # split line into values
                values = [value for value in line.split('\t') if value]

                # Test if the first column is more probable to be a sequence
                if first_line:
                    if not NoHeaderTab.is_sequence(values[-1]) and NoHeaderTab.is_sequence(values[0]):
                        sequence_index = 0
                        warnings.warn(
                            "The last column contains non-standard DNA characters. The first column is assumed to be the sequence column")
                    first_line = False

                sequence = values.pop(sequence_index)
                seqid = "_".join(sanitize(value) for value in values)

                yield Record(seqid=seqid, sequence=sequence)

        # return the list of fields and the generator closure
        return fields, record_generator
