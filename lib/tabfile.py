class Tabfile:

    @staticmethod
    def write(file, fields):
        print(f"Making file {file} with fields {fields}")
        record = yield
        print(f"Received record {record}")

    @staticmethod
    def read(file):
        def record_generator():
            yield {}
        return {}, record_generator
