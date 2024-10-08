from .record import *
from typing import List, Optional, Tuple, Iterator, TextIO, Dict, Callable, Any
import re
import warnings


def logical_lines(file: TextIO) -> Iterator[str]:
    """
    Iterator over the logical lines of Genbank flatfile.

    Logical line starts with indentation less or equal 12 whitespace characters.
    Newlines are replaced with ' '
    """
    # find the first non-blank line
    while True:
        current = file.readline()
        if not current:
            break
        if not current.isspace():
            break
    # the 'current' variable contains the initial part of the logical line
    current = current.strip()
    while True:
        # read a line
        line = file.readline()
        if not line:
            yield current
            break
        # check if it's a continuation
        if line[0:12].isspace():
            # if yes, add to the current logical line
            current = current + " " + line.strip()
        else:
            # else, yield the current logical line and begin a new one
            yield current
            current = line.strip()


def find_line(lines: Iterator[str], field: str) -> Optional[str]:
    """
    Iterates over 'lines' until the line beginning with 'field' is found.
    Returns this line if found, None if the end of iteration is reached.

    After the return, the next line is the first line of the iterator.
    """
    # iterate until the line is found
    while True:
        try:
            line = next(lines)
        except StopIteration:
            return None
        if line.startswith(field):
            break
    # return the line
    return line


def collect_metadata(lines: Iterator[str]) -> Optional[Dict[str, str]]:
    """
    Collects the major attributes of a Genbank flatfile record (until "FEATURES").
    Returns the dictionary of attributes, unless the EOF was reached before "FEATURES".

    Precondition: beginning of 'lines' is between record
    Postcondition: beginning of 'lines' is immediately after the "FEATURES" line
    """
    # find the start of a record
    line = find_line(lines, "LOCUS")
    if not line:
        return None

    # collect the attributes
    metadata: Dict[str, str] = {}
    while not line.startswith("FEATURES"):
        # field name is the first word, value is the rest of the line
        field, value = line.split(maxsplit=1)
        # save only the first value of the field
        metadata.setdefault(field.casefold(), value)
        try:
            line = next(lines)
        except StopIteration:
            return None
    return metadata


def collect_features(lines: Iterator[str]) -> Optional[Dict[str, str]]:
    """
    Returns the dictionary of "source" features with the first "/product" feature.
    Returns `None` if EOF is reached

    Precondition: beginning of 'lines' is immediately after the "FEATURES" line
    Postcondition: beginning of 'lines' is immediately after the "ORIGIN" line
    """
    # iterate until the "source" line
    line = find_line(lines, "source")
    if not line:
        warnings.warn(
            "A record in the Genbank file is missing a FEATURES field. Further parsing is impossible."
        )
        return None
    # collect the features from the logical line
    features: Dict[str, str] = {}
    for match in re.finditer(r'/([^=]*)="([^"]*)"', line):
        features.setdefault(match.group(1).casefold(), match.group(2))
    # save the first "/product" feature and iterate until the "ORIGIN" line
    while not line.startswith("ORIGIN"):
        # only search for "/product" if it's not already found
        if not "product" in features.keys():
            m = re.search(r'/product="([^"]*)"', line)
            if m:
                features.setdefault("product", m.group(1))
        try:
            line = next(lines)
        except StopIteration:
            return None
    return features


def read_sequence(lines: Iterator[str]) -> Optional[str]:
    """
    Returns the sequence from the current record
    sequence = ""
    Returns `None` if EOF is reached

    Precondition: beginning of 'lines' is immediately after the "ORIGIN" line
    Postcondition: beginning of 'lines' is immediately after the record
    """
    sequence = ""
    while True:
        # read a line
        try:
            line = next(lines)
        except StopIteration:
            return None
        # collect all the sequence parts, ignore the numbers
        for word in line.split():
            if not word.isdigit():
                if word.endswith(r"//"):
                    sequence = sequence + word[:-2]
                    return sequence
                sequence = sequence + word
        if line.startswith(r"//"):
            return sequence


