#!/usr/bin/env python3

def runLittleMan(mem):

    # Initialiser
    ac = 0
    pc = 0
    running = True

    # Kjør instruksjonssyklus
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
            ac = int(input('Input: '))
        elif instr == 902:      # OUT
            print(ac)
        elif instr == 000:      # HLT
            running = False
        else:                   # ERROR
            print('Error')
            running = False

# Les inn et tall og skriv det ut igjen
demo1 = [ 901, 902, 0 ]

# Les inn to tall og skriv ut summen
demo2 = [ 901, 306, 901, 106, 902, 0, 0 ]

# Demo ... hva er dette?
demo3 = [ 505, 902, 105, 305, 601, 1 ]

# Les inn maxverdi og skriv ut Fibonaccitallene mindre eller lik maxverdi
demo4 = [ 901, 321, 518, 902, 519,
          902, 118, 320, 221, 817,
          520, 902, 519, 318, 520,
          319, 606,   0,   1,   1,
          0, 0]

runLittleMan(demo1)