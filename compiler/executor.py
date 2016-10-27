
class Executor():

    def execute_bytecode(self, mem):
        """
        Run and execute Little Man instruction codes.
        """
        # Initialize
        ac = 0
        pc = 0
        running = True

        print("Program Output:")

        # Run instruction cycle
        while running:

            # Fetch
            instr = mem[pc]
            pc += 1

            # Execute
            if instr // 100 == 1:   # ADD
                ac += mem[instr % 100]
            elif instr // 100 == 2: # SUB
                ac -= mem[instr % 100]
            elif instr // 100 == 3: # STA
                mem[instr % 100] = ac
            elif instr // 100 == 5: # LDA
                ac = mem[instr % 100]
            elif instr // 100 == 6: # BRA
                pc = instr % 100
            elif instr // 100 == 7: # BRZ
                if ac == 0:
                    pc = instr % 100
            elif instr // 100 == 8: # BRP
                if ac > 0:
                    pc = instr % 100
            elif instr == 901:      # INP
                ac = int(input("Input: "))
            elif instr == 902:      # OUT
                print("> " + str(ac))
            elif instr == 000:      # HLT
                running = False
            else:                   # ERROR
                print("Error! Unknown instruction: \'{0}\'".format(instr))
                running = False

        print("Finished.")
