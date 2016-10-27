
class Executor():

    def execute_bytecode(self, mem, memory_size=100):
        """
        Run and execute Little Man instruction codes.
        """
        # Initialize
        ac = 0
        pc = 0
        running = True
        mem_size = memory_size

        print("Program Output:")

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
