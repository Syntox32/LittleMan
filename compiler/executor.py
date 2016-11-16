from compiler.error import ExecuteError

class Executor():

    def __init__(self, *, testing=False, test_input=7):
        self.testing = testing
        self.testing_output = test_input

    #def smart_error(self, instr, mem_size): pass

    def execute_bytecode(self, mem, memory_size=100):
        """
        Run and execute Little Man instruction codes.
        """
        # Initialize
        ac = 0
        pc = 0
        running = True
        mem_size = memory_size
        output = []

        print("Program Output:")

        # Run instruction cycle
        while running:

            if pc >= len(mem): # imminent IndexError
                raise ExecuteError("Program Counter is out of range ({0}) ".format(str(pc))
                    + "Are you missing a 'HLT' instruction?")

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
                # for testing purposes
                if not self.testing:
                    ac = int(input("Input: "))
                else:
                    ac = self.testing_output
            elif instr == (9 * mem_size) + 2:  # OUT
                print(str(ac))
                output.append(str(ac))

            # Stop/Coffee break
            elif instr == 000:      # HLT
                running = False

            # Error
            else:
                #self.smart_error(instr, mem_size) # try to give a smart error
                raise ExecuteError("Unknown instruction: \'{0}\'".format(instr))

        print("Finished.")
        return output
