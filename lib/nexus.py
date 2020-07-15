from typing import TextIO, Optional, Tuple, Callable, Iterator, List, Set, ClassVar, Generator
from lib.record import *
from lib.utils import *
import re


class Tokenizer:
    punctiation: ClassVar[Set[str]] = set('=;')

    def __init__(self, file: TextIO):
        magic_word = file.read(6)
        if magic_word != '#NEXUS':
            raise ValueError("The input file is not a nexus file")
        self.file = file
        self.token: List[str] = []
        self.line = ""
        self.line_pos = 0

    def peek_char(self) -> Optional[str]:
        try:
            c = self.line[self.line_pos]
            return c
        except IndexError:
            self.line = self.file.readline()
            if self.line == "":
                return None
            self.line_pos = 0
            c = self.line[0]
            return c

    def get_char(self) -> Optional[str]:
        c = self.peek_char()
        self.line_pos += 1
        return c

    def replace_token(self, token: List[str]) -> str:
        self.token, token = token, self.token
        return "".join(token)

    def skip_comment(self) -> None:
        while True:
            c = self.get_char()
            if c is None:
                raise ValueError("Nexus: EOF inside a comment")
            elif c == '[':
                self.skip_comment
            elif c == ']':
                break

    def read_quoted(self) -> List[str]:
        # s is a list representing a mutable string
        s = []
        while True:
            c = self.get_char()
            if c is None:
                raise ValueError("Nexus: EOF inside a quoted value")
            elif c == '\'':
                if self.peek_char == '\'':
                    s += ['\'']
                else:
                    return s
            else:
                s += [c]

    def __iter__(self) -> 'Tokenizer':
        return self

    def __next__(self) -> str:
        if self.token:
            return self.replace_token([])
        while True:
            c = self.get_char()
            if c is None:
                if self.token:
                    "".join(self.token)
                else:
                    raise StopIteration
            elif c in Tokenizer.punctiation:
                token = self.replace_token([c])
                if token:
                    return token
            elif c == '[':
                self.skip_comment()
            elif c == '\'':
                token = self.replace_token(self.read_quoted())
                if token:
                    return token
            elif c.isspace():
                if self.token:
                    token = self.replace_token([])
                    return token
            else:
                self.token.append(c)

    @staticmethod
    def print_tokens(path: str) -> None:
        with open(path) as file:
            for token in Tokenizer(file):
                print(repr(token))


class NexusCommands:

    def __init__(self, file: TextIO):
        self.tokenizer = Tokenizer(file)

    def __iter__(self) -> 'NexusCommands':
        return self

    def __next__(self) -> Tuple[str, Iterator[str]]:
        command = next(self.tokenizer).casefold()

        def arguments() -> Iterator[str]:
            while True:
                try:
                    arg = next(self.tokenizer)
                except StopIteration:
                    raise ValueError("Nexus: EOF inside a command")
                if arg == ';':
                    break
                else:
                    yield arg
        return command, arguments()

    @staticmethod
    def print_commands(path: str) -> None:
        with open(path) as file:
            for command, args in NexusCommands(file):
                print(repr(command), [repr(arg) for arg in args])


class NexusReader:

    def __init__(self):
        self.read_matrix = False

    def block_reset(self) -> None:
        self.read_matrix = False

    def execute(self, command: str, args: Iterator[str]) -> Optional[Iterator[Tuple[str, str]]]:
        if command == 'format':
            self.configure_format(args)
            return None
        elif command == 'end' or command == 'endblock':
            self.block_reset()
            return None
        elif command == 'matrix':
            return self.sequences(args)
        else:
            return None

    def configure_format(self, args: Iterator[str]) -> None:
        for arg in args:
            if arg.casefold() == 'datatype':
                if next(args) != '=':
                    continue
                if re.search(r'DNA|RNA|Nucleotide|Protein', next(args)):
                    self.read_matrix = True

    def sequences(self, args: Iterator[str]) -> Optional[Iterator[Tuple[str, str]]]:
        if not self.read_matrix:
            return None
        for arg in args:
            try:
                yield (arg, next(args))
            except StopIteration:
                raise ValueError(
                    f"In the Nexus file: {arg} has no corresponding sequence")


def seqid_max_reducer(acc: int, record: Record) -> int:
    l = len(record['seqid'])
    return max(acc, l)


class NexusFile:

    nexus_preamble: ClassVar[str] = """\
#NEXUS

begin data;

format datatype=DNA missing=N missing=? Gap=- Interleave=yes;
"""

    @staticmethod
    def read(file: TextIO) -> Tuple[List[str], Callable[[], Iterator[Record]]]:
        fields = ['seqid', 'sequence']

        def record_generator():
            nexus_reader = NexusReader()
            for command, args in NexusCommands(file):
                records = nexus_reader.execute(command, args)
                if records is not None:
                    for seqid, sequence in records:
                        yield Record(seqid=seqid, sequence=sequence)
        return fields, record_generator

    @staticmethod
    def write(file: TextIO, fields: List[str]) -> Generator:
        aggregator = PhylipAggregator((0, seqid_max_reducer))
        records = []
        name_assembler = NameAssembler(fields)
        unicifier = Unicifier(100)

        while True:
            try:
                record = yield
            except GeneratorExit:
                break
            record['seqid'] = unicifier.unique(name_assembler.name(record))
            aggregator.send(record)
            records.append(record)

        [max_length, min_length, seqid_max_length] = aggregator.results()

        aligner = dna_aligner(max_length, min_length)

        print(NexusFile.nexus_preamble, file=file)

        print(
            f"dimensions Nchar={max_length} Ntax={len(records)};\n", file=file)

        print("matrix", file=file)

        for record in records:
            print(record['seqid'].ljust(seqid_max_length), aligner(
                record['sequence']), file=file)

        print(";\n", file=file)
        print("end;", file=file)
