import os
from compiler.executor import Executor

class AsmExpression():
    def __init__(self, line_num, index, token, address=None):
        self.line_num = line_num
        self.index = index
        self.token = token
        self.adr = address

class Assembler(Executor):
    """
    Class for interpreting and parsing Little Man assembler into numeric
    instructions that can be understood by the 'Executor' class.
    """

    def run(self, filename):
        """
        Load from file
        """
        path = os.path.abspath(filename)
        ext = os.path.splitext(path)[1]

        if ext == ".man":
            # Read file contents and interpret it
            with open(path, "r") as f:
                contents = f.read()

            exprs = self._interpret(contents)
            bcode = self._parse(exprs)

            #e = Executor()
            #print(dir(e))

            # Print the new bytecode
            print("\nBytecode: [{0}]\n".format(",".join([str(b) for b in bcode])))
            self.execute_bytecode(bcode)
        else:
            # Error unknown extension
            print("I don't recognize that extension: \'{0}\'".format(ext))


    def load(self, string):
        """
        Load from string
        """
        exprs = self._interpret(string)
        bcode = self._parse(exprs, False)

        # Print the new bytecode
        print("\nBytecode: [{0}]\n".format(",".join([str(b) for b in bcode])))
        self.execute_bytecode(bcode)


    def _interpret(self, string):
        """
        Takes in a string of assembler

        Returns a list of expressions
        """
        lines = string.split("\n")
        exprs = []
        #adr_line_offset = 0

        for idx, l in enumerate(lines):
            line = l.strip().upper()

            # Skip empty lines or whole comment lines
            if line == "" or line.startswith("#"):
                #adr_line_offset += 1
                continue

            # Remove comments that are inline with code
            if "#" in line:
                line = line[0:line.index("#")].strip()

            values = line.split(" ")

            if len(values) == 1:   # Handle expressions with no address parameter
                token = line
                exprs.append(AsmExpression(idx, len(exprs), token))
            elif len(values) == 2: # Expressions with a address parameter
                token = values[0]
                adr = int(values[1]) # - adr_line_offset
                if int(adr) > 99:
                    print("Error! Memory address space exceeded: \'{0}\'".format(adr))
                exprs.append(AsmExpression(idx, len(exprs), token, adr))
            else: # Error
                print("Error! Invalid number of values({1}: \'{0}\'".format(len(values), line))

        return exprs


    def _parse(self, expressions, decrement_adr=False):
        """
        Parse a list of expressions into numeric instructions.

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

            # TODO: adr is going to be the same
            # as the line num, so we need to convert
            # the line num into the index of the bytecode

            #if not has_adr:
            #	print(">> {0}".format(token))
            #else:
            #	print(">> {0}:{1}".format(token, adr))


            if   token == "ADD": bytecode.append(100 + adr - adr_decrement) # add X to AC
            elif token == "SUB": bytecode.append(200 + adr - adr_decrement) # sub X from AC

            elif token == "STA": bytecode.append(300 + adr - adr_decrement)	# Store AC in X
            elif token == "LDA": bytecode.append(500 + adr - adr_decrement)	# Load X into AC

            elif token == "BRA": bytecode.append(600 + adr - adr_decrement) # Set PC to X
            elif token == "BRZ": bytecode.append(700 + adr - adr_decrement) # Set PC to X if AC=0
            elif token == "BRP": bytecode.append(800 + adr - adr_decrement) # Set PC to X if AC>0

            elif token == "INP": bytecode.append(901) # Read input to AC
            elif token == "OUT": bytecode.append(902) # Write output from AC

            elif token == "MEM": bytecode.append(adr) # Reserve a memory slot with value==adr
            elif token == "HLT": bytecode.append(000) # Exit

            # A way to add custom bytecode if you should so desire
            elif token.startswith("!"):
                instr = token[1:]
                if ex.adr is not None: # The custom instruction has an address value
                    bytecode.append(int(instr) + adr - 1)
                else: # Simply add the instruction
                    bytecode.append(int(instr))

            else: bytecode.append(adr)
                #print("Parsing Error! Line: {0}, Unknown instruction: \'{1}\'".format(idx, instr))
                #sys.exit(1)

        return bytecode
