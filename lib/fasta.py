import re
from lib.record import *

# replaces sequence of not-alphanum characters with '_'
def sanitize(s):
   return '_'.join(re.split(r'[^a-zA-Z0-9]+', s)) 

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
        # copy fields to avoid mutating the reader copy
        fields = fields.copy()

        # now fields contain only the fields' name which comprise the sequence name in FASTA
        try:
            fields.remove('uniquesequencename')
        except ValueError:
            pass
        fields.remove('sequence')

        while True:
            # receive a record
            try:
                record = yield
            except GeneratorExit:
                break

            # print the name line
            if fields:
                print('>', end='', file=file)
                print(*[sanitize(record[field]) for field in fields if record[field] != ""], sep='_', file=file)
            else:
                # executed if the input file is FASTA
                print('>', record['uniquesequencename'], sep="", file=file)

            # print the sequence
            print(record['sequence'], file=file)

    @staticmethod
    def read(file):
        # FASTA always have the same fields
        fields = ['uniquesequencename', 'sequence']
        def record_generator():
            for chunk in split_file(file):
                # 'uniquesequencename' is the first line without the initial character
                # 'sequence' is the concatenation of all the other lines
                yield Record(uniquesequencename=chunk[0][1:], sequence="".join(chunk[1:]))
        return fields, record_generator
