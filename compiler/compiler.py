# -*- coding: utf-8 -*-
import os, inspect
from compiler.error import AssemblerError, ParseError, ExtensionError
from compiler.executor import Executor
from compiler.tokenizer import Tokenizer, Token
from compiler.token import TokenType, SYMBOLS, KEYWORDS
from compiler.assembler import Assembler
from compiler.expression import Stack, Expression, ExpressionSolver
from compiler.instruction import Instruction, AsmExpressionContainer, JumpFlag
from compiler.memory import Memory
from compiler.utils import Utils

class ScriptCompiler(Executor):

    def __init__(self, *, testing=False):
        self.testing = testing
        self.debug = False
        self.mem = Memory()
        self.jump_table = {}
        self.solver = ExpressionSolver()

    def compile_from_file(self, filename, *, debug=False):
        path = os.path.abspath(filename)
        ext = os.path.splitext(path)[1]

        if ext != ".script":
            raise ExtensionError("Unknown extension: \'{0}\'".format(ext))

        with open(path, "r") as f:
            return self.compile(f.read(), debug=debug)


    def compile(self, string, *, debug=False):
        self.debug = debug

        # Read file contents and interpret it
        t = Tokenizer()
        t.load(string)

        self.tokens = t.tokenize()

        print("\nTokens:")
        for t in self.tokens: print("   {0}\t\t{1}".format(str(t.value), str(t.token)))

        (exprs, asm) = self._parse(self.tokens)

        a = Assembler(mem_size=100, testing=self.testing)
        output = a.load(asm)


        return output


    def _print_expr_tree(self, exprs, prefix=""):
        if len(exprs) == 0: return
        idx = 0
        curr = exprs[idx]
        while curr != None:
            print("{0}{1}".format(prefix, curr))

            if len(curr.expressions) != 0:
                self._print_expr_tree(curr.expressions, prefix + "\t")

            if idx + 1 < len(exprs):
                idx += 1
                curr = exprs[idx]
            else:
                curr = None


    def _parse_expr_recursive(self, tokens):
        exprs = []
        temp = []
        expr_stack = Stack()
        block_expr = None

        in_block = False
        level = 0
        idx = 0

        while idx < len(tokens):
            # increment
            t = tokens[idx]
            idx += 1

            # start parsing tokens

            if t.token == TokenType.FuncStart: # {
                # discard token
                # increment level
                level += 1

                # init an expression on the stack
                e = Expression(temp)
                expr_stack.push(e)
                temp = []

                # set inblock to true
                if not in_block: in_block = True
                else: pass # already in a block

            elif t.token == TokenType.FuncEnd: # }
                # discard token
                # increment level
                level -= 1

                if level > 0:
                    curr = expr_stack.pop()
                    prev = expr_stack.pop()
                    prev.expressions.append(curr)
                    expr_stack.push(prev)
                elif level == 0:
                    in_block = False
                    curr = expr_stack.pop()
                    # we're now at the lowest level and there is no
                    # other block on the stack (...shouldn't be atleast).
                    exprs.append(curr)
                else:
                    pass # error?

            elif t.token == TokenType.SemiColon:
                # discard token
                # now turn temp list into an expression
                e = Expression(temp)
                temp = []

                if in_block:
                    curr = expr_stack.pop()
                    curr.expressions.append(e)
                    expr_stack.push(curr)
                else:
                    exprs.append(e)

            else: # just add the token to the temp list
                temp.append(t)

        self._print_expr_tree(exprs) # debug

        return exprs


    def _handle_assignment(self, ex):
        """
        if the identifier does not exist, create a reference,
        solve the expression with the 'result_var' set to this identifier.

        if the identifier exists, create a temp reference to add the
        expression result into, then add the instructions to move the temp
        result variable into the reference.
        """
        identifier = str(ex.tokens[0].value)
        # skip the identifier and the '=' char
        relevant_tokens = ex.tokens[2:]

        asm = AsmExpressionContainer(ex)

        # reference does not exist
        if not self.mem.has_reference(identifier):
            if len(relevant_tokens) == 1 and relevant_tokens[0].value.isdigit():
                # one token that is an int value
                self.mem.add_reference(identifier, relevant_tokens[0].value)
            elif len(relevant_tokens) == 1 and self.mem.has_reference(relevant_tokens[0].value):
                # one token that is an identifier
                self.mem.add_reference(identifier, self.mem.get_reference(relevant_tokens[0].value))
            else:
                # several tokens, let's solve it
                self.mem.add_reference(identifier)
                instructions = self.solver.gen_runtime_expression(relevant_tokens,
                    self.mem, result_var=identifier)
                asm.merge(instructions)

        # reference exists
        else:
            temp = Memory.gen_temp_name()
            #self.mem.add_reference(temp)

            if len(relevant_tokens) == 1 and relevant_tokens[0].value.isdigit():
                # one token that is an int value
                self.mem.add_reference(temp, relevant_tokens[0].value)
            elif len(relevant_tokens) == 1 and self.mem.has_reference(relevant_tokens[0].value):
                # one token that is an identifier
                self.mem.add_reference(temp, self.mem.get_reference(relevant_tokens[0].value))
            else:
                # several tokens, let's solve it
                self.mem.add_reference(temp)
                instructions = self.solver.gen_runtime_expression(relevant_tokens,
                    self.mem, result_var=temp)
                asm.merge(instructions)

            # the 'temp' variabel may be loaded in the
            # AC, but just to be sure we do it again.
            asm.add(Instruction("LDA", variable=temp, comment="variable 're-assignment'"))
            asm.add(Instruction("STA", variable=identifier))

        return asm


    def _handle_if(self, ex):
        # skip the identifier and the '=' char
        relevant_tokens = ex.tokens[2:len(ex.tokens)-1]

        asm = AsmExpressionContainer(ex)
        result_var = ""

        if len(relevant_tokens) == 1 and relevant_tokens[0].token == TokenType.Identifier \
                and not relevant_tokens[0].value.isdigit():
            # single token with a value, should be dynamic
            #print("IT'S AN IDENTIFIER")
            var_name = str(relevant_tokens[0].value)
            result_var = var_name
            #self.mem.add_reference(temp, self.mem.get_reference(relevant_tokens[0].value))
        else:
            temp = Memory.gen_temp_name()
            #val = int(self.solver.solve_expr(ex.tokens[2:len(ex.tokens)-1], self.mem, None))
            #ex.value = val
            #var_name = add_mem_ref(val)
            if len(relevant_tokens) == 1 and relevant_tokens[0].value.isdigit():
                # one token that is an int value
                self.mem.add_reference(temp, relevant_tokens[0].value)
            elif len(relevant_tokens) == 1 and self.mem.has_reference(relevant_tokens[0].value):
                # one token that is an identifier
                #self.mem.add_reference(temp, self.mem.get_reference(relevant_tokens[0].value))
                temp = relevant_tokens[0].value
            else:
                # several tokens, let's solve it
                self.mem.add_reference(temp)
                instructions = self.solver.gen_runtime_expression(relevant_tokens,
                    self.mem, result_var=temp)
                asm.merge(instructions)
            result_var = temp


        asm.load(result_var)
        #print("a.load(var_name); == " + var_name)
        jp_name = Memory.gen_jump_name()
        #asm.load(temp)
        asm.add(Instruction("BRZ", jump=jp_name, comment="jump if zero"))

        for e in ex.expressions:
            ae = self._handle_expr(e)
            if ae is not None:
                asm.asm_expressions.append(ae)

        for aa in asm.asm_expressions:
            instrs = aa.get_instructions()
            for i in instrs:
                asm.add(i)

        asm.add(JumpFlag(jp_name))

        return asm


    def _handle_func_call(self, ex):
        # TODO: function lookup table with arument count and such
        #       cause right now all we have is "print" and "read"

        identifier = str(ex.tokens[2].value)
        a = AsmExpressionContainer(ex)
        name = str(ex.tokens[0].value)

        if name == "print":
             # identifier is a constant
             # so we just print it
            if identifier.isdigit():
                temp = Memory.gen_temp_name()
                self.mem.add_reference(temp, identifier)
                a.load(temp)
                a.do_print()
            else:
                a.load(identifier)
                a.do_print()

        elif name == "read":
            a.do_read()

            if self.mem.has_reference(identifier):
                temp = Memory.gen_temp_name()
                self.mem.add_reference(temp)

                a.add(Instruction("STA", variable=temp, comment="store input"))
                a.add(Instruction("LDA", variable=temp, comment="variable 're-assignment'"))
                a.add(Instruction("STA", variable=identifier))
            else:
                print("im so done with this shit")

        return a


    def _handle_expr(self, ex):
        """
        evaluate an expression and generate assembly for it
        """
        # returns true or false
        def expr_matches(expr, tokens):
            if len(expr.tokens) < len(tokens): return False
            for idx, val in enumerate(tokens):
                if str(val) != str(expr.tokens[idx].token):
                    return False
            return True

        match_assignment = lambda x: expr_matches(x, [TokenType.Identifier, TokenType.Equals])
        match_condition = lambda x: expr_matches(x, [TokenType.Conditional, TokenType.LParen])
        match_func = lambda x: expr_matches(x, [TokenType.Function, TokenType.LParen])

         # VARIABLE ASSIGMENT
        if match_assignment(ex):
            asm = self._handle_assignment(ex)
            return asm

        elif match_condition(ex): # IF STATEMENT
            asm = self._handle_if(ex)
            return asm

        elif match_func(ex):
            asm = self._handle_func_call(ex)
            return asm

        return None


    def _bind_jumps(self, instructions):
        def find_jump(instructions, alias):
            for idx, instr in enumerate(instructions):
                if instr.is_jump_endpoint:
                    for j in instr.jumps:
                        if alias == j.alias:
                            return (idx, instr)
            return None

        for inst in instructions:
            if inst.invalidate_jump_bindings:
                need = inst.jump
                (line_idx, jump_inst) = find_jump(instructions, need)
                if line_idx is None:
                    print("Error: What the f-...this shouldnt happen...")
                inst.set_adr(line_idx)

        return instructions


    def _merge_jumps(self, instructions):
        copy = [i for i in instructions]
        skip = 0

        for idx, inst in enumerate(copy):
            jumps = []
            inc = 1
            if skip != 0:
                skip -= 1
                continue

            if isinstance(inst, JumpFlag):
                # with the way we create the instructions,
                # there will always be another Instruction
                # after a jump command.
                jumps.append(inst)

                nxt = copy[idx + inc]
                while isinstance(nxt, JumpFlag):
                    jumps.append(nxt)
                    inc += 1
                    skip += 1
                    nxt = copy[idx + inc]

                # next is now an Instruction (hopefully)
                if not isinstance(nxt, Instruction):
                    print("Error: Instance was not an Instruction")

                for jp in jumps:
                    nxt.add_jump(jp)

        # Delete all the JumpFlags from the copy list

        has_jumps = lambda lst: any([True for l in lst if isinstance(l, JumpFlag)])
        while has_jumps(copy):
            for idx, j in enumerate(copy):
                if isinstance(j, JumpFlag):
                    del copy[idx]
                    continue

        return copy


    def _parse(self, tokens):
        exprs = self._parse_expr_recursive(tokens)
        asm_list = [] # AsmExpression

        for ex in exprs:
            asm_expr = self._handle_expr(ex)

            if Utils.check_none_critical(asm_expr):
                Utils.debug("Compiler Error!: 'asm_expr' cannot be None.")

            asm_list.append(asm_expr)


        g = []
        mem_asm = self.mem.gen_asm()

        g.extend(mem_asm)
         # get the rest of the instructions
        for expr in asm_list:
            g.extend(expr.get_instructions())

        g.append(Instruction("HLT", comment="exit"))

        print("\nDebug preview:\n")
        for idx, gg in enumerate(g):
            print(str(idx) + ": " + str(gg))


        instructions = self._merge_jumps(g)

        instructions = self.mem.bind_mem(instructions)
        if instructions is None:
            print("Critical Error!: Memory bindings.")
            return None

        instructions = self._bind_jumps(instructions)
        if Utils.check_none_critical(instructions):
            print("Critical Error!: Jump bindings.")
            return None


        assembly = "\n".join([a.asm() for a in instructions])
        print("\nCompiled:\n")
        for idx, gg in enumerate(instructions):
            print(str(idx) + ": " + str(gg))

        return [], assembly
