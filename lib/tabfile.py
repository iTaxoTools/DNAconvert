class Tabfile:

    @staticmethod
    def write(filename, fields):
        print("TODO: make Record class for handling of uniquesequencename")
        with open(filename, 'w') as file:
            # write the heading
            file.write('\t'.join(fields))

            while True:
                # receive a record
                try:
                    record = yield
                except GeneratorExit:
                    break
                # collect record fields in a list and join them with tabs
                file.write('\t'.join([record[field] for field in fields]))


    @staticmethod
    def read(filename):
        with open(filename, 'r') as file:
            # read the heading for the list of fields
            fields = file.readline().split('\t')
           
        # closure that will iterate over the subsequent lines and yield the records 
        def record_generator():
            # reopen because it's a new context
            with open(filename, 'r') as file:
                # skip the first line
                file.readline();
                for line in file:
                    # skip blank lines
                    if line.isspace(): continue
                    # split line into values
                    values = line.split('\t')
                    # pair them with fiels and send
                    yield {field: value for field, value in zip(fields, values)}

        # return the list of fields and the generator closure
        return fields, record_generator
