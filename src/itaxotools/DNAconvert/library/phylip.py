import warnings
from .utils import *
from .record import *
from typing import TextIO, Tuple, List, Callable, Iterator, Generator


class RelPhylipFile:
    """
    class for the relaxed Phylip format
    """
    @staticmethod
    def read(file: TextIO) -> Tuple[List[str], Callable[[], Iterator[Record]]]:
        """
        the reader method for the relaxed Phylip format
        """
        # Phylip always have the same fields
        fields = ['seqid', 'sequence']

        def record_generator() -> Iterator[Record]:
            # skip the first line
            file.readline()

            for line in file:
                # skip blank lines
                if line == "" or line.isspace():
                    continue
                # separate name and sequence
                name, _, sequence = line.partition(" ")
                # return the record
                yield Record(seqid=name, sequence=sequence)
        return fields, record_generator

    @staticmethod
    def write(file: TextIO, fields: List[str]) -> Generator:
        """
        the writer method for the relaxed Phylip format
        """
        # aggregate information about minumum and maximum length of the sequences
        aggregator = PhylipAggregator()
        records = []

        while True:
            try:
                record = yield
            except GeneratorExit:
                break
            aggregator.send(record)
            records.append(record)

        # extract the aggregate information
        [max_length, min_length] = aggregator.results()

        # formats all the sequences to the same maximum length
        aligner = dna_aligner(max_length, min_length)
        # generate the seqid from the fields
        name_assembler = NameAssembler(fields)

        # print the relaxed Phylip heading
        print(len(records), max_length, file=file)

        # print the records
        for record in records:
            print(name_assembler.name(record), aligner(
                record['sequence']), file=file)


class PhylipFile:
    """
    class for the Phylip format
    """
    @staticmethod
    def read(file: TextIO) -> Tuple[List[str], Callable[[], Iterator[Record]]]:
        """
        the reader method for the Phylip format
        """
        # Phylip always have the same fields
        fields = ['seqid', 'sequence']

        def record_generator() -> Iterator[Record]:
            # skip the first line
            file.readline()

            for line in file:
                # skip the blank lines
                if line == "" or line.isspace():
                    continue
                # name is the first 10 characters
                name = line[0:10]
                # everything else in the sequence
                sequence = line[10:]
                yield Record(seqid=name, sequence=sequence)
        return fields, record_generator

    @staticmethod
    def write(file: TextIO, fields: List[str]) -> Generator:
        """
        the writer method for the Phylip format
        """
        # aggregate the minimum and maximum length of sequences
        aggregator = PhylipAggregator()
        records = []

        while True:
            try:
                record = yield
            except GeneratorExit:
                break
            aggregator.send(record)
            records.append(record)

        # extract the aggragate information
        [max_length, min_length] = aggregator.results()

        # formats all the sequences to the same maximum length
        aligner = dna_aligner(max_length, min_length)
        # generate the seqid from the fields
        name_assembler = NameAssembler(fields, abbreviate_species=True)
        # makes seqid unique within 10 characters
        unicifier = Unicifier(10)

        # write the Phylip heading
        print(len(records), max_length, file=file)

        # write the records
        for record in records:
            print(unicifier.unique(name_assembler.name(record)),
                  aligner(record['sequence']), sep=" ", file=file)
