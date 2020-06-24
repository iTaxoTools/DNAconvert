import re

class Aggregator:
    """Aggregates information about records
    """
    def __init__(self, *reducers):
        """ Takes pairs of accumulators and reducers
        each reducer should a pure function
        that takes the current accumulator value and the current record
        and returns the new value of the accumulator
        """
        self._accs, self._reducers = zip(*reducers)

    def send(self, record):
        """ Send a record to collect its information
        updates all the accumulators
        """
        for i, acc in self._accs.enumerate():
            self._accs[i] = self._reducers[i](acc, record)

    def results(self):
        """ Returns the current values of the accumulators
        """
        return self._accs

def sanitize(s):
    """ replaces sequence of not-alphanum characters with '_'
    """
    return '_'.join(part for part in (re.split(r'[^a-zA-Z0-9]+', s)) if part) 

class NameAssembler:
    """create 'uniquesequencename' for the record,
    depending on the fields given to the constructor
    """

    def _simple_name(self, record):
        """used when there no information fields
        """
        return record['uniquesequencename']

    def _complex_name(self, record):
        """used when information fields (all except 'uniquesequencename' and 'sequence') are present
        Their values are concatenated with underscores and forbidden character are replaced with underscores
        taking care of multiple underscores
        """
        return "_".join(sanitize(record[field]) for field in self._fields if record[field] != "")

    def __init__(self, fields):
        fields = fields.copy()
        try:
           fields.remove('uniquesequencename')
           fields.remove('sequence')
        except ValueError:
            pass
        if fields:
            self._fields = fields
            self.name = self._complex_name
        else:
            self.name = self._simple_name
