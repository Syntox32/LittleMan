# -*- coding: utf-8 -*-
import os
from compiler.executor import Executor
from compiler.tokenizer import Tokenizer, Token
from compiler.token import TokenType, SYMBOLS, KEYWORDS
from compiler.assembler import Assembler
from compiler.expression import Stack, Expression, ExpressionSolver
from compiler.instruction import Instruction, AsmExpressionContainer, JumpFlag

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
            (exprs, asm) = self._parse(self.tokens)

            a = Assembler(mem_size=100)
            a.load(asm)

            # write generated assembly to file
            # with open("gen.man", "w") as f: f.write(asm)

            # Print out some debug values
            if exprs is not None:
                print("\nExpressions:")
                for idx, val in enumerate(exprs):
                    print("   {0}: {1}".format(str(idx)," ".join([str(t.value) for t in val.tokens])))

            #print("\nTokens:")
            #for t in self.tokens: print("   {0}\t\t{1}".format(str(t.value), str(t.token)))
        else: # unknown extension
            print("I don't recognize that extension: \'{0}\'".format(ext))

    def _print_expr_tree(self, exprs, prefix=""):
        if len(exprs) == 0: return
        # recursivly print expression
        #for e in exprs:
        #    print("\t" + str(e))
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


    def _parse(self, tokens):
        assembly = ""
        var_mem = {}
        es = ExpressionSolver()

        exprs = self._parse_expr_recursive(tokens)
        #global glb_increment_counter = 0

        def get_name(lol=[]):
            if len(lol) == 0: lol.append(0)
            s = str(lol[0])
            lol[0] = lol[0] + 1
            return s

        # returns true or false
        def expr_matches(expr, tokens):
            if len(expr.tokens) < len(tokens): return False
            for idx, val in enumerate(tokens):
                if str(val) != str(expr.tokens[idx].token):
                    return False
            return True

        # e.g.: var = ...
        match_assignment = lambda x: expr_matches(x, [TokenType.Identifier, TokenType.Equals])
        match_condition = lambda x: expr_matches(x, [TokenType.Conditional, TokenType.LParen])
        match_func = lambda x: expr_matches(x, [TokenType.Function, TokenType.LParen])

        stack = Stack()
        asm_list = [] # AsmExpression

        memory = {}
        line_count = 0

        def add_mem_ref(value, name=None):
            ref_name = name if name is not None else get_name() #str(len(memory) + 1)
            #print("ref_name: " + ref_name)
            memory.update({ref_name: {"value":value, "line": -1}})
            return ref_name

        def check_mem_exists(name):
            return name in memory

        # recursivly invalidte all the memory
        # I hope this is a good idea
        def invalidate(a_expr, mem):
            if a_expr.invalidate_vars:
                a_expr.invalidate_mem(mem)
            if a_expr.asm_expressions is not None:
                for aa in a_expr.asm_expressions:
                    invalidate(aa, mem)

        # now gen the rest of the assembly
        def get_asm(a_expr, *, dry=False):
            instr_list = []
            b = a_expr.build()
            #if not dry:
            #    line_count += len(b)
            instr_list.extend(b)
            print(instr_list)

            if a_expr.asm_expressions is not None:
                for aa in a_expr.asm_expressions:
                    instr_list.extend(get_asm(aa))
                    #print(instr_list)
            return instr_list

        def handle_expr(ex):
            """
            evaluate expression and generate assembly for it
            """
            if match_assignment(ex): # VARIABLE ASSIGMENT
                var_name = str(ex.tokens[0].value)
                result_variable = ""
                #fix_mem = False
                #if check_mem_exists(var_name):
                temp_name = get_name() # get new temp place for the result to stay
                add_mem_ref(0, temp_name)
                result_variable = temp_name
                fix_mem = True

                if not check_mem_exists(var_name):
                    add_mem_ref(0, var_name)
                    #fix_mem = True
                    #fix_mem = True
                #else:
                #    add_mem_ref(0, var_name)
                #    result_variable = var_name

                # skip the identifier and the '=' char
                relevant_tokens = ex.tokens[2:]

                asm = None
                expr = False
                if len(relevant_tokens) == 1:
                    temp_var_name = get_name()
                    add_mem_ref(relevant_tokens[0].value, temp_var_name)
                    temp_name = temp_var_name
                else:
                    (mem, asm) = es.gen_runtime_expression(relevant_tokens, memory, None, result_var=result_variable)
                    for e in asm.get_instructions(): print("\t{0}".format(str(e))) # debug

                    # The runtime expression generates it's own memory,
                    # so we have to add this to our "global" memory.
                    for m in mem: memory.update({m: mem[m]})
                    expr = True


                # TODO: Check if the expression only contains constant values
                #       then we use this method instead.
                #val = int(es.solve_expr(ex.tokens[2:], memory, None))
                #print("value: " + str(val))

                def fix_reassignment():
                    pass

                # skip the identifier and the '=' char
                #relevant_tokens = ex.tokens[2:]
                #(mem, asm) = es.gen_runtime_expression(relevant_tokens, memory, None, result_var=var_name)
                #for e in asm.get_instructions(): print("\t{0}".format(str(e)))
                #for m in mem: memory.update({m: mem[m]})

                a = AsmExpressionContainer(ex)
                if expr:
                    for inst in asm.get_instructions():
                        a.add(inst)

                if fix_mem:
                    a.add(Instruction("LDA", variable=temp_name, comment="variable 're-assignment'"))
                    a.add(Instruction("STA", variable=var_name))

                return a

                #return None # don't generate memory ASM from

            elif match_condition(ex): # IF STATEMENT
                # skip the identifier and the '=' char
                tokens = ex.tokens[2:len(ex.tokens)-1]
                if len(tokens) == 1 and tokens[0].token == TokenType.Identifier \
                        and not tokens[0].value.isdigit():
                    # single token with a value, should be dynamic
                    print("IT'S AN IDENTIFIER")
                    var_name = str(tokens[0].value)
                    #if var_name in memory:
                    #    print("lolshit")
                else:
                    val = int(es.solve_expr(ex.tokens[2:len(ex.tokens)-1], memory, None))
                    ex.value = val
                    var_name = add_mem_ref(val)

                a = AsmExpressionContainer(ex)

                a.load(var_name)
                print("a.load(var_name); == " + var_name)
                jp_name = get_name()
                a.add(Instruction("BRZ", jump=jp_name, comment="jump if zero"))
                #old_count = line_count
                #print("old count: " + str(old_count))

                for e in ex.expressions:
                    ae = handle_expr(e)
                    if ae is not None:
                        a.asm_expressions.append(ae)

                for aa in a.asm_expressions:
                    instrs = aa.get_instructions()
                    for i in instrs:
                        a.add(i)

                a.add(JumpFlag(jp_name))

                #print("WHAT TEH FUCK: " + str(get_asm(a, dry=True)))
                #ops_after = len(get_asm(a, dry=True))

                #a.jump_if_zero(ops_after + 1)
                #a.add("BRZ 40")

                return a

            elif match_func(ex): # FUNCTION CALL
                # TODO: function lookup table with arument count and such
                #       cause right now all we have is "print" and "read"

                var_name = str(ex.tokens[2].value)
                a = AsmExpressionContainer(ex)
                #print("CAUSE LOL WTF :" + str(a.asm))
                #print("EXPRESSION    :" + str(ex))

                if str(ex.tokens[0].value) == "print":
                    if var_name.isdigit():
                        temp_name = add_mem_ref(var_name)
                        a.load(temp_name)
                        a.do_print()
                    else:
                        #val = memory[var_name]["value"]
                        #temp_name = add_mem_ref(val)
                        #a.load(temp_name)
                        #
                        a.load(var_name)
                        a.do_print()
                        #a.add("OUT")
                    #ASM.do_print(var_name)
                elif str(ex.tokens[0].value) == "read":
                    #a.add("INP")
                    #a.do_read()
                    a.add(Instruction("INP", comment="read"))

                    if check_mem_exists(var_name):
                        temp_name = get_name()
                        print("INP temp name: *** " + temp_name)
                        add_mem_ref(0, temp_name)
                        a.add(Instruction("STA", variable=temp_name, comment="store input"))
                        a.add(Instruction("LDA", variable=temp_name, comment="variable 're-assignment'"))
                        a.add(Instruction("STA", variable=var_name))
                    else:
                        print("im so done with this shit")
                        #a.store(var_name)
                    #ASM.do_read(var_name)

                return a

            return None

        #print(asm_list)

        idx = 0
        while idx < len(exprs):
            ex = exprs[idx]

            a_expr = handle_expr(ex)
            if a_expr is not None:
                #print("WHAAA: " + str(ex))
                asm_list.append(a_expr)
                #print("lolSHITIII :" + str([str(a) for a in asm_list]))

            idx += 1
            if idx >= len(exprs):
                break

        def gen_mem(memory):
            jf_name = get_name()
            o = [Instruction("BRA", jump=jf_name, comment="jump over memory")] # adr=(len(memory) + 1)
            for m in memory:
                o.append(Instruction("MEM", adr=(memory[m]["value"]),
                                alias=m, comment="<{0}>".format(m)))
            o.append(JumpFlag(jf_name))
            return o

        #jump_table = {}
        def merge_jumps(instructions):
            copy = [i for i in instructions]
            skip = 0
            for idx, inst in enumerate(copy):
                #print("index: " + str(idx))
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
                        #remove.append(idx)
                        inc += 1
                        skip += 1
                        nxt = copy[idx + inc]

                    # next is now an Instruction (hopefully)
                    if not isinstance(nxt, Instruction):
                        print("Error: Instance was not an Instruction")

                    for jp in jumps:
                        nxt.add_jump(jp)
                    #print("jumps: " + str([j.alias for j in jumps]))

            def has_jumps(inst_list):
                for l in inst_list:
                    if isinstance(l, JumpFlag):
                        return True
                return False

            while has_jumps(copy):
                for idx, j in enumerate(copy):
                    if isinstance(j, JumpFlag):
                        del copy[idx]
                        continue

            return copy

        def bind_mem(instructions):
            def find_alias(instructions, alias):
                for idx, instr in enumerate(instructions):
                    if instr.alias == alias:
                        return (idx, instr)
                return None

            for inst in instructions:
                if inst.invalidate_binding:
                    # find memory with name "inst.variable"
                    need = inst.variable
                    print("need: " + need)
                    (line_idx, mem_inst) = find_alias(instructions, need)
                    if line_idx is None:
                        print("Error: What the f-...this shouldnt happen...")
                    print("\tline found: " + str(line_idx))
                    inst.set_adr(line_idx)

            return instructions


        def bind_jumps(instructions):
            def find_jump(instructions, alias):
                for idx, instr in enumerate(instructions):
                    if instr.is_jump_endpoint:
                        #print("JUMPS: " + str(instr.jumps))
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

        def gen_assembly():
            g = []
            mem_asm = gen_mem(memory)

            for ma in mem_asm: # add memory table instructions
                g.append(ma)

            for expr in asm_list: # get the rest of the instructions
                g.extend(expr.get_instructions())

            g.append(Instruction("HLT", comment="exit"))

            print("\nDebug preview:\n")
            for idx, gg in enumerate(g):
                print(str(idx) + ": " + str(gg))

            instructions = merge_jumps(g)
            instructions = bind_mem(instructions)
            instructions = bind_jumps(instructions)

            return instructions

        assembly_instructions = gen_assembly()
        assembly = "\n".join([a.asm() for a in assembly_instructions])
        print("\nCompiled:\n")
        for idx, gg in enumerate(assembly_instructions):
            print(str(idx) + ": " + str(gg))

        #assembly = "\n".join([a.asm() for a in gen_assembly()])
        return [], assembly #exprs, assembly
