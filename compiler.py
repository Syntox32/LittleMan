
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

			#print("> {0}".format(instr))

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
	def __init__(self, line_num, index, token, address=None):
		self.line_num = line_num
		self.index = index
		self.token = token
		self.adr = address


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

			# Print the new bytecode
			print("[{0}]".format(",".join([str(b) for b in bcode])))
			super().execute_bytecode(bcode)
		else:
			# Error unknown extension
			print("I don't recognize that extension: \'{0}\'".format(ext))


	def _interpret(self, string):
		lines = string.split("\n")
		exprs = []
		#adr_line_offset = 0

		for idx, l in enumerate(lines):
			line = l.strip().upper()

			# Skip empty lines or whole comment lines
			if line == "" or line.startswith("#"):
				#adr_line_offset += 1
				continue

			# Remove comments that are inline with code
			if "#" in line:
				line = line[0:line.index("#")].strip()

			values = line.split(" ")

			if len(values) == 1:   # Handle expressions with no address parameter
				token = line
				exprs.append(AsmExpression(idx, len(exprs), token))
			elif len(values) == 2: # Expressions with a address parameter
				token = values[0]
				adr = int(values[1]) # - adr_line_offset
				if int(adr) > 99:
					print("Error! Memory address space exceeded: \'{0}\'".format(adr))
				exprs.append(AsmExpression(idx, len(exprs), token, adr))
			else: # Error
				print("Error! Invalid number of values({1}: \'{0}\'".format(len(values), line))

		return exprs


	def _parse(self, expressions):

		bytecode = []

		for idx, ex in enumerate(expressions):
			token = ex.token
			has_adr = ex.adr is not None
			adr  = int(ex.adr) if has_adr else None

			# TODO: adr is going to be the same
			# as the line num, so we need to convert
			# the line num into the index of the bytecode

			#if not has_adr:
			#	print(">> {0}".format(token))
			#else:
			#	print(">> {0}:{1}".format(token, adr))


			if   token == "ADD": bytecode.append(100 + adr - 1) # add X to AC
			elif token == "SUB": bytecode.append(200 + adr - 1) # sub X from AC

			elif token == "STA": bytecode.append(300 + adr - 1)	# Store AC in X
			elif token == "LDA": bytecode.append(500 + adr - 1)	# Load X into AC
			
			elif token == "BRA": bytecode.append(600 + adr - 1) # Set PC to X
			elif token == "BRZ": bytecode.append(700 + adr - 1) # Set PC to X if AC=0
			elif token == "BRP": bytecode.append(800 + adr - 1) # Set PC to X if AC>0
			
			elif token == "INP": bytecode.append(901) # Read input to AC
			elif token == "OUT": bytecode.append(902) # Write output from AC
			
			elif token == "MEM": bytecode.append(adr) # Reserve a memory slot with value==adr
			elif token == "HLT": bytecode.append(000) # Exit

			# A way to add custom bytecode if you should so desire
			elif token.startswith("!"):
				instr = token[1:]
				if ex.adr is not None: # The custom instruction has an address value
					bytecode.append(int(instr) + adr - 1)
				else: # Simply add the instruction
					bytecode.append(int(instr))

			else: # Error
				print("Parsing Error! Line: {0}, Unknown instruction: \'{1}\'".format(idx, instr))
				sys.exit(1)

		return bytecode