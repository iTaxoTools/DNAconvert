import warnings
from lib.utils import *
from lib.record import *
from typing import TextIO, Tuple, List, Callable, Iterator, Generator


class RelPhylipFile:
    @staticmethod
    def read(file: TextIO) -> Tuple[List[str], Callable[[], Iterator[Record]]]:
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
        aggregator = PhylipAggregator()
        records = []

        while True:
            try:
                record = yield
            except GeneratorExit:
                break
            aggregator.send(record)
            records.append(record)

        [max_length, min_length] = aggregator.results()

        aligner = dna_aligner(max_length, min_length)
        name_assembler = NameAssembler(fields)

        print(len(records), max_length, file=file)

        for record in records:
            print(name_assembler.name(record), aligner(
                record['sequence']), file=file)


class PhylipFile:
    @staticmethod
    def read(file: TextIO) -> Tuple[List[str], Callable[[], Iterator[Record]]]:
        # Phylip always have the same fields
        fields = ['seqid', 'sequence']

        def record_generator() -> Iterator[Record]:
            # skip the first line
            file.readline()

            for line in file:
                if line == "" or line.isspace():
                    continue
                name = line[0:10]
                sequence = line[10:]
                yield Record(seqid=name, sequence=sequence)
        return fields, record_generator

    @staticmethod
    def write(file: TextIO, fields: List[str]) -> Generator:
        aggregator = PhylipAggregator()
        records = []

        while True:
            try:
                record = yield
            except GeneratorExit:
                break
            aggregator.send(record)
            records.append(record)

        [max_length, min_length] = aggregator.results()

        aligner = dna_aligner(max_length, min_length)
        name_assembler = NameAssembler(fields)
        unicifier = Unicifier(10)

        print(len(records), max_length, file=file)

        for record in records:
            print(unicifier.unique(name_assembler.name(record)),
                  aligner(record['sequence']), sep="", file=file)
