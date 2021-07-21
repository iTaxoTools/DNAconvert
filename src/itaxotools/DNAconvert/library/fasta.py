import re
import warnings
from .record import *
from .utils import *
from typing import TextIO, Iterator, List, Generator, Tuple, Set


def split_file(file: TextIO) -> Iterator[List[str]]:
    """
    Returns iterator that yield records as lists of lines
    """
    # find the beginning of the first record
    line = " "
    while line[0] != '>':
        line = file.readline()

    # chunk contains the already read lines of the current record
    chunk = []
    # put the first line of the first record into chunk
    chunk.append(line.rstrip())

    for line in file:
        # skip the blank lines
        if line == "" or line.isspace():
            continue

        # yield the chunk if the new record has begun
        if line[0] == '>':
            yield chunk
            chunk = []

        # put the first line of the new record into chunk
        chunk.append(line.rstrip())

    # yield the last record
    yield chunk


class Fastafile:
    """ Class for standard FASTA files"""

    @staticmethod
    def write(file: TextIO, fields: List[str]) -> Generator:
        """FASTA writer method"""
        # the standard NameAssembler
        name_assembler = NameAssembler(fields)

        # the writing loop
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
    def read(file: TextIO) -> Tuple[List[str], Callable[[], Iterator[Record]]]:
        """FASTA reader method"""

        # FASTA always have the same fields
        fields = ['seqid', 'sequence']

        def record_generator() -> Iterator[Record]:
            for chunk in split_file(file):
                # 'seqid' is the first line without the initial character
                # 'sequence' is the concatenation of all the other lines
                yield Record(seqid=chunk[0][1:], sequence="".join(chunk[1:]))
        return fields, record_generator


class UnicifierSN(Unicifier):
    """
    Unicifier specialized to generate species names for Hapview

    It appends numbers without a separation character
    """

    def __init__(self, length_limit: Optional[int] = None):
        super().__init__(length_limit)
        self._sep = ""


class SpeciesNamer:
    """
    Makes correspondence between long species name in the record and unique short names

    name(record: Record) -> str
        returns Hapview short species name for the given record
    """

    def __init__(self, species: Set[str], species_field: Optional[str]):
        """
        species is the set of species' names in the input file.
        species_field is the name of the field that contains the species' name
        """
        # if the species' name is not given
        # self.name returns consecutive numbers
        if not species_field:
            self._count = 0
            self.name = self._count_name
            return

        def short_name(name: str) -> str:
            """Takes a binomial name and return the first 4 letters of the species part"""
            _, second_part = re.split(r'[ _]', name, maxsplit=1)
            try:
                return second_part[0:4]
            except IndexError:
                raise ValueError(f"Malformed species name {name}")

        # make Unicifier for the short names
        unicifier = UnicifierSN()

        # save the field name
        self._species_field = species_field
        # generate a dictionary from the binomial name to the unique short name
        self._species = {long_name: unicifier.unique(
            short_name(long_name)) for long_name in species}
        # self.name does the lookup in the above dictionary
        self.name = self._dict_name

    def _count_name(self, record: Record) -> str:
        self._count += 1
        return str(self._count - 1)

    def _dict_name(self, record: Record) -> str:
        return self._species[record[self._species_field]]


class HapviewFastafile:
    """class for the FASTA format of the Haplotype Viewer"""

    @ staticmethod
    def read(file: TextIO) -> Tuple[List[str], Callable[[], Iterator[Record]]]:
        """
        FASTA Hapview reader method

        The same as for the standard FASTA     
        """
        # FASTA always have the same fields
        fields = ['seqid', 'sequence']

        def record_generator() -> Iterator[Record]:
            for chunk in split_file(file):
                # 'seqid' is the first line without the initial character
                # 'sequence' is the concatenation of all the other lines
                yield Record(seqid=chunk[0][1:], sequence="".join(chunk[1:]))
        return fields, record_generator

    @ staticmethod
    def write(file: TextIO, fields: List[str]) -> Generator:
        """FASTA Hapview writer method"""
        # if there is a field with the name of the species
        # then aggregate the names into a set
        # else use the standard Phylip Aggregator
        species_field = get_species_field(fields)
        if species_field:
            def species_reducer(acc: Set[str], record: Record) -> Set[str]:
                assert species_field is not None
                acc.add(record[species_field])
                return acc
            aggregator = PhylipAggregator((set(), species_reducer))
        else:
            aggregator = PhylipAggregator()

        # collect the record and aggregate the information about them
        records = []
        while True:
            try:
                record = yield
            except GeneratorExit:
                break
            aggregator.send(record)
            records.append(record)
        [max_length, min_length, species] = aggregator.results()

        # will create the short species' names
        species_namer = SpeciesNamer(species, species_field)
        # will ensure that all sequences have the same length
        aligner = dna_aligner(max_length, min_length)
        # creates or copies the seqid
        name_assembler = NameAssembler(fields)
        # makes the seqid unique
        unicifier = Unicifier(100)

        # write the records
        for record in records:
            print('>', unicifier.unique(name_assembler.name(record)),
                  '.', species_namer.name(record), sep="", file=file)
            print(aligner(record['sequence']), file=file)


