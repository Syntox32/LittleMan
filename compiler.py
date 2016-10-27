# -*- coding: utf-8 -*-
import os
from enum import Enum, IntEnum

class Executor():
	def execute_bytecode(self, mem):

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
				print("> " + str(ac))
			elif instr == 000:      # HLT
				running = False
			else:                   # ERROR
				print("Error! Unknown instruction: \'{0}\'".format(instr))
				running = False

		print("Finished.")


class StringReader:

    def __init__(self, string):
        self.string = string
        self.idx = 0

    def next(self):
        if self.idx + 1 > len(self.string):
            raise IndexError("String index is out of range.")
        char = self.string[self.idx:self.idx + 1]
        self.idx += 1
        return char

    def peak(self, n=1):
        if self.idx + n > len(self.string):
            raise IndexError("String index is out of range.")
        return self.string[self.idx:self.idx + n]

    def read(self, n):
        if self.idx + n > len(self.string):
            raise IndexError("String index is out of range.")
        char = self.string[self.idx:self.idx + n]
        self.idx += n
        return char

    def read_until(self, c):
        if len(c) != 1:
            raise AttributeError("Argument can only be one character.")
        ret = ""
        while self.idx + 1 <= len(self.string):
            char = self.next()
            ret += char
            if char == c:
                return ret
        return ret

    def skip_whitespace(self):
        while self.idx + 1 <= len(self.string):
            peak_char = self.peak()
            if peak_char != " ":
                break
            self.idx += 1

    @property
    def pos(self):
        return self.idx

    @pos.setter
    def pos(self, value):
        if value < 0 or value >= len(self.string):
            raise IndexError("Position index is out of range.")
        self.idx = value

    @property
    def length(self):
        return len(self.string)


class TokenType(IntEnum):
	IntValue = 0
	Function = 2
	LParen = 3
	RParen = 4
	Equals   = 5 # =
	EqualTo = 6 # ==
	If = 7
	While = 8
	Var = 9
	Identifier = 10
	Print = 11
	Read = 12
	SemiColon = 13
	Add = 14
	Sub = 15
	Mul = 16
	Div = 17
	FuncStart = 18
	FuncEnd = 19
	Colon = 20
	Comment = 21
	Period = 22
	Seperator = 23
	Conditional = 24
	FuncDecl = 25

SYMBOLS = {
	"(": TokenType.LParen,
	")": TokenType.RParen,
	"+": TokenType.Add,
	"-": TokenType.Sub,
	"*": TokenType.Mul,
	"/": TokenType.Div,

	"{": TokenType.FuncStart,
	"}": TokenType.FuncEnd,
	".": TokenType.Period,
	",": TokenType.Seperator,
	";": TokenType.SemiColon,
	":": TokenType.Colon,
	"=": TokenType.Equals,
	"#": TokenType.Comment

	#"var": Token.Var,
	#"if": Token.If,
	#"while": Token.While,
	#"def": Token.Function
}

KEYWORDS = {
	"if": TokenType.Conditional,
	"while": TokenType.While,
	"def": TokenType.FuncDecl,
	"print": TokenType.Function,
	"read": TokenType.Function
}


class AssemblyBuilder():
	def __init__(self):
		self.instructions = []
		self.memory = {}
		self.curr_line = 0

	def add_mem(self, name, val):
		# 0: BRA 2
		# 1: MEM $val
		# 2: ...
		self.memory.update({ name: {"value": int(val), "line": self.curr_line + 1} })
		self.instructions.append("BRA " + str(self.curr_line + 2) + "   # assign memory")
		self.instructions.append("MEM " + str(val))
		self.curr_line += 2

	def do_print(self, name):
		# 0: LDA &name
		# 1: OUT
		# 2: ...
		line = self.memory[str(name)]["line"]
		self.instructions.append("LDA " + str(line) + "   # output")
		self.instructions.append("OUT")
		self.curr_line += 2

	def do_read(self, name):
		# 0: INP
		# 1: STA &name
		# 2: ...
		line = self.memory[str(name)]["line"]
		self.instructions.append("INP" + "   # read")
		self.instructions.append("STA " + str(line))
		self.curr_line += 2

	def do_assignment(self, src, dst):
		# Set SRC to DST
		# 0: LDA &src
		# 1: STA &dst
		# 2: ...
		src_line = self.memory[str(src)]["line"]
		dst_line = self.memory[str(dst)]["line"]
		self.instructions.append("LDA " + str(src_line) + "   # assignment")
		self.instructions.append("STA " + str(dst_line))
		self.curr_line += 2

	def do_add(self, target, src):
		# Add SRC to TARGET
		# 0: LDA &target
		# 1: ADD &src
		# 2: ...
		target_line = self.memory[str(target)]["line"]
		src_line = self.memory[str(src)]["line"]
		self.instructions.append("LDA " + str(target_line) + "   # add")
		self.instructions.append("ADD " + str(src_line))
		self.instructions.append("STA " + str(target_line))
		self.curr_line += 3

	def do_sub(self, target, src):
		# Subtract SRC to TARGET
		# 0: LDA &target
		# 1: SUB &src
		# 2: ...
		target_line = self.memory[str(target)]["line"]
		src_line = self.memory[str(src)]["line"]
		self.instructions.append("LDA " + str(target_line) + "   # sub")
		self.instructions.append("SUB " + str(src_line))
		self.instructions.append("STA " + str(target_line))
		self.curr_line += 3

	def do_hlt(self):
		# n-1: ...
		#   n: HLT
		self.instructions.append("HLT" + "   # halt")
		self.curr_line += 1

	def do_gt(self, left, right):
		#
		pass

	def do_lt(self, left, right): pass

	def build(self):
		ret = ""
		self.do_hlt()
		for inst in self.instructions:
			ret += inst + "\n"
		return ret

	def debug_print(self):
		#self.do_hlt()
		print("\nDebug print:")
		for idx, inst in enumerate(self.instructions):
			print("  " + str(idx) + ": " + inst)

