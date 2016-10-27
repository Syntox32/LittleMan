# -*- coding: utf-8 -*-
import os
from compiler.executor import Executor
from compiler.tokenizer import Tokenizer
from compiler.token import TokenType, SYMBOLS, KEYWORDS
from compiler.assemblybuilder import AssemblyBuilder
from compiler.assembler import Assembler


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

			t = Tokenizer()
			t.load_from_file(path)

			self.tokens = t.tokenize()

			#with open(path, "r") as f:
			#	contents = f.read()

			#self.reader = StringReader(contents)

			#self.tokens = []

			# Do the actual compilation

			#self._tokenize()
			(exprs, asm) = self._parse(self.tokens)
			#print(asm)

			a = Assembler(mem_size=1000)
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
