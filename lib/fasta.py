import re
import warnings
from lib.record import *
from lib.utils import *
from typing import TextIO, Iterator, List, Generator, Tuple, Set


# Yields a list of lines that comprise one FASTA record
def split_file(file: TextIO) -> Iterator[List[str]]:

    # find the beginning of the first record
    line = " "
    while line[0] != '>':
        line = file.readline()

    # chunk contains the already read lines of the current record
    chunk = []
    chunk.append(line.rstrip())

    for line in file:
        # skip the blank lines
        if line == "" or line.isspace():
            continue

        # yield the chunk if the new record has begun
        if line[0] == '>':
            yield chunk
            chunk = []

        chunk.append(line.rstrip())

    # yield the last record
    yield chunk


class Fastafile:
    @staticmethod
    def write(file: TextIO, fields: List[str]) -> Generator:
        name_assembler = NameAssembler(fields)

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
        # FASTA always have the same fields
        fields = ['seqid', 'sequence']

        def record_generator() -> Iterator[Record]:
            skipped = 0
            for chunk in split_file(file):
                # skip if there is no sequence
                if len(chunk) <= 1:
                    skipped += 1
                    continue
                # 'seqid' is the first line without the initial character
                # 'sequence' is the concatenation of all the other lines
                yield Record(seqid=chunk[0][1:], sequence="".join(chunk[1:]))
            if skipped > 0:
                warnings.warn(
                    f"{skipped} records did not contain a sequence and are therefore not included in the converted file")
        return fields, record_generator


class UnicifierSN(Unicifier):
    def __init__(self, length_limit: Optional[int] = None):
        super().__init__(length_limit)
        self._sep = ""


class SpeciesNamer:
    """makes correspondence between long species name in the record and unique short names
    """

    def __init__(self, species: Set[str], species_field: Optional[str]):
        if not species_field:
            self._count = 0
            self.name = self._count_name
            return
        # make list of pair of species and first 4 letters of the second part of the name

        def short_name(name: str) -> str:
            _, second_part = re.split(r'[ _]', name, maxsplit=1)
            try:
                return second_part[0:4]
            except IndexError:
                raise ValueError(f"Malformed species name {name}")
        unicifier = UnicifierSN()
        self._species_field = species_field
        self._species = {long_name: unicifier.unique(
            short_name(long_name)) for long_name in species}
        self.name = self._dict_name

    def _count_name(self, record: Record) -> str:
        self._count += 1
        return str(self._count - 1)

    def _dict_name(self, record: Record) -> str:
        return self._species[record[self._species_field]]


class HapviewFastafile:
    @ staticmethod
    def read(file: TextIO) -> Tuple[List[str], Callable[[], Iterator[Record]]]:
        # FASTA always have the same fields
        fields = ['seqid', 'sequence']

        def record_generator() -> Iterator[Record]:
            skipped = 0
            for chunk in split_file(file):
                # skip if there is no sequence
                if len(chunk) <= 1:
                    skipped += 1
                    continue
                # 'seqid' is the first line without the initial character
                # 'sequence' is the concatenation of all the other lines
                yield Record(seqid=chunk[0][1:], sequence="".join(chunk[1:]))
            if skipped > 0:
                warnings.warn(
                    f"{skipped} records did not contain a sequence and are therefore not included in the converted file")
        return fields, record_generator

    @ staticmethod
    def write(file: TextIO, fields: List[str]) -> Generator:
        species_field = get_species_field(fields)
        if species_field:
            def species_reducer(acc: Set[str], record: Record) -> Set[str]:
                assert species_field is not None
                acc.add(record[species_field])
                return acc
            aggregator = PhylipAggregator((set(), species_reducer))
        else:
            aggregator = PhylipAggregator()
        records = []

        while True:
            try:
                record = yield
            except GeneratorExit:
                break
            aggregator.send(record)
            records.append(record)

        [max_length, min_length, species] = aggregator.results()
        species_namer = SpeciesNamer(species, species_field)

        aligner = dna_aligner(max_length, min_length)
        name_assembler = NameAssembler(fields)
        unicifier = Unicifier(100)

        for record in records:
            print('>', unicifier.unique(name_assembler.name(record)),
                  '.', species_namer.name(record), sep="", file=file)
            print(aligner(record['sequence']), file=file)


class FastQFile:

    @ staticmethod
    def to_fasta(infile: TextIO, outfile: TextIO) -> None:
        for line in infile:
            if line[0] == '@':
                print('>', line[1:], sep="", end="", file=outfile)
                line = infile.readline()
                print(line, file=outfile, end="")

    @ staticmethod
    def read(file: TextIO) -> Tuple[List[str], Callable[[], Iterator[Record]]]:
        fields = ['seqid', 'sequence',
                  'quality_score_identifier', 'quality_score']

        def record_generator() -> Iterator[Record]:
            for line in file:
                if line[0] == '@':
                    seqid = line[1:].rstrip()
                    sequence = file.readline().rstrip()
                    quality_score_identifier = file.readline().rstrip()
                    quality_score = file.readline().rstrip()
                    yield Record(seqid=seqid, sequence=sequence, quality_score_identifier=quality_score_identifier, quality_score=quality_score)
        return fields, record_generator

    @ staticmethod
    def write(file: TextIO, fields: List[str]) -> Generator:
        if not {'seqid', 'sequence', 'quality_score_identifier', 'quality_score'} <= set(fields):
            raise ValueError(
                'FastQ requires the fields seqid, sequence, quality_score_identifier and quality_score')
        while True:
            try:
                record = yield
            except GeneratorExit:
                break
            print('@', record['seqid'], sep="", file=file)
            for field in ['sequence', 'quality_score_identifier', 'quality_score']:
                print(record[field], file=file)