# field that need to be present in every record
gb_required_fields = ["accession", "authors", "title", "journal"]
# optional fields
gb_optional_fields = [
    "organism",
    "mol_type",
    "altitude",
    "bio_material",
    "cell_line",
    "cell_type",
    "chromosome",
    "citation",
    "clone",
    "clone_lib",
    "collected_by",
    "collection_date",
    "country",
    "geo_loc_name",
    "cultivar",
    "culture_collection",
    "db_xref",
    "dev_stage",
    "ecotype",
    "environmental_samplefocus",
    "germlinehaplogroup",
    "haplotype",
    "host",
    "identified_by",
    "isolate",
    "isolation_source",
    "lab_host",
    "lat_lon",
    "macronuclearmap",
    "mating_type",
    "metagenome_source",
    "note",
    "organelle",
    "PCR_primersplasmid",
    "pop_variant",
    "product",
    "proviralrearrangedsegment",
    "serotype",
    "serovar",
    "sex",
    "specimen_voucher",
    "type_material",
    "strain",
    "sub_clone",
    "submitter_seqid",
    "sub_species",
    "sub_strain",
    "tissue_lib",
    "tissue_type",
    "transgenictype_material",
    "variety",
    "locus",
]
# fields in the required order
gb_fields = [
    "seqid",
    "organism",
    "accession",
    "specimen_voucher",
    "type_material",
    "strain",
    "isolate",
    "country",
    "geo_loc_name",
    "sequence",
    "authors",
    "title",
    "journal",
    "locus",
    "mol_type",
    "altitude",
    "bio_material",
    "cell_line",
    "cell_type",
    "chromosome",
    "citation",
    "clone",
    "clone_lib",
    "collected_by",
    "collection_date",
    "cultivar",
    "culture_collection",
    "db_xref",
    "dev_stage",
    "ecotype",
    "environmental_samplefocus",
    "germlinehaplogroup",
    "haplotype",
    "host",
    "identified_by",
    "isolation_source",
    "lab_host",
    "lat_lon",
    "macronuclearmap",
    "mating_type",
    "metagenome_source",
    "note",
    "organelle",
    "PCR_primersplasmid",
    "pop_variant",
    "product",
    "proviralrearrangedsegment",
    "serotype",
    "serovar",
    "sex",
    "sub_clone",
    "submitter_seqid",
    "sub_species",
    "sub_strain",
    "tissue_lib",
    "tissue_type",
    "transgenictype_material",
    "variety",
]


class GenbankFile:
    """class for the Genbank flatfile"""

    @staticmethod
    def _identify_record(
        metadata: Dict[str, str], features: Dict[str, str], sequence: str
    ) -> Tuple[str, str]:
        for field in gb_required_fields:
            if field in metadata:
                return field, metadata[field]
        for field in gb_optional_fields:
            if field in features:
                return field, features[field]
        return "sequence", sequence[:20]

    @staticmethod
    def read(file: TextIO) -> Tuple[List[str], Callable[[], Iterator[Record]]]:
        """Genbank flatfile reader method"""

        def record_generator() -> Iterator[Record]:
            # prepare the iterator over the logical lines
            lines = logical_lines(file)
            while True:
                # collect the major attributes of a record
                metadata = collect_metadata(lines)
                if metadata is None:
                    # EOF
                    break
                # read the features and the sequence
                features = collect_features(lines)
                if features is None:
                    # EOF
                    break
                sequence = read_sequence(lines)
                if sequence is None:
                    # EOF
                    break
                # initialize the record
                try:
                    seqid = metadata["definition"]
                except KeyError:
                    key, val = GenbankFile._identify_record(
                        metadata, features, sequence
                    )
                    warnings.warn(
                        f'The record with {key} "{val}" is missing the definition.'
                        "A seqid cannot be obtained. "
                        "Skipping"
                    )
                    continue
                record = Record(seqid=seqid, sequence=sequence)
                # write the fields of the record
                for field in gb_required_fields:
                    try:
                        record[field] = metadata[field]
                    except KeyError:
                        record[field] = ""
                for field in gb_optional_fields:
                    try:
                        record[field] = features[field]
                    except KeyError:
                        record[field] = ""
                yield record

        return gb_fields, record_generator

    @staticmethod
    def write(_: Any) -> None:
        """Genbank flatfile cannot be written"""
        raise ValueError("Conversion to the Genbank flat file format is not supported")
