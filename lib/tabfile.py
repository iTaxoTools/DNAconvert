from lib.record import *

class Tabfile:
    """Class for reading and writing tab-separated files with genetic information"""

    @staticmethod
    def write(filename, fields):
        uniquenames = {} # dictionary remember the 'uniquesequencename' values that have already been seen

        with open(filename, 'w') as file:
            # write the heading
            file.write('\t'.join(fields) + '\n')

            while True:
                # receive a record
                try:
                    record = yield
                except GeneratorExit:
                    break
                # enforce uniqueness of 'uniquesequencename'
                try:
                    uniquename = record['uniquesequencename']
                    record['uniquesequencename'] += '_' + str(uniquenames[uniquename])
                    uniquenames[uniquename] += 1
                except KeyError:
                    uniquenames[record['uniquesequencename']] = 1

                # collect record fields in a list and join them with tabs
                file.writelines('\t'.join([record[field] for field in fields]) + '\n')


    @staticmethod
    def read(filename):
        with open(filename, 'r') as file:
            # read the heading for the list of fields
            fields = file.readline().rstrip('\n').split('\t')
            for required_field in ['uniquesequencename', 'sequence']:
                if required_field not in fields:
                    raise ValueError(f"Input file is not a valid genetic tab format, missing '{required_field}'")
           
        # closure that will iterate over the subsequent lines and yield the records 
        def record_generator():
            # reopen because it's a new context
            with open(filename, 'r') as file:
                # skip the first line
                file.readline()
                for line in file:
                    line = line.rstrip('\n')
                    # skip blank lines
                    if line.isspace() or line == "": continue
                    # split line into values
                    values = line.split('\t')
                    # pair them with fiels and send
                    yield Record(**{field: value for field, value in zip(fields, values)})

        # return the list of fields and the generator closure
        return fields, record_generator