class NameAssemblerGB(NameAssembler):
    def __init__(self, fields: List[str]):
        if 'seqid' in fields:
            self.name = self._simple_name
        else:
            self._fields = [field for field in [
                'organism', 'specimen_voucher'] if field in fields]
            self.name = self._complex_name


class GenbankFastaFile:
    genbankfields = ['organism', 'mol_type', 'altitude', 'bio_material', 'cell_line', 'cell_type', 'chromosome', 'citation', 'clone', 'clone_lib', 'collected_by', 'collection_date', 'country', 'cultivar', 'culture_collectiondb_xref', 'dev_stage', 'ecotype', 'environmental_samplefocus', 'germlinehaplogroup', 'haplotype', 'host', 'identified_by', 'isolate', 'isolation_source',
                     'lab_host', 'lat_lon', 'macronuclearmap', 'mating_type', 'metagenome_source', 'note', 'organelle', 'PCR_primersplasmid', 'pop_variant', 'proviralrearrangedsegment', 'serotype', 'serovar', 'sex', 'specimen_voucher', 'strain', 'sub_clone', 'submitter_seqid', 'sub_species', 'sub_strain', 'tissue_lib', 'tissue_type', 'transgenictype_material', 'variety']

    @ staticmethod
    def prepare(fields: List[str], record: Record) -> None:
        if 'country' in fields:
            region = record.get('region')
            locality = record.get('locality')
            if region:
                record['country'] = record['country'] + \
                    f": {region}" + (f", {locality}" if locality else "")
            else:
                record['country'] = record['country'] + \
                    (f": {locality}" if locality else "")
        if 'organism' not in fields:
            try:
                record['organism'] = record['species']
            except KeyError:
                pass
        record['sequence'] = record['sequence'].strip("nN?")

    @ staticmethod
    def parse_ident(line: str) -> Tuple[str, Dict[str, str]]:
        if line[0] != '>':
            raise ValueError("Genbank fasta: invalid identifier line\n" + line)
        [seqid, values_str] = line[1:].split(maxsplit=1)
        values: Dict[str, str] = {}
        for m in re.finditer(r'\[([^=\]]+)=([^\]]+)\]', values_str):
            field = m.group(1).strip()
            value = m.group(2).strip()
            if field == 'country':
                place = re.split(r'[,:] ', value)
                values.update(
                    zip(['country', 'region', 'locality'], place + ['', '']))
            else:
                values[field] = value
        return seqid, values

    @ staticmethod
    def read(file: TextIO) -> Tuple[List[str], Callable[[], Iterator[Record]]]:
        while True:
            line = file.readline()
            if line == "" or line.isspace():
                continue
            _, values = GenbankFastaFile.parse_ident(line)
            fields = ['seqid'] + list(values.keys()) + ['sequence']
            break
        file.seek(0, 0)

        def record_generator() -> Iterator[Record]:
            skipped = 0
            for chunk in split_file(file):
                # skip if there is no sequence
                if len(chunk) <= 1:
                    skipped += 1
                    continue
                ident = chunk[0]
                seqid, values = GenbankFastaFile.parse_ident(ident)
                yield Record(seqid=seqid, sequence="".join(chunk[1:]), **values)
            if skipped > 0:
                warnings.warn(
                    f"{skipped} records did not contain a sequence and are therefore not included in the converted file")
        return fields, record_generator

    @staticmethod
    def write(file: TextIO, fields: List[str]) -> Generator:
        seqid_exists = [x for x in ['seqid'] if 'seqid' in fields]
        fields = [
            field for field in fields if field in GenbankFastaFile.genbankfields]
        if not (('organism' in fields or 'species' in fields) and ('specimen_voucher' in fields or 'isolate' in fields or 'clone' in fields or 'haplotype' in fields)):
            warnings.warn("Your file has been converted. However, apparently in your tab file either the organism, or a unique source identifier (specimen-voucher, isolate, clone) was missing, which may be required for submission to GenBank")
        length_okay = True
        no_dashes = True
        name_assembler = NameAssemblerGB(seqid_exists + fields)
        unicifier = Unicifier(25)
        while True:
            try:
                record = yield
            except GeneratorExit:
                break
            GenbankFastaFile.prepare(fields, record)
            if length_okay and len(record['sequence']) < 200:
                length_okay = False
                warnings.warn(
                    "Some of your sequences are <200 bp in length and therefore will probably not accepted by the GenBank nucleotide database")
            if no_dashes and '-' in record['sequence']:
                no_dashes = False
                warnings.warn("Some of your sequences contain dashes (gaps) which is only allowed if you submit them as alignment. If you do not wish to submit your sequences as alignment, please remove the dashes before conversion.")
            print('>'+unicifier.unique(name_assembler.name(record)), *
                  [f"[{field}={record[field].strip()}]" for field in fields], file=file)
            print(record['sequence'], file=file)
