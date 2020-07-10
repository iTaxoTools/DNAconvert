from typing import TextIO, Optional

class Tokenizer:
    punctiation = set('=;')

    def __init__(self: Tokenizer, file: TextIO):
        magic_word = file.read(6)
        if magic_word != '#Nexus': raise ValueError("The input file is not a nexus file")
        self.file = file
        self.token = ""
        self.line = ""
        self.line_pos = 0

    def peek_char(self: Tokenizer) -> Optional(str):
        try:
            c = self.line[self.line_pos]
        except IndexError:
            self.line = self.file.readline
            if self.line == "": return None
            self.line_pos = 0
            c = self.line[0]
        finally:
            return c

    def get_char(self: Tokenizer) -> Optional(str):
        c = self.peek_char()
        self.line_pos += 1
        return c

    def replace_token(self: Tokenizer, token: str) -> str:
        self.token, token = token, self.token
        return token

    def skip_comment(self: Tokenizer):
        while True:
            c = self.get_char()
            if c == None:
                raise ValueError("Nexus: EOF inside a comment")
            elif c == '[':
                self.skip_comment
            elif c == ']':
                break

    def read_quoted(self: Tokenizer):
        s = ""
        while True:
            c = self.get_char()
            if c == None:
                raise ValueError("Nexus: EOF inside a quoted value")
            elif c == '\'':
                if self.peek_char == '\'':
                    s += '\''
                else:
                    return s
            else:
                s += c

    def __iter__(self: Tokenizer):
        return self

    def __next__(self: Tokenizer) -> str:
        if self.token: return self.replace_token("")
        while True:
            c = self.get_char()
            if c == None:
                if self.token:
                    return self.token
                else:
                    raise StopIteration
            elif c in Tokenizer.punctiation: 
                return self.replace_token(c)
            elif c == '[':
                self.skip_comment()
            elif c =='\'':
                return self.replace_token(self.read_quoted())

class NexusFile:

    @staticmethod
    def read(file):
        fields = ['seqid', 'sequence']