class Token():
	def __init__(self, value, token_type):
		self.value = value
		self.token = token_type

class ScriptAsmExpression():
	def __init__(self, mnemonic, address):
		self.mic = mnemonic
		self.adr = address

class Expression():
	def __init__(self, tokens=None, expressions=None):
		self.tokens = [] if tokens is None else tokens
		self.expressions = [] if expressions is None else expressions

class ScriptCompiler(Executor):
	def __init__(self): pass

	def compile(self, filename):
		path = os.path.abspath(filename)
		ext = os.path.splitext(path)[1]

		if ext == ".script":
			# Read file contents and interpret it
			with open(path, "r") as f:
				contents = f.read()

			self.reader = StringReader(contents)

			self.tokens = []

			# Do the actual compilation

			self._tokenize()
			(exprs, asm) = self._parse(self.tokens)
			#print(asm)

			a = Assembler()
			a.load(asm)

			with open("gen.man", "w") as f:
				f.write(asm)

			# Print out some debug values

			if exprs is not None:
				print("\nExpressions:")
				for idx, val in enumerate(exprs):
					print("   {0}: {1}".format(str(idx)," ".join([str(t.value) for t in val.tokens])))

			print("\nTokens:")
			for t in self.tokens:
				print("   {0}\t\t{1}".format(str(t.value), str(t.token)))
		else:
			# Error unknown extension
			print("I don't recognize that extension: \'{0}\'".format(ext))


	def _tokenize(self):

		curr_str = ""

		def handle_curr_str(currstr):
			if currstr.strip() is not "":
				currstr = currstr.strip()
				token = None
				if currstr in KEYWORDS:
					token = Token(currstr, KEYWORDS[currstr])
				else:
					token = Token(currstr, TokenType.Identifier)
				self.tokens.append(token)
				currstr = ""
			return currstr

		# to the end of the string, do something
		while self.reader.pos != self.reader.length:
			# if there are whitespace, skip it
			if self.reader.peak() == " ":
				curr_str = handle_curr_str(curr_str)
				self.reader.skip_whitespace()

			if self.reader.peak() == "#":
				self.reader.read_until("\n");
				continue

			# Handle newlines
			#if self.reader.peak() == "\n":
				# Remove this line if you want semicolon-based code
				# instead of line based
			#	curr_str = handle_curr_str(curr_str)
				# TODO: Maybe add a TokenType.Newline for easier parsing?
			#	self.reader.next()
			#	continue

			# Check to see if the next character is a symbol we know of
			if self.reader.peak() in SYMBOLS:
				curr_str = handle_curr_str(curr_str)

				char = self.reader.next()
				token = Token(char, SYMBOLS[char])
				self.tokens.append(token)
				continue
			else:
				curr_str += self.reader.next()
				continue


	def _parse(self, tokens):
		exprs = [] # list of ScriptAsmExpressions
		assembly = ""
		var_mem = {}
		in_expr = False
		ASM = AssemblyBuilder()

		# Create a list of expressions before doing any compilation
		temp = [] # List of tokens
		for t in tokens:
			#temp.append(t)
			if t.token == TokenType.SemiColon:
				exprs.append(Expression(temp))
				temp = []
				in_expr = False
			else:
				temp.append(t)
				in_expr = True

		expect_equal = False
		expect_identifier = False
		expect_var_value = False
		curr_var_name = ""

		# returns true or false
		def expr_matches(expr, tokens):
			if len(expr.tokens) != len(tokens):
				return False
			for idx, val in enumerate(expr.tokens):
				if str(val.token) != str(tokens[idx]):
					return False
			return True

		is_var_assignment = lambda x: expr_matches(x, [TokenType.Identifier,
														TokenType.Equals,
														TokenType.Identifier])

		is_func_call = lambda x: expr_matches(x, [TokenType.Function,
													TokenType.LParen,
													TokenType.Identifier,
													TokenType.RParen])

		is_var_add_var = lambda x: expr_matches(x, [TokenType.Identifier,
														TokenType.Add,
														TokenType.Equals,
														TokenType.Identifier])

		is_var_sub_var = lambda x: expr_matches(x, [TokenType.Identifier,
														TokenType.Sub,
														TokenType.Equals,
														TokenType.Identifier])

		def parse_var_assignment(ex):
			var_name = str(ex.tokens[0].value)
			var_val = ex.tokens[2].value
			value_is_name = False

			try:
				value_is_name = str(var_val) in var_mem
			except: pass

			if var_name in var_mem: # Exists
				if value_is_name:
					var_mem[var_name] = var_mem[str(var_val)]
					# add value of var_val to var_name
					#ASM.do_add(var_name, var_val)
					ASM.do_assignment(var_val, var_name)
				else:
					var_mem[var_name] = int(var_val)
					mem_name = str(ASM.curr_line + 1)
					ASM.add_mem(mem_name, int(var_val))
					ASM.do_assignment(mem_name, var_name)
			else: # If it does not exist, we update it with the new value
				if value_is_name:
					var_mem.update({ var_name: var_mem[str(var_val)] })
					# add new memory equal to the value of var_val
					ASM.add_mem(var_name, var_mem[str(var_val)])
					#asm.do_add(var_name, var_val) # ASM
				else:
					var_mem.update({ var_name: int(var_val) })
					ASM.add_mem(var_name, int(var_val))

			# MEM $init_value

		def parse_add_sub(ex):
			var_name = str(ex.tokens[0].value)
			var_val = ex.tokens[3].value
			value_is_name = False
			add = ex.tokens[1].token == TokenType.Add

			try:
				value_is_name = str(var_val) in var_mem
			except: pass

			if var_name in var_mem: # Exists
				if value_is_name:
					#v = var_mem[var_name]
					if add:
					#	v += var_mem[str(var_val)]
						ASM.do_add(var_name, str(var_val))
					else:
					#	v -= var_mem[str(var_val)]
						ASM.do_sub(var_name, str(var_val))
					#var_mem[var_name] = v
				else:
					#v = var_mem[var_name]
					if add:
						mem_name = str(ASM.curr_line + 1)
						ASM.add_mem(mem_name, int(var_val))
						ASM.do_add(var_name, mem_name)
						#v += int(var_val)
					else:
						mem_name = str(ASM.curr_line + 1)
						ASM.add_mem(mem_name, int(var_val))
						ASM.do_sub(var_name, mem_name)
						#v -= int(var_val)
					#var_mem[var_name] = v

		def parse_func_call(ex):
			if str(ex.tokens[0].value) == "print":
				var_name = str(ex.tokens[2].value)
				ASM.do_print(var_name)

			elif str(ex.tokens[0].value) == "read":
				var_name = str(ex.tokens[2].value)
				ASM.do_read(var_name)

		for ex in exprs:
			print("debug: {0}".format(" ".join([str(t.value) for t in ex.tokens])))

			if is_var_assignment(ex):
				print("\tassuming variable assignment")
				parse_var_assignment(ex)

			if is_func_call(ex):
				print("\tassuming function call")
				parse_func_call(ex)

			if is_var_add_var(ex) or is_var_sub_var(ex):
				print("\tassuming add/sub operation on variable")
				parse_add_sub(ex)

		assembly = ASM.build()
		ASM.debug_print()
		return exprs, assembly


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

			#e = Executor()
			#print(dir(e))

			# Print the new bytecode
			print("\nBytecode: [{0}]\n".format(",".join([str(b) for b in bcode])))
			self.execute_bytecode(bcode)
		else:
			# Error unknown extension
			print("I don't recognize that extension: \'{0}\'".format(ext))


	def load(self, string):
		exprs = self._interpret(string)
		bcode = self._parse(exprs, False)

		# Print the new bytecode
		print("\nBytecode: [{0}]\n".format(",".join([str(b) for b in bcode])))
		self.execute_bytecode(bcode)


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


	def _parse(self, expressions, decrement_adr=False):

		bytecode = []
		# This is set to True if we read human written assembly.
		# Lines in margins in editors starts at index 1, so we
		# have to adjust for that by subtracting one.
		adr_decrement = 1 if decrement_adr else 0

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


			if   token == "ADD": bytecode.append(100 + adr - adr_decrement) # add X to AC
			elif token == "SUB": bytecode.append(200 + adr - adr_decrement) # sub X from AC

			elif token == "STA": bytecode.append(300 + adr - adr_decrement)	# Store AC in X
			elif token == "LDA": bytecode.append(500 + adr - adr_decrement)	# Load X into AC

			elif token == "BRA": bytecode.append(600 + adr - adr_decrement) # Set PC to X
			elif token == "BRZ": bytecode.append(700 + adr - adr_decrement) # Set PC to X if AC=0
			elif token == "BRP": bytecode.append(800 + adr - adr_decrement) # Set PC to X if AC>0

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

			else: bytecode.append(adr)
				#print("Parsing Error! Line: {0}, Unknown instruction: \'{1}\'".format(idx, instr))
				#sys.exit(1)

		return bytecode
