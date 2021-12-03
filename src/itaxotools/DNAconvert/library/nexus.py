from typing import TextIO, Optional, Tuple, Callable, Iterator, List, Set, ClassVar, Generator, DefaultDict
from .record import *
from .utils import *
from collections import defaultdict
import re
import nexus as python_nexus


class Tokenizer:
    """
    Token iterator for the NEXUS format

    Emits the stream of words and punctuation
    """
    punctuation: ClassVar[Set[str]] = set('=;')

    def __init__(self, file: TextIO):
        """
        Iterate over the token in 'file'
        """
        # check that the file is in NEXUS format
        magic_word = file.read(6)
        if magic_word != '#NEXUS':
            raise ValueError("The input file is not a nexus file")
        # contains the underlying file
        self.file = file
        # the currently read token
        self.token: List[str] = []
        # the currently read line
        self.line = ""
        # the reading position in the line
        self.line_pos = 0

    def peek_char(self) -> Optional[str]:
        """
        Returns the next char, without advancing the position.
        Returns None, if EOF is reached
        """
        try:
            c = self.line[self.line_pos]
            return c
        except IndexError:
            # line_pos is self.line.len()
            # it's equivalent to 0 in the next line
            self.line = self.file.readline()
            if self.line == "":
                # EOF is reached
                return None
            self.line_pos = 0
            c = self.line[0]
            return c

    def get_char(self) -> Optional[str]:
        """
        Emits a char, advancing the reading
        Returns None, if EOF is reached
        """
        c = self.peek_char()
        self.line_pos += 1
        return c

    def replace_token(self, token: List[str]) -> str:
        """
        Remember the next token and return the str representation of the current one
        """
        self.token, token = token, self.token
        return "".join(token)

    def skip_comment(self) -> None:
        """
        Advance the iterator past the end of a comment
        """
        while True:
            c = self.get_char()
            if c is None:
                # EOF is reached, should not happen in a well-formed file
                raise ValueError("Nexus: EOF inside a comment")
            elif c == '[':
                # comment inside a comment
                self.skip_comment
            elif c == ']':
                # end of the comment
                break

    def read_quoted(self) -> List[str]:
        """
        Reads a quoted string as one token
        """
        s = []
        while True:
            c = self.get_char()
            if c is None:
                # EOF is reached, should not happen in a well-formed file
                raise ValueError("Nexus: EOF inside a quoted value")
            elif c == '\'':
                # possible end of the quoted value
                if self.peek_char == '\'':
                    # '' is ', and not the end
                    s += ['\'']
                else:
                    # the end of the line
                    return s
            else:
                # update the line
                s += [c]

    def __iter__(self) -> 'Tokenizer':
        """ Tokenizer is an Iterator"""
        return self

    def __next__(self) -> str:
        if self.token:
            # the is a previously saved token
            return self.replace_token([])
        while True:
            c = self.get_char()
            if c is None:
                # EOF => return the last token
                if self.token:
                    "".join(self.token)
                else:
                    raise StopIteration
            elif c in Tokenizer.punctuation:
                # punctuation is a token by itself => save it into the token
                token = self.replace_token([c])
                if token:
                    return token
            elif c == '[':
                # a comment => skip it
                self.skip_comment()
            elif c == '\'':
                # a quoted value => read it and save into the token
                token = self.replace_token(self.read_quoted())
                if token:
                    return token
            elif c.isspace():
                # whitespace => return the token, if it's the first whitespace
                if self.token:
                    token = self.replace_token([])
                    return token
            else:
                # otherwise => update the token
                self.token.append(c)

    @staticmethod
    def print_tokens(path: str) -> None:
        """
        Testing method to check that the tokens are read correctly
        """
        with open(path) as file:
            for token in Tokenizer(file):
                print(repr(token))


class NexusCommands:
    """
    Iterator that emits NEXUS command as a tuple of the command name and the arguments' iterator
    """

    def __init__(self, file: TextIO):
        """
        Iterate over the commands in 'file'
        """
        self.tokenizer = Tokenizer(file)

    def __iter__(self) -> 'NexusCommands':
        """
        NexusCommands is an Iterator
        """
        return self

    def __next__(self) -> Tuple[str, Iterator[str]]:
        # next token is the command name
        command = next(self.tokenizer).casefold()

        def arguments() -> Iterator[str]:
            # emit tokens until the ';'
            while True:
                try:
                    arg = next(self.tokenizer)
                except StopIteration:
                    # EOF is reached; should not happen in a well-formed file
                    raise ValueError("Nexus: EOF inside a command")
                if arg == ';':
                    break
                else:
                    yield arg
        return command, arguments()

    @staticmethod
    def print_commands(path: str) -> None:
        """
        Testing method to check that commands are read correctly
        """
        with open(path) as file:
            for command, args in NexusCommands(file):
                print(repr(command), [repr(arg) for arg in args])


