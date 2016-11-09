from compiler.instruction import Instruction, JumpFlag
from compiler.utils import Utils

class Memory:

    GlobalTempCount = 0
    GlobalNameCount = 0
    GlobalJumpCount = 0

    def __init__(self):
        self.memory = {}

    def has_reference(self, identifier):
        """
        check if memory exists
        """
        return identifier in self.memory

    def get_reference(self, identifier):
        """
        get memory reference
        """
        if self.has_reference(identifier):
            return self.memory[identifier]
        else:
            Utils.debug("Compiler Error!: No reference to variable \'{0}\'"
                .format(identifier))
        return None

    def add_reference(self, identifier, init_value=0):
        self.memory.update({ identifier: {"value": init_value, "line": -1} })
        self.debug()
        return identifier

    def gen_asm(self):
        """
        returns a list of 'Instruction' and 'JumpFlag'
        """
        jump_id = Memory.gen_jump_name()
        inst = [Instruction("BRA", jump=jump_id, comment="jump over memory")]

        for idx, m in enumerate(self.memory):
            ref = self.memory[m]

            i = Instruction("MEM", adr=ref["value"], comment="<{0}>".format(m))
            inst.append(i)

            # Update the memory table so that we can use it
            # as a lookup table with for it's location in the file.
            #
            # Memory is always the first thing in the file, so
            # we can safely say the first index + 1 (jump over the BRA instruction)
            # will make it align properly.
            #
            ref["line"] = idx + 1
            self.memory[m] = ref

        inst.append(JumpFlag(jump_id))
        return inst

    def bind_mem(self, instructions):
        """
        returns True if the binding was successfull,

        otherwise it returns False.
        """
        for inst in instructions:
            # check if the instruction requires a binding
            if inst.invalidate_binding:
                requires = inst.variable

                ref = self.get_reference(requires)
                if ref is None:
                    return None

                if ref["line"] == -1:
                    print("Compiler Error!: Lines where never binded to memory.")
                    return None

                # set the adr to the memory
                inst.set_adr(ref["line"])

        return instructions # success

    def merge(self, other_memory):
        """
        returns True if the binding was successfull,

        otherwise it returns False.
        """
        for m in other_memory:
            if m in self.memory:
                print("Compiler Error!: Memory merge conflict.")
                return False

            self.memory.update({m: other_memory[m]})

        return True

    def get(self):
        return self.memory

    def debug(self):
        print("Memory view:")
        for m in self.memory:
            print("\t{0}:   {1}".format(m, self.memory[m]["value"]))

    ## Static methods

    @staticmethod
    def gen_temp_name():
        name = "temp_{0}".format(str(Memory.GlobalTempCount))
        Memory.GlobalTempCount += 1
        return name

    @staticmethod
    def gen_name():
        name = "mem_{0}".format(str(Memory.GlobalNameCount))
        Memory.GlobalNameCount += 1
        return name

    @staticmethod
    def gen_jump_name():
        name = "jump_{0}".format(str(Memory.GlobalJumpCount))
        Memory.GlobalJumpCount += 1
        return name
