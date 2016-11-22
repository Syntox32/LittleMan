import os
from compiler.executor import Executor, StatefullExecutor

class AsmExpression():
    def __init__(self, string, token, address=None):
        self.token = token
        self.adr = address
        self.string = string

    def __str__(self):
        if self.adr is None:
            return "{0}".format(self.token)
        else:
            return "{0} {1}".format(self.token, self.adr)

class Assembler(Executor):
    """
    Class for interpreting and parsing Little Man assembler into numeric
    instructions that can be understood by the 'Executor' class.
    """

    def __init__(self, *, mem_size=100):
        """
        Set memory size
        """
        self.mem_size = mem_size

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

            exprs = self._interpret(contents)
            bcode = self._parse(exprs, decrement_adr=read_from_file)

            #e = Executor()
            #print(dir(e))

            # Print the new bytecode
            print("\nBytecode: [{0}]\n".format(",".join([str(b) for b in bcode])))
            self.execute_bytecode(bcode, self.mem_size)
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
        self.execute_bytecode(bcode, self.mem_size)


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
            if "#" in line:
                line = line[0:line.index("#")].strip()

            values = line.split(" ")

            if len(values) == 1:   # Handle expressions with no address parameter
                token = line
                exprs.append(AsmExpression(line, token))
            elif len(values) == 2: # Expressions with a address parameter
                token = values[0]
                adr = int(values[1])
                #if int(adr) > 99:
                #   print("Error! Memory address space exceeded: \'{0}\'".format(adr))
                exprs.append(AsmExpression(line, token, adr))
            else: # Error
                print("Error! Invalid number of values({1}: \'{0}\'".format(len(values), line))
                return None

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

            if   token == "ADD": bytecode.append((1 * self.mem_size) + adr - adr_decrement) # add X to AC
            elif token == "SUB": bytecode.append((2 * self.mem_size) + adr - adr_decrement) # sub X from AC

            elif token == "STA": bytecode.append((3 * self.mem_size) + adr - adr_decrement)	# Store AC in X
            elif token == "LDA": bytecode.append((5 * self.mem_size) + adr - adr_decrement)	# Load X into AC

            elif token == "BRA": bytecode.append((6 * self.mem_size) + adr - adr_decrement) # Set PC to X
            elif token == "BRZ": bytecode.append((7 * self.mem_size) + adr - adr_decrement) # Set PC to X if AC=0
            elif token == "BRP": bytecode.append((8 * self.mem_size) + adr - adr_decrement) # Set PC to X if AC>0

            elif token == "INP": bytecode.append((9 * self.mem_size) + 1) # Read input to AC
            elif token == "OUT": bytecode.append((9 * self.mem_size) + 2) # Write output from AC

            elif token == "MEM": bytecode.append(adr) # Reserve a memory slot with value==adr
            elif token == "HLT": bytecode.append(000) # Exit

        return bytecode

