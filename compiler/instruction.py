
class VariablePlaceholder:
    def __init__(self, instruction, idx, var_name):
        self.fmt_instr = instruction
        self.idx = idx
        self.name = var_name

class JumpPlaceholder:
    def __init__(self, instruction, jumps_ahead, line, idx):
        self.fmt_instr = instruction
        self.jumps = jumps_ahead
        self.code_location = line
        self.idx = idx

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
        #curr_idx = len(self.asm)
        #vp = VariablePlaceholder("LDA {0}", curr_idx, name)
        #self.placeholders.append(vp)
        self.invalidate_vars = True
        #self.asm.append("<load op>")
        self.asm.append(Instruction("LDA", variable=name, comment="load"))

    def do_print(self):
        self.asm.append(Instruction("OUT", comment="print"))

    def do_read(self):
        self.asm.append(Instruction("INP", comment="read"))

    def store(self, name):
        #curr_idx = len(self.asm)
        #vp = VariablePlaceholder("STA {0}", curr_idx, name)
        #self.placeholders.append(vp)
        self.invalidate_vars = True
        #self.asm.append("<store op>")
        self.asm.append(Instruction("STA", variable=name, comment="store variable"))

    def invalidate_mem(self, memory):
        for vp in self.placeholders:
            val = memory[vp.name]["line"]
            self.asm[vp.idx].set_adr(val)
            #self.asm[vp.idx] = vp.fmt_instr.format(str(val))
        self.invalidate_vars = False

    def invalidate_jump(self, mem_part_len):
        for jp in self.jumps:
            #self.asm[jp.idx] = jp.fmt_instr.format(str((mem_part_len + jp.code_location + jumps)))
            self.asm[jp.idx].set_adr(mem_part_len + jp.code_location + jumps)
        self.invalidate_jump = False

    def build(self):
        return [instr.asm() for instr in self.asm]

    def get_instructions(self):
        return self.asm

    def __str__(self):
        return str(self.expression) + " - invalidate_vars: " + str(self.invalidate_vars)