
class Executor:

    def execute_bytecode(self, mem, memory_size=100):
        """
        Run and execute Little Man instruction codes.
        """
        # Initialize
        ac = 0
        pc = 0
        running = True
        mem_size = memory_size

        print(TermColors.HEADER + "Program Output:")

        # Run instruction cycle
        while running:

            # Fetch
            instr = mem[pc]
            pc += 1

            # Add, Subtract
            if instr // mem_size == 1:   # ADD
                ac += mem[instr % mem_size]
            elif instr // mem_size == 2: # SUB
                ac -= mem[instr % mem_size]

            # Store and load
            elif instr // mem_size == 3: # STA
                mem[instr % mem_size] = ac
            elif instr // mem_size == 5: # LDA
                ac = mem[instr % mem_size]

            # Branch operations
            elif instr // mem_size == 6: # BRA
                pc = instr % mem_size
            elif instr // mem_size == 7: # BRZ
                if ac == 0:
                    pc = instr % mem_size
            elif instr // mem_size == 8: # BRP
                if ac > 0:
                    pc = instr % mem_size

            # I/O
            elif instr == (9 * mem_size) + 1:  # INP
                ac = int(input("Input: "))
            elif instr == (9 * mem_size) + 2:  # OUT
                print(str(ac))

            # Stop/Coffee break
            elif instr == 000:      # HLT
                running = False

            # Error
            else:                        # ERROR
                print("Error! Unknown instruction: \'{0}\'".format(instr))
                running = False

        print("Finished.")

class ExecuteState:
    def __init__(self, ac, pc, init_mem, mem, output, running, mem_size):
        self.ac = ac
        self.pc = pc
        self.init_mem = init_mem
        self.mem = mem
        self.output = output
        self.running = running
        self.mem_size = mem_size

class StatefullExecutor:

    def __init__(self, mem_size=100):
        self.mem_size = mem_size
        self.pc = 0
        self.ac = 0
        self.mem = []
        self.running = False
        self.output = []
        self.states = []

    def load_instructions(self, mem):
        self.init_mem = mem
        self.mem = mem
        self.running = True
        self.output = []
        self.pc = 0
        self.ac = 0
        self.states = []

        self.push_state()

    def reset(self):
        self.mem = self.init_mem
        #print(mem)
        self.running = True
        self.output = []
        self.pc = 0
        self.ac = 0
        self.states = []

    def preserve_state(self):
        return ExecuteState(
            self.ac,
            self.pc,
            self.init_mem,
            self.mem,
            self.output,
            self.running,
            self.mem_size)

    def load_state(self, state, curr_states):
        self.ac = state.ac
        self.pc = state.pc
        #self.init_mem = state.init_mem
        self.mem = state.mem
        self.output = state.output
        self.running = state.running
        self.mem_size = state.mem_size
        self.states = curr_states

    def push_state(self):
        self.states.append(self.preserve_state())

    def rollback_state(self):
        if len(self.states) == 0:
            #print("Error!: No state to roll back to.")
            return False
        self.load_state(self.states[len(self.states)-1],
            self.states[:len(self.states)-1])
        return True

    def get_input(self, inp=None):
        if inp is None:
            self.ac = int(input("Input: "))
        else:
            self.ac = int(inp)

    def get_output(self):
        return str(self.ac)

    def next(self):
        """
        An executor with a state.

        Returns:
            None - error, unknown instructions
            0 - success
            1 - requesting input
            2 - requesting output
        """
        #self.running = True

        #print("DEBUG: " + str(self.pc))
        # Fetch
        if self.pc >= len(self.mem):
            print("Detected index out of range:\n\tPC: {0}"
                .format(str(self.pc)))
            return None
        instr = self.mem[self.pc]
        self.pc += 1

        # Add, Subtract
        if instr // self.mem_size == 1:   # ADD
            self.ac += self.mem[instr % self.mem_size]
        elif instr // self.mem_size == 2: # SUB
            self.ac -= self.mem[instr % self.mem_size]

        # Store and load
        elif instr // self.mem_size == 3: # STA
            self.mem[instr % self.mem_size] = self.ac
        elif instr // self.mem_size == 5: # LDA
            self.ac = self.mem[instr % self.mem_size]

        # Branch operations
        elif instr // self.mem_size == 6: # BRA
            self.pc = instr % self.mem_size
        elif instr // self.mem_size == 7: # BRZ
            if self.ac == 0:
                self.pc = instr % self.mem_size
        elif instr // self.mem_size == 8: # BRP
            if self.ac > 0:
                self.pc = instr % self.mem_size

        # I/O
        elif instr == (9 * self.mem_size) + 1:  # INP
            #self.ac = int(input("Input: "))
            self.push_state()
            return 1
        elif instr == (9 * self.mem_size) + 2:  # OUT
            #print(str(self.ac))
            self.output.append(str(self.ac))
            self.push_state()
            return 2

        # Stop/Coffee break
        elif instr == 000:      # HLT
            self.running = False

        # Error
        else:                        # ERROR
            print("Error! Unknown instruction: \'{0}\'".format(instr))
            self.running = False
            return None

        self.push_state()
        return 0