class TermColors:
    CYAN = '\033[96m'
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Debugger:

    def __init__(self, mem_size=100):
        self.exprs = []
        self.assembler = Assembler(mem_size=mem_size)
        self.executor = StatefullExecutor(mem_size=mem_size)
        self.filename = ""

        self.ASM_VIEW_COUNT = 25
        self.DISPLAY_WIDTH = 50
        self.ASM_VIEW_WIDTH = 22
        self.R_COL_WIDTH = self.DISPLAY_WIDTH - self.ASM_VIEW_WIDTH - 1

    def load_assembler_from_file(self, filename):
        self.filename = filename
        with open(os.path.abspath(filename), "r") as f:
            content = f.read()
            self.load_assembler(content, from_file=True)

    def load_assembler(self, assembler, *, from_file=False):
        self.exprs = self.assembler._interpret(assembler)
        self.instructions = self.assembler._parse(self.exprs, from_file)
        self.executor.load_instructions(self.instructions)
        self.mem_indices = self.get_mem_indices(self.exprs)

    def load_instructions(self, instructions): pass

    def get_mem_indices(self, expressions):
        indices = []
        for idx, expr in enumerate(expressions):
            if expr.token == "MEM":
                indices.append(idx)
        return indices

    def display(self, curr_idx=0):
        #        info
        #----------------------
        # asm     |    mem view
        # ...     |  line 1 MEM value
        # ...     |  line 1 MEM value
        # ...     | -----------
        #         | Program output
        #         |
        # ---------------------
        # cmd help
        # cmd input

        print("Little Man Debugger - " + self.filename)
        print("-" * self.DISPLAY_WIDTH)

        right_col = []

        for i in range(self.ASM_VIEW_COUNT):
            asm_string = ""
            if i < len(self.exprs):
                asm_string = self._string_pad(str(i + 1) + ": " + str(self.exprs[i]),
                                self.ASM_VIEW_WIDTH)
            else:
                asm_string = self._string_pad(str(i) + ": " + asm_string, self.ASM_VIEW_WIDTH)
            if i == curr_idx:
                asm_string = TermColors.FAIL + asm_string + TermColors.ENDC
            asm_string += "|"

            right_col.append(self._string_pad(" Program Counter: " + str(curr_idx), self.R_COL_WIDTH))
            right_col.append(TermColors.CYAN + " Accumulator:   " + str(self.executor.ac) + TermColors.ENDC)
            right_col.append("-" * (self.R_COL_WIDTH - 1))

            # add memory view
            if len(self.mem_indices) != 0:
                right_col.append(" Memory:")
                for imem in self.mem_indices:
                    right_col.append("   {0}: MEM {1}"
                        .format(str(imem + 1), str(self.executor.mem[imem])))

            if len(self.executor.output) != 0:
                right_col.append("-" * (self.R_COL_WIDTH - 1))
                right_col.append(" Output:")
                for out in self.executor.output:
                    right_col.append("   > {0}".format(out))

            if i < len(right_col):
                asm_string += right_col[i]

            print(asm_string)
            right_col = []

        print("-" * self.DISPLAY_WIDTH)
        print("(N)ext, (Q)uit | Experimental: (P)rev, (R)eset")


    def next(self, quit=False):
        ret = 0

        if quit:
            print("User terminated session.")
            return

        if self.executor.running:
            self._clear()
            self.display(self.executor.pc)

            ret = self.executor.next()
            if ret is None:
                print("Error: Uknown instruction at line: {0}"
                    .format(self.executor.pc))

            if ret == 1: # request input
                cmd = self.get_input(get_input=True)
                self.executor.get_input(int(cmd))
                #self.executor.push_state()
                self.next()
                return None

            ret = self.handle_command()
            while ret is False:
                ret = self.handle_command()


    def _string_pad(self, string, width, fill=" "):
        return string + fill*(width-len(string))

    def handle_command(self):
        cmd = self.get_input().lower()

        commands = ["next", "prev", "quit", "reset"]

        if cmd.startswith("n"):
            #self.executor.push_state()
            self.next()

        elif cmd.startswith("p"):
            ret = self.executor.rollback_state()
            if not ret:
                print("Error!: Not state to roll back to.")
                return False
            self.mem_indices = self.get_mem_indices(self.exprs)
            self.next()

        elif cmd.startswith("q"):
            self.next(quit=True)

        elif cmd.startswith("r"):
            self.executor.reset()
            self.mem_indices = self.get_mem_indices(self.exprs)
            #self.executor.push_state()
            self.next()

        elif cmd == "":
            return False

        return any([True for c in commands if c.startswith(cmd)])

    def get_input(self, get_input=False):
        prefix = "> "
        if get_input:
            prefix = TermColors.CYAN + "Input: " + TermColors.ENDC
        cmd = input(prefix)

        def convert_int(val):
            try:
                return int(val)
            except Exception as e:
                return None

        if get_input:
            while convert_int(cmd) is None:
                print("(error: program input must be of type 'int')")
                cmd = input(prefix)

        return cmd

    def _clear(self):
        os.system("clear")

    def _remove_comments(self, asm):
        ret = []
        for a in asm:
            line = a.strip().upper()
            if "#" in line:
                line = line[0:line.index("#")].strip()
            ret.append(line)
        return ret
