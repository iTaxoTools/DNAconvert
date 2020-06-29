from lib.record import *
from lib.utils import *

class Tabfile:
    """Class for reading and writing tab-separated files with genetic information"""

    @staticmethod
    def write(file, fields):
        if 'uniquesequencename' not in fields:
            raise ValueError("Tab format expects a 'uniquesequencename'")

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
            record['uniquesequencename'] = unicifier.unique(record['uniquesequencename'])

            # collect record fields in a list and join them with tabs
            file.writelines('\t'.join([record[field] for field in fields]) + '\n')


    @staticmethod
    def read(file):
        # read the heading for the list of fields
        fields = file.readline().rstrip('\n').split('\t')
        fields = list(map(str.casefold, fields))
        for required_field in ['uniquesequencename', 'sequence']:
            if required_field not in fields:
                raise ValueError(f"Input file is not a valid genetic tab format, missing '{required_field}'")
           
        # closure that will iterate over the subsequent lines and yield the records 
        def record_generator():
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
