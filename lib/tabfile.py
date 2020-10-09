from typing import TextIO, List, Tuple, Callable, Iterator, Generator
from lib.utils import *
from lib.record import *


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
                "The field 'seqid' is missing. Conversion will proceed, but please check the converted file for correctness.")
        if 'sequence' not in fields:
            if len(sequence_candidates := [i for i, field in enumerate(fields) if 'sequence' in field]) == 1:
                warnings.warn("The field 'sequence' is missing, but another field containing the same term was found and is interpreted as containing the sequences. Conversion will proceed, but please check the converted file for correctness")
                i = sequence_candidates[0]
                fields[i] = 'sequence'

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
