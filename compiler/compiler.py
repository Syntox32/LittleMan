# -*- coding: utf-8 -*-
import os
from compiler.executor import Executor
from compiler.tokenizer import Tokenizer, Token
from compiler.token import TokenType, SYMBOLS, KEYWORDS
from compiler.assemblybuilder import AssemblyBuilder
from compiler.assembler import Assembler
from compiler.expression import Stack, Expression, ExpressionSolver


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
                self._print_expr_tree(curr.expressions, prefix + "  ")
            if idx + 1 < len(exprs):
                idx += 1
                curr = exprs[idx]
            else:
                curr = None


    def _parse(self, tokens):
        exprs = [] # list of ScriptAsmExpressions
        assembly = ""
        var_mem = {}
        in_block = False
        ASM = AssemblyBuilder()
        es = ExpressionSolver()

        idx = 0
        temp = 0
        level = 0
        temp = []
        block_expr = Expression()
        expr_stack = Stack()

        # helper functions
        peek = lambda: tokens[idx + 1]
        can_peek = lambda: idx + 1 < len(tokens)

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

        self._print_expr_tree(exprs)

        # returns true or false
        def expr_matches(expr, tokens):
            if len(expr.tokens) < len(tokens): return False
            for idx, val in enumerate(tokens):
                if str(val) != str(expr.tokens[idx].token):
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

        def parse_func_call(ex):
            if str(ex.tokens[0].value) == "print":
                var_name = str(ex.tokens[2].value)
                ASM.do_print(var_name)

            elif str(ex.tokens[0].value) == "read":
                var_name = str(ex.tokens[2].value)
                ASM.do_read(var_name)




        # e.g.: var = ...
        match_assignment = lambda x: expr_matches(x, [TokenType.Identifier, TokenType.Equals])

        for ex in exprs:
            print("debug: {0}".format(" ".join([str(t.value) for t in ex.tokens])))

            if match_assignment(ex):
                var_name = str(ex.tokens[0].value)

                # skip the identifier and the '=' char
                val = int(es.solve_expr(ex.tokens[2:], var_mem, None))

                var_mem[var_name] = val
                ASM.add_mem(var_name, val)
                print("match_assignment == True\n")

            if is_func_call(ex):
                print("\tassuming function call")
                parse_func_call(ex)


        assembly = ASM.build()
        ASM.debug_print()
        return exprs, assembly