class FastQFile:
    """class for the FastQ format"""

    @ staticmethod
    def to_fasta(infile: TextIO, outfile: TextIO) -> None:
        """Quick conversion from FastQ to FASTA"""
        for line in infile:
            # loop through lines until the start of a record
            if line[0] == '@':
                # copy the seqid
                print('>', line[1:], sep="", end="", file=outfile)
                # copy the sequence
                line = infile.readline()
                print(line, file=outfile, end="")

    @ staticmethod
    def read(file: TextIO) -> Tuple[List[str], Callable[[], Iterator[Record]]]:
        """FastQ reader method"""
        # FastQ always have the same fields
        fields = ['seqid', 'sequence',
                  'quality_score_identifier', 'quality_score']

        def record_generator() -> Iterator[Record]:
            for line in file:
                # loop until the start of a record
                # then read 4 lines and yield them as a record
                if line[0] == '@':
                    seqid = line[1:].rstrip()
                    sequence = file.readline().rstrip()
                    quality_score_identifier = file.readline().rstrip()
                    quality_score = file.readline().rstrip()
                    yield Record(seqid=seqid, sequence=sequence, quality_score_identifier=quality_score_identifier, quality_score=quality_score)
        return fields, record_generator

    @ staticmethod
    def write(file: TextIO, fields: List[str]) -> Generator:
        """FastQ writer method"""

        # check that all the required fields are present
        if not {'seqid', 'sequence', 'quality_score_identifier', 'quality_score'} <= set(fields):
            raise ValueError(
                'FastQ requires the fields seqid, sequence, quality_score_identifier and quality_score')

        while True:
            # get the record
            try:
                record = yield
            except GeneratorExit:
                break
            # write the name
            print('@', record['seqid'], sep="", file=file)
            # write the other attributes
            for field in ['sequence', 'quality_score_identifier', 'quality_score']:
                print(record[field], file=file)


class NameAssemblerGB(NameAssembler):
    """
    A specialization of NameAssembler of Genbank FASTA. 

    It gives the higher priority to copying the seqid. Otherwise it is assembled from the organism and specimen_voucher field"""

    def __init__(self, fields: List[str]):
        if 'seqid' in fields:
            self.name = self._simple_name
        else:
            self._fields = [field for field in [
                'organism', 'specimen_voucher'] if field in fields]
            self.name = self._complex_name


