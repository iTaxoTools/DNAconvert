from .ext_ASCII_conv_table import ext_ascii_trans
from typing import List, Callable, Optional, Dict, Any
from .record import *
import re
import warnings
import unicodedata

# read by lib.utils.Unicifier._unique_limit
GLOBAL_OPTION_DISABLE_AUTOMATIC_RENAMING = False


class Aggregator:
    """Aggregates information about records
    """

    def __init__(self, *reducers: Any):
        """ Takes pairs of accumulators and reducers
        each reducer should a pure function
        that takes the current accumulator value and the current record
        and returns the new value of the accumulator
        """
        accs, reducers = zip(*reducers)
        self._accs = list(accs)
        self._reducers = list(reducers)

    def send(self, record: Record) -> None:
        """ Send a record to collect its information
        updates all the accumulators
        """
        for i, acc in enumerate(self._accs):
            self._accs[i] = self._reducers[i](acc, record)

    def results(self) -> List[Any]:
        """ Returns the current values of the accumulators
        """
        return self._accs


def _max_reducer(acc: int, record: Record) -> int:
    """
    returns the maximum between acc and the length of sequence in record
    """
    l = len(record['sequence'])
    return max(acc, l)


def _min_reducer(acc: int, record: Record) -> int:
    """
    returns the minimum between acc and the length of sequence in record
    """
    l = len(record['sequence'])
    if acc:
        return min(acc, l)
    else:
        return l


class PhylipAggregator(Aggregator):
    """
    Specialization of the Aggregator for the Phylip format
    with two default reducers
    """

    def __init__(self, *reducers: Any):
        super().__init__((0, _max_reducer), (None, _min_reducer), *reducers)


def sanitize(s: str) -> str:
    """ replaces sequence of not-alphanum characters with '_'
    replaces some extended ASCII characters with ASCII representations
    """
    s = unicodedata.normalize('NFKC', s).translate(ext_ascii_trans)
    return '_'.join(part for part in (re.split(r'[^a-zA-Z0-9]+', s)) if part)


class NameAssembler:
    """create 'seqid' for the record,
    depending on the fields given to the constructor

    the name(self, record) method is used for 'seqid' generation
    """

    @staticmethod
    def _species_abbr(species: str) -> str:
        try:
            genus, species = species.split(maxsplit=1)
        except ValueError:
            return species
        else:
            return genus[0:3] + species

    def _simple_name(self, record: Record) -> str:
        """used when there no information fields
        """
        return sanitize(record['seqid'])

    def _complex_name(self, record: Record) -> str:
        """used when information fields (all except 'seqid' and 'sequence') are present
        Their values are concatenated with underscores and forbidden character are replaced with underscores
        taking care of multiple underscores
        """
        parts = [record[field]
                 for field in self._fields if record[field] != ""]
        if self.abbreviate_species and self._fields[0] == 'species':
            parts[0] = NameAssembler._species_abbr(parts[0])
        return "_".join(map(sanitize, parts))

    def __init__(self, fields: List[str], *, abbreviate_species: bool = False):
        # copy the fields to not mutate the original
        fields = fields.copy()
        self.abbreviate_species = abbreviate_species
        try:
            # seqid should not be used for the name generation
            fields.remove('seqid')
        except ValueError:
            pass
        try:
            # only the fields before the sequence field will be used
            i = fields.index('sequence')
        except ValueError:
            pass
        else:
            # collect the relevant fields
            fields = fields[:i]
        if fields:
            # generate 'seqid' from the fields
            if 'species' in fields:
                i = fields.index('species')
                fields[0], fields[i] = fields[i], fields[0]
            self._fields = fields
            self.name = self._complex_name
        else:
            # copy the 'seqid'
            self.name = self._simple_name


def dna_aligner(max_length: int, min_length: int) -> Callable[[str], str]:
    """
    returns a function that takes a sequence and pads it to the max_length

    min_legth is used for optimisation
    """
    if max_length == min_length:
        # nothing needs to be done
        return lambda x: x
    else:
        # warn the user about the padding
        warnings.warn("The requested output format requires all sequences to be of equal length which is not the case in your input file. Probably your sequences are unaligned. To complete the conversion, dash-signs have been added at the end of the shorter sequences to adjust their length, but this may impede proper analysis - please check.")

        def dash_adder(sequence: str) -> str:
            # pad the sequences
            return sequence.ljust(max_length, '-')
        return dash_adder


def get_species_field(fields: List[str]) -> Optional[str]:
    """
    calculates the field name, that contains the species name
    """
    # allowed names
    field_names = ['organism', 'scientificname', 'identification/fullscientificnamestring',
                   'scientific name', 'scientific_name', 'species', 'speciesname', 'species name', 'species_name']
    fields_set = set(fields)
    # find the first allowed name in the given field names
    return next((field for field in field_names if field.casefold() in fields_set), None)


class Unicifier():
    """Takes care of making the names unique.
    Either overwrite the end with consecutive number, if given a length limit.
    Or keeps tracks on already seen names and prevents name collision by adding a number suffix

    use unique(self, name) method to generate a unique name based on the given one
    """

    def __init__(self, length_limit: Optional[int] = None):
        if length_limit:
            # limit-based generation
            self._length_limit = length_limit
            self._count = 0
            self.unique = self._unique_limit
        else:
            # memorization-bases generation
            self._sep = '_'
            self._seen_name: Dict[str, int] = {}
            self.unique = self._unique_set

    def _unique_limit(self, name: str) -> str:
        if GLOBAL_OPTION_DISABLE_AUTOMATIC_RENAMING:
            return name[0:self._length_limit]
        # overwrite the end with counter
        suff = str(self._count)
        self._count += 1
        return name[0:self._length_limit - len(suff)] + suff

    def _unique_set(self, name: str) -> str:
        # unless already seen, the result is the input
        uniquename = name
        try:
            # try to generate the unique name based on the memorized ones
            uniquename = name + self._sep + str(self._seen_name[name])
        except KeyError:
            # the name have not been seen before
            self._seen_name[name] = 1
        else:
            # increment the amount the name have been seen
            self._seen_name[name] += 1
        return uniquename
