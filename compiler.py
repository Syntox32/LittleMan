
import os

class Executor():
	def execute_bytecode(self, mem):

		# Initialize
		ac = 0
		pc = 0
		running = True

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
				print(ac)
			elif instr == 000:      # HLT
				running = False
			else:                   # ERROR
				print("Error! Unknown instruction: \'{0}\'".format(instr))
				running = False


class AsmExpression():
	def __init__(self, token, address=None):
		self.token = token
		self.adr = address

	def get_opcode(): pass


class Assembler(Executor):
	
	def run(self, filename):
		path = os.path.abspath(filename)
		ext = os.path.splitext(path)[1]
		
		if ext == ".man":
			# Read file contents and interpret it
			with open(path, "r") as f:
				contents = f.read()

			exprs = self._interpret(contents)
			bcode = self._parse(exprs)

			print(",".join([str(b) for b in bcode]))
			super().execute_bytecode(bcode)
		else:
			# Error unknown extension
			print("I don't recognize that extension: \'{0}\'".format(ext))


	def _interpret(self, string):
		lines = string.split("\n")
		lines = self._prep_lines(lines)

		exprs = []

		for l in lines:
			values = l.split(" ")

			if len(values) == 1:   # Handle expressions with no address parameter
				token = l
				exprs.append(AsmExpression(token))
			elif len(values) == 2: # Expressions with a address parameter
				token = values[0]
				adr = values[1]
				if int(adr) > 99:
					print("Error! Memory address space exceeded: \'{0}\'".format(adr))
				exprs.append(AsmExpression(token, adr))
			else: # Error
				print("Error! Invalid number of values({1}: \'{0}\'".format(len(values), l))

		return exprs

	def _prep_lines(self, lines):
		"""
		Remove comments and emtpy lines.
		"""
		clean_lines = []
		for l in lines:
			line = l.strip().upper()
			
			# Skip empty lines or whole comment lines
			if line == "" or line.startswith("#"): continue
			# Remove comments that are inline with code
			if "#" in line:
				line = line[0:line.index("#")]
			clean_lines.append(line)

		return clean_lines

	def _parse(self, expressions):

		bytecode = []

		for ex in expressions:
			token = ex.token
			has_adr = ex.adr is not None
			adr  = int(ex.adr) if has_adr else None

			if   token == "ADD": bytecode.append(100 + adr) # add X to AC
			elif token == "SUB": bytecode.append(200 + adr) # sub X from AC

			elif token == "STA": bytecode.append(300 + adr)	# Store AC in X
			elif token == "LDA": bytecode.append(500 + adr)	# Load X into AC
			
			elif token == "BRA": bytecode.append(600 + adr) # Set PC to X
			elif token == "BRZ": bytecode.append(700 + adr) # Set PC to X if AC=0
			elif token == "BRP": bytecode.append(800 + adr) # Set PC to X if AC>0
			
			elif token == "INP": bytecode.append(901) # Read input to AC
			elif token == "OUT": bytecode.append(902) # Write output from AC
			
			elif token == "MEM": bytecode.append(adr) # Reserve a memory slot with value==adr
			elif token == "HLT": bytecode.append(000) # Exit

			# A way to add custom bytecode if you should so desire
			elif token.startswith("!"):
				instr = token[1:]
				if ex.adr is not None: # The custom instruction has an address value
					bytecode.append(int(instr) + adr)
				else: # Simply add the instruction
					bytecode.append(int(instr))

			else: # Error
				print("Parsing Error! Unknown instruction: \'{0}\'".format(instr))
				sys.exit(1)

		return bytecode