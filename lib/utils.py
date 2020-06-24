import re
import warnings

class Aggregator:
    """Aggregates information about records
    """
    def __init__(self, *reducers):
        """ Takes pairs of accumulators and reducers
        each reducer should a pure function
        that takes the current accumulator value and the current record
        and returns the new value of the accumulator
        """
        accs, reducers = zip(*reducers)
        self._accs = list(accs)
        self._reducers = list(reducers)

    def send(self, record):
        """ Send a record to collect its information
        updates all the accumulators
        """
        for i, acc in enumerate(self._accs):
            self._accs[i] = self._reducers[i](acc, record)

    def results(self):
        """ Returns the current values of the accumulators
        """
        return self._accs

def _max_reducer(acc, record):
    l = len(record['sequence'])
    return max(acc, l)

def _min_reducer(acc, record):
    l = len(record['sequence'])
    if acc:
        return min(acc, l)
    else:
        return l

class PhylipAggregator(Aggregator):
    def __init__(self, *reducers):
        super().__init__((0, _max_reducer), (None, _min_reducer), *reducers)

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

def dna_aligner(max_length, min_length):
    if max_length == min_length:
        return lambda x: x
    else:
        warnings.warn("The requested output format requires all sequences to be of equal length which is not the case in your input file. Probably your sequences are unaligned. To complete the conversion, dash-signs have been added at the end of the shorter sequences to adjust their length, but this may impede proper analysis - please check.")
        def dash_adder(sequence):
            return sequence + "-" * (max_length - len(sequence))
        return dash_adder
