import re
def sanitize(s):
   return '_'.join(re.split(r'[^a-zA-Z0-9]+', s)) 

class Fastafile:
    @staticmethod
    def write(filename, fields):
        fields = fields.copy()
        try:
            fields.remove('uniquesequencename')
        except ValueError:
            pass
        fields.remove('sequence')
        with open(filename, 'w') as file:
            while True:
                try:
                    record = yield
                except GeneratorExit:
                    break
                print('>', end='', file=file)
                print(*[sanitize(record[field]) for field in fields if record[field] != ""], sep='_', file=file)
                print(record['sequence'], file=file)
