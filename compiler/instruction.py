
class JumpFlag:
    def __init__(self, alias):
        self.alias = alias

    def __str__(self):
        return "<jump: {0}>".format(self.alias)

class Instruction:
    def __init__(self, instruction, *, adr=None, variable=None, jump=None, comment=None, alias=None):
        self.adr = adr
        self.instruction = instruction
        self.has_adr = False if adr is None else True
        self.flags = []
        self.comment = "" if comment is None else comment
        self.alias = "" if alias is None else alias

        self.variable = variable
        self.invalidate_binding = self.variable is not None
        self.jump = jump
        self.invalidate_jump_bindings = self.jump is not None

        self.is_jump_endpoint = False
        self.jumps = []

    def add_jump(self, jp_flag):
        if not self.is_jump_endpoint:
            self.is_jump_endpoint = True
        self.jumps.append(jp_flag)

    def has_flag(self, flag):
        for f in self.flags:
            if f == flag:
                return True
        return False

    def set_adr(self, adr):
        self.adr = adr
        self.has_adr = True
        self.invalidate_binding = False
        self.invalidate_jump_bindings = False

    def _get_comment(self):
        # TODO: print comments "evenly?"
        return "" if self.comment is None else "\t\t# " + self.comment

    def asm(self):
        s = ""
        if self.invalidate_binding or self.invalidate_jump_bindings:
            var = self.variable if self.invalidate_binding else self.jump
            s = "{0} <{1}>{2}".format(self.instruction, var, self._get_comment())
        elif self.has_adr:
            s = "{0} {1}{2}".format(self.instruction, str(self.adr), self._get_comment())
        else:
            s = "{0}    {1}".format(self.instruction, self._get_comment())

        if self.is_jump_endpoint:
            s += "  ({0})".format(",".join([j.alias for j in self.jumps]))

        return s

    def __str__(self):
        return self.asm()


class AsmExpressionContainer:
    def __init__(self, expression): #, asm_instructions=None, asm_expressions=None):
        self.expression = expression
        self.asm = [] #[] if asm_instructions is None else asm
        self.asm_expressions = [] #asm_expressions
        self.invalidate_vars = False
        self.placeholders = []
        self.jumps = []
        self.invalidate_jumps = True

    def add(self, instr):
        self.asm.append(instr)

    def load(self, name):
        self.invalidate_vars = True
        self.asm.append(Instruction("LDA", variable=name, comment="load"))

    def do_print(self):
        self.asm.append(Instruction("OUT", comment="print"))

    def do_read(self):
        self.asm.append(Instruction("INP", comment="read"))

    def store(self, name):
        self.invalidate_vars = True
        self.asm.append(Instruction("STA", variable=name, comment="store variable"))

    def merge(self, container):
        if isinstance(container, list):
            for a in container_list:
                self.asm.extend(a.get_instructions())
        elif isinstance(container, AsmExpressionContainer):
            self.asm.extend(container.get_instructions())
        else:
            print("Compiler Error!: Cannot merge container of type: "
                + type(container))

    def build(self):
        return [instr.asm() for instr in self.asm]

    def get_instructions(self):
        return self.asm

    def __str__(self):
        return str(self.expression) + " - invalidate_vars: " + str(self.invalidate_vars)