class GenbankFastaFile:
    """class for the Genbank FASTA submission format"""

    # the list of Genbank fields
    genbankfields = ['seqid', 'organism', 'accession', 'specimen-voucher', 'strain', 'isolate', 'country', 'sequence', 'mol-type', 'altitude', 'bio-material', 'cell-line', 'cell-type', 'chromosome', 'citation', 'clone', 'clone-lib', 'collected-by', 'collection-date', 'cultivar', 'culture-collectiondb-xref', 'dev-stage', 'ecotype', 'environmental-samplefocus', 'germlinehaplogroup',
                     'haplotype', 'host', 'identified-by', 'isolation-source', 'lab-host', 'lat-lon', 'macronuclearmap', 'mating-type', 'metagenome-source', 'note', 'organelle', 'PCR-primersplasmid', 'pop-variant', 'proviralrearrangedsegment', 'serotype', 'serovar', 'sex', 'sub-clone', 'submitter-seqid', 'sub-species', 'sub-strain', 'tissue-lib', 'tissue-type', 'transgenictype-material', 'variety']

    @ staticmethod
    def prepare(fields: List[str], record: Record) -> None:
        """
        Transforms the record to the simple form.

        Fuses country, region and locality fields,
        replaces species field with the organism field,
        remove uncertain bases from the beginning and the end of the sequence
        """
        # fuse country, region and locality
        if 'country' in fields:
            region = record.get('region')
            locality = record.get('locality')
            if region:
                # "country: region[, locality]"
                record['country'] = record['country'] + \
                    f": {region}" + (f", {locality}" if locality else "")
            else:
                # "country[: locality]"
                record['country'] = record['country'] + \
                    (f": {locality}" if locality else "")
        # replace species field with organism field
        if 'organism' not in fields:
            try:
                record['organism'] = record['species']
            except KeyError:
                pass
        # strip the sequence of uncertain bases
        record['sequence'] = record['sequence'].strip("nN?")

    @ staticmethod
    def parse_ident(line: str) -> Tuple[str, Dict[str, str]]:
        """Reads the attributes from the first line of Genbank FASTA record. Returns seqid and the dictionary of attributes"""
        # raise an error if the line is invalid
        if line[0] != '>':
            raise ValueError("Genbank fasta: invalid identifier line\n" + line)
        # split out the seqid
        [seqid, values_str] = line[1:].split(maxsplit=1)

        # collect the attributes
        values: Dict[str, str] = {}
        # the regex matches [field=value], field is stored in group 1, value in group 2
        field_value_regex = r'\[([^=\]]+)=([^\]]+)\]'
        for m in re.finditer(field_value_regex, values_str):
            field = m.group(1).strip()
            value = m.group(2).strip()
            if field == 'country':
                # special treatment for the country field
                # split into country, region, locality
                place = re.split(r'[,:] ', value)
                # put into the dictionary
                values.update(
                    zip(['country', 'region', 'locality'], place + ['', '']))
            else:
                values[field] = value

        # initialise all the missing fields
        for field in GenbankFastaFile.genbankfields:
            if not (field == "seqid" or field == "sequence"):
                values.setdefault(field, "")
        return seqid, values

    @ staticmethod
    def read(file: TextIO) -> Tuple[List[str], Callable[[], Iterator[Record]]]:
        """Genbank FASTA reader method"""
        def record_generator() -> Iterator[Record]:
            for chunk in split_file(file):
                ident = chunk[0]
                # parse the seqid and attributes
                seqid, values = GenbankFastaFile.parse_ident(ident)
                yield Record(seqid=seqid, sequence="".join(chunk[1:]), **values)
        return GenbankFastaFile.genbankfields, record_generator

    @staticmethod
    def write(file: TextIO, fields: List[str]) -> Generator:
        """Genbank FASTA writer method"""
        # discard the invalid fields
        fields = [
            field for field in fields if field.replace('_', '-') in GenbankFastaFile.genbankfields]
        # raise a warning if the required fields are not present
        if not (('organism' in fields or 'species' in fields) and ('specimen_voucher' in fields or 'specimen-voucher' in fields or 'isolate' in fields or 'clone' in fields or 'haplotype' in fields)):
            warnings.warn("Your file has been converted. However, apparently in your tab file either the organism, or a unique source identifier (specimen-voucher, isolate, clone) was missing, which may be required for submission to GenBank")

        # so far no sequence <200bp
        length_okay = True
        # so far no sequences with dashes
        no_dashes = True

        # creates seqid for Genbank FASTA
        name_assembler = NameAssemblerGB(fields)
        # makes the seqid unique within 25 characters
        unicifier = Unicifier(25)

        # receive the records and write them
        while True:
            try:
                record = yield
            except GeneratorExit:
                break

            # standardize the record
            GenbankFastaFile.prepare(fields, record)

            # raise the warning if the sequence <200 bp and turn off the checking for this
            if length_okay and len(record['sequence']) < 200:
                length_okay = False
                warnings.warn(
                    "Some of your sequences are <200 bp in length and therefore will probably not accepted by the GenBank nucleotide database")

            # raise the warning if the sequence has dashes and turn off the checking for this
            if no_dashes and '-' in record['sequence']:
                no_dashes = False
                warnings.warn("Some of your sequences contain dashes (gaps) which is only allowed if you submit them as alignment. If you do not wish to submit your sequences as alignment, please remove the dashes before conversion.")
            # print seqid and attributes
            print('>'+unicifier.unique(name_assembler.name(record)), *
                  [f"[{field.replace('_', '-')}={record[field].strip()}]" for field in fields if record[field] and not record[field].isspace() and not (field == "seqid" or field == "sequence")], file=file)
            # print the sequence
            print(record['sequence'], file=file)


class MoidFastaFile:
    """class for MoID FASTA format"""
    @staticmethod
    def write(file: TextIO, fields: List[str]) -> Generator:
        """MoID writer method"""

        # assemble the name from fields if 'specimen_voucher' or 'isolate' is missing
        # in this case, also put a limit on number of characters
        name_assembler = NameAssembler(fields, abbreviate_species=True)
        unicifier = Unicifier(10)

        # the writing loop
        while True:
            # receive a record
            try:
                record = yield
            except GeneratorExit:
                break

            if 'specimen_voucher' in fields or 'specimen-voucher' in fields or 'isolate' in fields:
                name = record['specimen_voucher'] if 'specimen_voucher' in fields else record[
                    'specimen-voucher'] if 'specimen-voucher' in fields else record['isolate']
                name = sanitize(name)
            else:
                name = unicifier.unique(name_assembler.name(record))
            species = record['species'] if 'species' in fields else record['organism'] if 'organism' in fields else ""
            species = sanitize(species)

            print(">", name, "|", species, sep="", file=file)
            print(record['sequence'], file=file)

    @staticmethod
    def read(file: TextIO) -> Tuple[List[str], Callable[[], Iterator[Record]]]:
        """MoID reader method"""

        # MoID always have the same fields
        fields = ['seqid', 'species', 'sequence']

        def record_generator() -> Iterator[Record]:
            for chunk in split_file(file):
                # 'seqid' is the part of the first line between the initial character and '|'
                # 'species' is the part of the first line after '|'
                # 'sequence' is the concatenation of all the other lines
                seqid, _, species = chunk[0][1:].partition('|')
                yield Record(seqid=seqid, species=species, sequence="".join(chunk[1:]))
        return fields, record_generator
