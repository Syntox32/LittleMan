import os
from compiler.stringreader import StringReader
from compiler.token import TokenType, SYMBOLS, KEYWORDS

class Token():
    def __init__(self, value, token_type):
        self.value = value
        self.token = token_type

class Tokenizer():
    """
    Turn a string or file into tokens
    """

    def load(self, string):
        """
        Load from string
        """
        self.reader = StringReader(string)

    def load_from_file(self, filename):
        """
        Read from file
        """
        path = os.path.abspath(filename)
        with open(path, "r") as f:
            self.reader = StringReader(f.read())

    def tokenize(self):
        """
        Tokenize the contents of string.
        symbols and keywords are defined in 'token.py'

        Return a list of tokens.
        """
        tokens = []
        curr_str = ""

        # This is explained later in the method
        expecting_identifier = False

        def handle_curr_str(currstr):
            """
            Check to see if the current string is either
            an identifier or is in the KEYWORDS list,
            if it is we add it as a token with the corresponding tokentype
            """
            if currstr.strip() is not "":
                currstr = currstr.strip()
                token = None

                if currstr in KEYWORDS:
                    token = Token(currstr, KEYWORDS[currstr])
                else:
                    token = Token(currstr, TokenType.Identifier)

                tokens.append(token)
                currstr = ""
            return currstr

        # to the end of the string, do something
        while self.reader.pos != self.reader.length:

            # If there is whitespace, we skip it
            if self.reader.peak() == " ":
                # Maybe create identifier
                curr_str = handle_curr_str(curr_str)
                self.reader.skip_whitespace()
                continue

            # Skip to the end of the line if there is comments
            if self.reader.peak() == "#":
                self.reader.read_until("\n");
                continue

            #if expecting_identifier

            # Handle newlines as end of line
            # if self.reader.peak() == "\n":
            #    Remove this line if you want semicolon-based code
            #    instead of line based
            #	 curr_str = handle_curr_str(curr_str)
            #    TODO: Maybe add a TokenType.Newline for easier parsing?
            #	 self.reader.next()
            #	 continue

            # If the tokenizer expects an idenfitier (e.g. "1") and it finds
            # a char "-" it will add a "0" token before it, such that the
            # expression solver will be able to evalutate the expression.
            # Example: "var = -2;" becomes "var = 0 - 2;"
            if (self.reader.peak() == "+" or self.reader.peak() == "-") \
                    and expecting_identifier:
                token = Token("0", TokenType.Identifier)
                tokens.append(token)
                expecting_identifier = False

            if self.reader.peak() == "=":
                expecting_identifier = True

            # Check to see if the next character is a symbol we know of
            if self.reader.peak() in SYMBOLS:
                # Maybe create identifier
                curr_str = handle_curr_str(curr_str)

                char = self.reader.next()
                token = Token(char, SYMBOLS[char])
                tokens.append(token)

                # This is a hack to make sure assignments like "-13" and
                # "-13 + - 10" work.
                #
                # If the tokenizer detects that there are two consecutive
                # operators, it will place a "0" token idenfitier in the middle
                # so that the expression solver can evaluate it.
                # Example:
                #   > foo = -13 + - + 10;
                #   becomes
                #   > foo = 0 - 13 + 0 - 10;
                ops = ["+", "-"]
                self.reader.skip_whitespace()
                if char == "-" and self.reader.peak() == "+":
                    self.reader.next()
                elif char in ops and self.reader.peak() in ops:
                    token = Token("0", TokenType.Identifier)
                    tokens.append(token)
            else:
                curr_str += self.reader.next()
                expecting_identifier = False


        return tokens