class NexusReader:
    """
    A virtual machine that executes NEXUS command and emits the sequences in the file
    """

    def __init__(self) -> None:
        self.block_reset()

    def block_reset(self) -> None:
        """Resets the machine to the initial state at the end of each block"""
        # indicates if the current block's matrix contains useable information
        self.read_matrix = False
        # indicates if the current block's matrix is interleaved
        self.interleave = False
        # holds the length of sequence for the current block
        self.nchar = None

    def execute(self, command: str, args: Iterator[str]) -> Optional[Iterator[Tuple[str, str]]]:
        """
        Executes a NEXUS command and updates the internal state

        Returns an iterator over sequences in a matrix, if the command is 'matrix'
        """
        # for each command execute the corresponding method
        if command == 'format':
            self.configure_format(args)
            return None
        elif command == 'dimensions':
            self.read_dimensions(args)
        elif command == 'end' or command == 'endblock':
            self.block_reset()
            return None
        elif command == 'matrix':
            return self.sequences(args)
        else:
            return None

    def configure_format(self, args: Iterator[str]) -> None:
        """
        Configure the internal state in responce to the 'format' command
        """
        # If the 'datatype' is DNA, RNA, Nucleotide or Protein, prepare for reading
        for arg in args:
            if arg.casefold() == 'datatype':
                if next(args) != '=':
                    continue
                if re.search(r'DNA|RNA|Nucleotide|Protein', next(args), flags=re.IGNORECASE):
                    self.read_matrix = True
            elif arg.casefold() == 'interleave':
                self.interleave = True

    def read_dimensions(self, args: Iterator[str]) -> None:
        for arg in args:
            if arg.casefold() == 'nchar':
                if next(args) != '=':
                    continue
                try:
                    self.nchar = int(next(args))
                except ValueError:
                    pass

    def sequences(self, args: Iterator[str]) -> Optional[Iterator[Tuple[str, str]]]:
        """
        Emit the sequence in the current matrix, if the datatype is correct
        """
        if not self.read_matrix:
            return None
        if self.interleave:
            return self.sequences_interleaved(args)
        else:
            return self.sequences_noninterleaved(args)

    @staticmethod
    def sequences_interleaved(args: Iterator[str]) -> Iterator[Tuple[str, str]]:
        matrix: DefaultDict[str, str] = defaultdict(str)
        for arg in args:
            try:
                matrix[arg] += next(args)
            except StopIteration:
                # expects the value to come in pairs (name, sequence)
                raise ValueError(
                    f"In the Nexus file: {arg} has no corresponding sequence")
        return iter(matrix.items())

    def sequences_noninterleaved(self, args: Iterator[str]) -> Iterator[Tuple[str, str]]:
        if not self.nchar:
            raise ValueError(
                "Cannot parse non-interleaved NEXUS file without an 'nchar' value")
        for arg in args:
            seqid = arg
            sequence = ""
            while (len(sequence) < self.nchar):
                sequence += next(args)
            yield (seqid, sequence)


def seqid_max_reducer(acc: int, record: Record) -> int:
    """
    A reducer to determine the longest sequence name
    """
    l = len(record['seqid'])
    return max(acc, l)


class NexusFile:
    """class for the NEXUS file"""

    # the text which is always in the beginning of the NEXUS file
    nexus_preamble: ClassVar[str] = """\
#NEXUS

begin data;
"""

    nexus_format_line = "format datatype=DNA missing=N missing=? Gap=- Interleave=yes;"

    @staticmethod
    def read(file: TextIO) -> Tuple[List[str], Callable[[], Iterator[Record]]]:
        """the NEXUS reader method"""
        # NEXUS always have the same fields
        fields = ['seqid', 'sequence']

        def record_generator() -> Iterator[Record]:
            # create the virtual machine
            nexus_reader = NexusReader()
            # execute all the commands in the file
            for command, args in NexusCommands(file):
                records = nexus_reader.execute(command, args)
                if records is not None:
                    # capture the records
                    for seqid, sequence in records:
                        yield Record(seqid=seqid, sequence=sequence)
        return fields, record_generator

    @staticmethod
    def write(file: TextIO, fields: List[str]) -> Generator:
        """the NEXUS writer method"""
        # aggregate minimum sequence length, maximum sequence length and the maximum seqid length
        aggregator = PhylipAggregator((0, seqid_max_reducer))
        # assembles the seqid
        name_assembler = NameAssembler(fields)
        # makes the seqid unique within 100 characters
        unicifier = Unicifier(100)

        # collect the record and aggregate the information
        records = []
        while True:
            try:
                record = yield
            except GeneratorExit:
                break
            # the seqid needs to be generated before using the aggregator
            record['seqid'] = unicifier.unique(name_assembler.name(record))
            aggregator.send(record)
            records.append(record)

        # extract the aggregated information
        [max_length, min_length, seqid_max_length] = aggregator.results()

        # pads the sequences with '-'
        aligner = dna_aligner(max_length, min_length)

        # write the beginning
        print(NexusFile.nexus_preamble, file=file)

        # print the dimensions command
        print(
            f"dimensions Nchar={max_length} Ntax={len(records)};", file=file)

        # print the format command
        print(NexusFile.nexus_format_line, file=file)

        file.write('\n')

        # print the matrix command
        print("matrix", file=file)
        for record in records:
            print(record['seqid'].ljust(seqid_max_length), aligner(
                record['sequence']), file=file)

        # finish the block
        print(";\n", file=file)
        print("end;", file=file)


class NexusFileSimple(NexusFile):

    @staticmethod
    def read(file: TextIO) -> Tuple[List[str], Callable[[], Iterator[Record]]]:
        """NEXUS reader method using parser from python-nexus"""
        # NEXUS always have the same fields
        raise ValueError(
            "python-nexus parser is temporarily disabled. Use 'internal' parser instead")
        fields = ['seqid', 'sequence']

        def record_generator() -> Iterator[Record]:
            nexus_file = python_nexus.NexusReader.from_file(file.name)
            if 'data' in nexus_file.blocks:
                for seqid, sequence in nexus_file.data.matrix.items():
                    yield Record(seqid=seqid, sequence="".join(sequence))

        return fields, record_generator
