from lib.utils import *
from lib.record import *

class RelPhylipFile:
    @staticmethod
    def read(file):
        # Phylip always have the same fields
        fields = ['seqid', 'sequence']
        def record_generator():
            # skip the first line
            file.readline()

            for line in file:
                # skip blank lines
                if line == "" or line.isspace(): continue
                # separate name and sequence
                name, _, sequence = line.partition(" ")
                # skip if there is no sequence
                if sequence == "" or sequence.isspace(): continue
                # return the record
                yield Record(seqid=name, sequence=sequence)
        return fields, record_generator

    @staticmethod
    def write(file, fields):
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
            print(name_assembler.name(record), aligner(record['sequence']), file=file)

class PhylipFile:
    @staticmethod
    def read(file):
        # Phylip always have the same fields
        fields = ['seqid', 'sequence']
        def record_generator():
            # skip the first line
            file.readline()

            for line in file:
                if line == "" or line.isspace(): continue
                # skip is there is no sequence
                if len(line) < 10: continue
                name = line[0:10]
                sequence = line[10:]
                yield Record(seqid=name, sequence=sequence)
        return fields, record_generator

    @staticmethod
    def write(file, fields):
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
            print(unicifier.unique(name_assembler.name(record)), aligner(record['sequence']), sep="", file=file)
