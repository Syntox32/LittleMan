import os
from compiler.executor import Executor
from compiler.error import AssemblerError, ParseError, ExtensionError

class AsmExpression():
    def __init__(self, token, address=None):
        self.token = token
        self.adr = address

class Assembler(Executor):
    """
    Class for interpreting and parsing Little Man assembler into numeric
    instructions that can be understood by the 'Executor' class.
    """

    def __init__(self, *, mem_size=100, testing=False):
        """
        Set memory size
        """
        self.mem_size = mem_size
        self.testing = testing
        super().__init__(testing=testing)

    def run(self, filename, read_from_file=False):
        """
        Load from file
        """
        path = os.path.abspath(filename)
        ext = os.path.splitext(path)[1]

        if ext == ".man":
            # Read file contents and interpret it
            with open(path, "r") as f:
                contents = f.read()

            return self.load(contents, read_from_file)
        else:
            # Error unknown extension
            raise ExtensionError("Unknown extension: \'{0}\'".format(ext))


    def load(self, string, read_from_file=False):
        """
        Load from string
        """
        exprs = self._interpret(string)
        bcode = self._parse(exprs, decrement_adr=read_from_file)

        # Print the new bytecode
        print("\nBytecode: [{0}]\n".format(",".join([str(b) for b in bcode])))

        return self.execute_bytecode(bcode, self.mem_size)


    def _interpret(self, string):
        """
        Takes in a string of assembler

        Returns a list of expressions
        """
        lines = string.split("\n")
        exprs = []

        for l in lines:
            line = l.strip().upper()

            # Remove comments that are inline with code.
            # Whole comment lines are not supported.
            if "#" in line: line = line[0:line.index("#")].strip()

            values = line.split(" ")

            if len(values) == 1:   # Handle expressions with no address parameter
                token = line
                exprs.append(AsmExpression(token))
            elif len(values) == 2: # Expressions with a address parameter
                token = values[0]
                adr = int(values[1])
                #if int(adr) > 99:
                #   print("Error! Memory address space exceeded: \'{0}\'".format(adr))
                exprs.append(AsmExpression(token, adr))
            else: # Error
                raise ParseError("Invalid number of values('{1}'): {0}".format(len(values), line))

        return exprs


    def _parse(self, expressions, decrement_adr=False):
        """
        Parse a list of expressions into numeric instructions.

        Use decrement_adr if you have handwritten the assembly and have
        followed a line margin that starts at 1.

        Returns list of instructions.
        """
        bytecode = []
        # This is set to True if we read human written assembly.
        # Lines in margins in editors starts at index 1, so we
        # have to adjust for that by subtracting one.
        adr_decrement = 1 if decrement_adr else 0

        for idx, ex in enumerate(expressions):
            token = ex.token
            has_adr = ex.adr is not None
            adr  = int(ex.adr) if has_adr else None

            if token == "": continue # if we find an empty token, skip it

            # Check if the instruction is missing an address
            if not has_adr and token in ["ADD", "SUB", "STA", "LDA", "BRA", "BRZ", "BRP", "MEM"]:
                raise ParseError("Expected address for instruction: '{0}' Line: {1}"
                    .format(token, str(idx + 1)))

            if   token == "ADD": bytecode.append((1 * self.mem_size) + adr - adr_decrement) # add X to AC
            elif token == "SUB": bytecode.append((2 * self.mem_size) + adr - adr_decrement) # sub X from AC

            elif token == "STA": bytecode.append((3 * self.mem_size)  + adr - adr_decrement) # Store AC in X
            elif token == "LDA": bytecode.append((5 * self.mem_size)  + adr - adr_decrement) # Load X into AC

            elif token == "BRA": bytecode.append((6 * self.mem_size)  + adr - adr_decrement) # Set PC to X
            elif token == "BRZ": bytecode.append((7 * self.mem_size)  + adr - adr_decrement) # Set PC to X if AC=0
            elif token == "BRP": bytecode.append((8 * self.mem_size)  + adr - adr_decrement) # Set PC to X if AC>0

            elif token == "INP": bytecode.append((9 * self.mem_size) + 1) # Read input to AC
            elif token == "OUT": bytecode.append((9 * self.mem_size) + 2) # Write output from AC

            elif token == "MEM": bytecode.append(adr) # Reserve a memory slot with value==adr
            elif token == "HLT": bytecode.append(000) # Exit

            else: # unknown token
                raise ParseError("Unknown token: '{0}'".format(token))

        return bytecode
