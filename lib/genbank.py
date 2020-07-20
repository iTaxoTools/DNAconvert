from lib.record import *
from typing import List, Optional, Tuple, Iterator, TextIO, Dict, Callable, Any
import re


def logical_lines(file: TextIO) -> Iterator[str]:
    while True:
        current = file.readline()
        if not current:
            break
        if not current.isspace():
            break
    current = current.strip()
    while True:
        line = file.readline()
        if not line:
            yield current
            break
        if line[0:12].isspace():
            current = current + ' ' + line.strip()
        else:
            yield current
            current = line.strip()


def find_line(lines: Iterator[str], field: str) -> Optional[str]:
    try:
        line = next(lines)
    except StopIteration:
        return None
    while not line.startswith(field):
        try:
            line = next(lines)
        except StopIteration:
            return None
    return line


def collect_metadata(lines: Iterator[str]) -> Optional[Dict[str, str]]:
    line = find_line(lines, "LOCUS")
    if not line:
        return None

    metadata: Dict[str, str] = {}
    while not line.startswith("FEATURES"):
        field, value = line.split(maxsplit=1)
        metadata.setdefault(field.casefold(), value)
        try:
            line = next(lines)
        except StopIteration:
            return None
    return metadata


def collect_features(lines: Iterator[str]) -> Dict[str, str]:
    line = find_line(lines, "source")
    if not line:
        raise ValueError("The Genbank file is missing a FEATURES field")
    features: Dict[str, str] = {}
    for match in re.finditer(r'/([^=]*)="([^"]*)"', line):
        features.setdefault(match.group(1).casefold(), match.group(2))
    while not line.startswith("ORIGIN"):
        if not 'product' in features.keys():
            m = re.search(r'/product="([^"]*)"', line)
            if m:
                features.setdefault('product', m.group(1))
        try:
            line = next(lines)
        except StopIteration:
            raise ValueError("The Genbank file is missing a sequence")
    return features


def read_sequence(lines: Iterator[str]) -> str:
    sequence = ""

    try:
        line = next(lines)
    except StopIteration:
        raise ValueError("The Genbank file has an incomplete sequence")
    while not line.startswith(r'//'):
        for word in line.split():
            if not word.isdigit():
                sequence = sequence + word
        try:
            line = next(lines)
        except StopIteration:
            raise ValueError("The Genbank file has an incomplete sequence")
    return sequence


gb_required_fields = ["accession", "authors", "title", "journal"]
gb_optional_fields = ['organism', 'mol_type', 'altitude', 'bio_material', 'cell_line', 'cell_type', 'chromosome', 'citation', 'clone', 'clone_lib', 'collected_by', 'collection_date', 'country', 'cultivar', 'culture_collection', 'db_xref', 'dev_stage', 'ecotype', 'environmental_samplefocus', 'germlinehaplogroup', 'haplotype', 'host', 'identified_by', 'isolate',
                      'isolation_source', 'lab_host', 'lat_lon', 'macronuclearmap', 'mating_type', 'metagenome_source', 'note', 'organelle', 'PCR_primersplasmid', 'pop_variant', 'product', 'proviralrearrangedsegment', 'serotype', 'serovar', 'sex', 'specimen_voucher', 'strain', 'sub_clone', 'submitter_seqid', 'sub_species', 'sub_strain', 'tissue_lib', 'tissue_type', 'transgenictype_material', 'variety']
gb_essential_fields = ["seqid", "organism", "accession", "specimen_voucher",
                       "strain", "isolate", "country", "sequence", "authors", "title", "journal"]
gb_fields = ["seqid", "organism", "accession", "specimen_voucher", "strain", "isolate", "country", "sequence", "authors", "title", "journal", 'mol_type', 'altitude', 'bio_material', 'cell_line', 'cell_type', 'chromosome', 'citation', 'clone', 'clone_lib', 'collected_by', 'collection_date', 'cultivar', 'culture_collection', 'db_xref', 'dev_stage', 'ecotype', 'environmental_samplefocus', 'germlinehaplogroup',
             'haplotype', 'host', 'identified_by', 'isolation_source', 'lab_host', 'lat_lon', 'macronuclearmap', 'mating_type', 'metagenome_source', 'note', 'organelle', 'PCR_primersplasmid', 'pop_variant', 'product', 'proviralrearrangedsegment', 'serotype', 'serovar', 'sex', 'sub_clone', 'submitter_seqid', 'sub_species', 'sub_strain', 'tissue_lib', 'tissue_type', 'transgenictype_material', 'variety']


class GenbankFile:

    @ staticmethod
    def read(file: TextIO) -> Tuple[List[str], Callable[[], Iterator[Record]]]:

        def record_generator() -> Iterator[Record]:
            lines = logical_lines(file)
            while True:
                metadata = collect_metadata(lines)
                if not metadata:
                    break
                else:
                    features = collect_features(lines)
                    sequence = read_sequence(lines)
                    record = Record(
                        seqid=metadata["definition"], sequence=sequence)
                    for field in gb_required_fields:
                        record[field] = metadata[field]
                    for field in gb_optional_fields:
                        try:
                            record[field] = features[field]
                        except KeyError:
                            record[field] = ""
                    yield record
        return gb_fields, record_generator

    @ staticmethod
    def write(_: Any) -> None:
        raise ValueError(
            "Conversion to the Genbank flat file format is not supported")
