
class StringReader:
    """
    A string-reader made with expression parsing in mind.

    Author: Anders Milje <https://github.com/Syntox32>
    """

    def __init__(self, string):
        self.string = string
        self.idx = 0

    def next(self):
        """
        Move forward one character and incrementing the index.
        """
        if self.idx + 1 > len(self.string):
            raise IndexError("String index is out of range.")
        char = self.string[self.idx:self.idx + 1]
        self.idx += 1
        return char

    def peak(self, n=1):
        """
        Return the next character without incrementing the index.
        """
        if self.idx + n > len(self.string):
            raise IndexError("String index is out of range.")
        return self.string[self.idx:self.idx + n]

    def read(self, n):
        """
        Read N characters from the current index and return the resulting string.
        """
        if self.idx + n > len(self.string):
            raise IndexError("String index is out of range.")
        char = self.string[self.idx:self.idx + n]
        self.idx += n
        return char

    def read_until(self, c):
        """
        Read characters until we encounter char C, then we return the result string.

        Char C is included in the return string.
        """
        if len(c) != 1:
            raise AttributeError("Argument can only be one character.")
        ret = ""
        while self.idx + 1 <= len(self.string):
            char = self.next()
            ret += char
            if char == c:
                return ret
        return ret

    def skip_whitespace(self):
        """
        Increment while the next character is whitespace.
        """
        while self.idx + 1 <= len(self.string):
            peak_char = self.peak()
            if peak_char != " ":
                break
            self.idx += 1

    @property
    def pos(self):
        """
        Our position in the string.
        """
        return self.idx

    @pos.setter
    def pos(self, value):
        """
        Set our position in the string.
        """
        if value < 0 or value >= len(self.string):
            raise IndexError("Position index is out of range.")
        self.idx = value

    @property
    def length(self):
        """
        Return the length of the string we're reading through.
        """
        return len(self.string)
