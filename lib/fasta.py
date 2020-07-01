import re
import warnings
from lib.record import *
from lib.utils import *


# Yields a list of lines that comprise one FASTA record
def split_file(file):

    # find the beginning of the first record
    line = " "
    while line[0] != '>':
        line = file.readline()

    # chunk contains the already read lines of the current record
    chunk = []
    chunk.append(line.rstrip())

    for line in file:
        # skip the blank lines
        if line == "" or line.isspace(): continue

        # yield the chunk if the new record has begun
        if line[0] == '>':
            yield chunk
            chunk = []

        chunk.append(line.rstrip())

    # yield the last record
    yield chunk

class Fastafile:
    @staticmethod
    def write(file, fields):
        name_assembler = NameAssembler(fields)

        while True:
            # receive a record
            try:
                record = yield
            except GeneratorExit:
                break

            # print the unique name
            print(">", name_assembler.name(record), sep="", file=file)

            # print the sequence
            print(record['sequence'], file=file)

    @staticmethod
    def read(file):
        # FASTA always have the same fields
        fields = ['seqid', 'sequence']
        def record_generator():
            skipped = 0
            for chunk in split_file(file):
                # skip if there is no sequence
                if len(chunk) <= 1: 
                    skipped += 1
                    continue
                # 'seqid' is the first line without the initial character
                # 'sequence' is the concatenation of all the other lines
                yield Record(seqid=chunk[0][1:], sequence="".join(chunk[1:]))
            if skipped > 0: warnings.warn(f"{skipped} records did not contain a sequence and are therefore not included in the converted file")
        return fields, record_generator

class UnicifierSN(Unicifier):
    def __init__(self, length_limit=None):
        super().__init__(length_limit)
        self._sep = ""

class SpeciesNamer:
    """makes correspondence between long species name in the record and unique short names
    """
    def __init__(self, species, species_field):
        if not species_field:
            self._count = 0
            self.name = self._count_name
            return
        # make list of pair of species and first 4 letters of the second part of the name
        def short_name(name):
            _, second_part = re.split(r'[ _]', name, maxsplit=1)
            try:
                return second_part[0:4]
            except IndexError:
                raise ValueError(f"Malformed species name {name}")
        unicifier = UnicifierSN()
        self._species_field = species_field
        self._species = {long_name: unicifier.unique(short_name(long_name)) for long_name in species}
        self.name = self._dict_name

    def _count_name(self, record):
        self._count += 1
        return str(self._count - 1)

    def _dict_name(self, record):
        return self._species[record[self._species_field]]

class HapviewFastafile:
    @staticmethod
    def read(file):
        # FASTA always have the same fields
        fields = ['seqid', 'sequence']
        def record_generator():
            skipped = 0
            for chunk in split_file(file):
                # skip if there is no sequence
                if len(chunk) <= 1: 
                    skipped += 1
                    continue
                # 'seqid' is the first line without the initial character
                # 'sequence' is the concatenation of all the other lines
                yield Record(seqid=chunk[0][1:], sequence="".join(chunk[1:]))
            if skipped > 0: warnings.warn(f"{skipped} records did not contain a sequence and are therefore not included in the converted file")
        return fields, record_generator

    @staticmethod
    def write(file, fields):
        species_field = get_species_field(fields)
        if species_field:
            def species_reducer(acc, record):
                acc.add(record[species_field])
                return acc
            aggregator = PhylipAggregator((set(), species_reducer))
        else:
            aggregator = PhylipAggregator()
        records = []
        
        while True:
            try:
                record = yield
            except GeneratorExit:
                break
            aggregator.send(record)
            records.append(record)
        
        [max_length, min_length, species] = aggregator.results()
        species_namer = SpeciesNamer(species, species_field)

        aligner = dna_aligner(max_length, min_length)
        name_assembler = NameAssembler(fields)
        unicifier = Unicifier(100)

        for record in records:
            print('>', unicifier.unique(name_assembler.name(record)), '.', species_namer.name(record), sep="", file=file)
            print(aligner(record['sequence']), file=file)

class FastQFile:
    
    @staticmethod
    def to_fasta(infile, outfile):
        for line in infile:
            if line[0] == '@':
                print('>', line[1:], sep="", end="", file=outfile)
                line = infile.readline()
                print(line, file=outfile, end="")

    @staticmethod
    def read(file):
        fields = ['seqid', 'sequence', 'quality_score_identifier', 'quality_score']
        def record_generator():
            for line in file:
                if line[0] == '@':
                    seqid = line[1:].rstrip()
                    sequence = file.readline().rstrip()
                    quality_score_identifier = file.readline().rstrip()
                    quality_score = file.readline().rstrip()
                    yield Record(seqid=seqid, sequence=sequence, quality_score_identifier=quality_score_identifier, quality_score=quality_score)
        return fields, record_generator

    @staticmethod
    def write(file, fields):
        if not {'seqid', 'sequence', 'quality_score_identifier', 'quality_score'} <= set(fields):
            raise ValueError('FastQ requires the fields seqid, sequence, quality_score_identifier and quality_score')
        while True:
            try:
                record = yield
            except GeneratorExit:
                break
            print('@', record['seqid'], sep="", file=file)
            for field in ['sequence', 'quality_score_identifier', 'quality_score']:
                print(record[field], file=file)
