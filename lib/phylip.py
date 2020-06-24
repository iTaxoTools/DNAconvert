from lib.utils import *
from lib.record import *

class RelPhylipFile:
    @staticmethod
    def read(file):
        # Phylip always have the same fields
        fields = ['uniquesequencename', 'sequence']
        def record_generator():
            # skip the first line
            file.readline()

            for line in file:
                if line == "" or line.isspace(): continue
                name, _, sequence = line.partition(" ")
                yield Record(uniquesequencename=name, sequence=sequence)
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