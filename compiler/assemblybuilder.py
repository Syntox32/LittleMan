
class AssemblyBuilder():
    """
    Class to help with generating Little Man assembly code
    """
    
    def __init__(self):
        self.instructions = []
        self.memory = {}
        self.curr_line = 0

    def add_mem(self, name, val):
        # 0: BRA 2
        # 1: MEM $val
        # 2: ...
        self.memory.update({ name: {"value": int(val), "line": self.curr_line + 1} })
        self.instructions.append("BRA " + str(self.curr_line + 2) + "   # assign memory")
        self.instructions.append("MEM " + str(val))
        self.curr_line += 2

    def do_print(self, name):
        # 0: LDA &name
        # 1: OUT
        # 2: ...
        line = self.memory[str(name)]["line"]
        self.instructions.append("LDA " + str(line) + "   # output")
        self.instructions.append("OUT")
        self.curr_line += 2

    def do_read(self, name):
        # 0: INP
        # 1: STA &name
        # 2: ...
        line = self.memory[str(name)]["line"]
        self.instructions.append("INP" + "   # read")
        self.instructions.append("STA " + str(line))
        self.curr_line += 2

    def do_assignment(self, src, dst):
        # Set SRC to DST
        # 0: LDA &src
        # 1: STA &dst
        # 2: ...
        src_line = self.memory[str(src)]["line"]
        dst_line = self.memory[str(dst)]["line"]
        self.instructions.append("LDA " + str(src_line) + "   # assignment")
        self.instructions.append("STA " + str(dst_line))
        self.curr_line += 2

    def do_add(self, target, src):
        # Add SRC to TARGET
        # 0: LDA &target
        # 1: ADD &src
        # 2: ...
        target_line = self.memory[str(target)]["line"]
        src_line = self.memory[str(src)]["line"]
        self.instructions.append("LDA " + str(target_line) + "   # add")
        self.instructions.append("ADD " + str(src_line))
        self.instructions.append("STA " + str(target_line))
        self.curr_line += 3

    def do_sub(self, target, src):
        # Subtract SRC to TARGET
        # 0: LDA &target
        # 1: SUB &src
        # 2: ...
        target_line = self.memory[str(target)]["line"]
        src_line = self.memory[str(src)]["line"]
        self.instructions.append("LDA " + str(target_line) + "   # sub")
        self.instructions.append("SUB " + str(src_line))
        self.instructions.append("STA " + str(target_line))
        self.curr_line += 3

    def do_hlt(self):
        # n-1: ...
        #   n: HLT
        self.instructions.append("HLT" + "   # halt")
        self.curr_line += 1

    def do_gt(self, left, right):
        #
        pass

    def do_lt(self, left, right): pass

    def build(self):
        ret = ""
        self.do_hlt()
        for inst in self.instructions:
            ret += inst + "\n"
        return ret

    def debug_print(self):
        #self.do_hlt()
        print("\nDebug print:")
        for idx, inst in enumerate(self.instructions):
            print("  " + str(idx) + ": " + inst)
