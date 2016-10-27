# -*- coding: utf-8 -*-
import os
from compiler.executor import Executor
from compiler.tokenizer import Tokenizer, Token
from compiler.token import TokenType, SYMBOLS, KEYWORDS
from compiler.assemblybuilder import AssemblyBuilder
from compiler.assembler import Assembler


class Expression:
    def __init__(self, tokens=None, expressions=None):
        self.tokens = [] if tokens is None else tokens
        self.expressions = [] if expressions is None else expressions

class Stack:
    def __init__(self): self.items = []
    def push(self, item): self.items.append(item)
    def pop(self): return self.items.pop()
    def peek(self): return self.items[len(self.items)-1]
    def size(self): return len(self.items)

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

            #print("\nTokens:")
            #for t in self.tokens: print("   {0}\t\t{1}".format(str(t.value), str(t.token)))

            #with open(path, "r") as f:
            #	contents = f.read()

            #self.reader = StringReader(contents)

            #self.tokens = []

            # Do the actual compilation

            #self._tokenize()
            (exprs, asm) = self._parse(self.tokens)
            #print(asm)

            a = Assembler(mem_size=100)
            a.load(asm)

            with open("gen.man", "w") as f:
                f.write(asm)

            # Print out some debug values

            if exprs is not None:
                print("\nExpressions:")
                for idx, val in enumerate(exprs):
                    print("   {0}: {1}".format(str(idx)," ".join([str(t.value) for t in val.tokens])))

            #print("\nTokens:")
            #for t in self.tokens: print("   {0}\t\t{1}".format(str(t.value), str(t.token)))

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

        def precedence(token):
            if token.token == TokenType.Add or token.token == TokenType.Sub:
                return 1
            elif token.token == TokenType.Mul or token.token == TokenType.Div:
                return 2
            return 0

        def apply_shunting_yard(tokens):
            output = []
            op = Stack()

            for t in tokens:
                v = t.value

                if t.token == TokenType.Function:
                    output.append(t)

                elif t.token == TokenType.Identifier and t.value.isdigit():
                    output.append(t)
                elif t.token == TokenType.Identifier:
                    output.append(Token(var_mem[str(t.value)], t.token))

                elif t.token == TokenType.Seperator:
                    if op.size != 0:
                        while op.peek().token != TokenType.LParen:
                            output.append(op.pop())

                elif t.token == TokenType.Add or \
                        t.token == TokenType.Sub or \
                        t.token == TokenType.Mul or \
                        t.token == TokenType.Div:
                    if op.size() != 0:
                        while op.size() > 0 and precedence(t) <= precedence(op.peek()):
                                output.append(op.pop())
                    op.push(t)

                elif t.token == TokenType.LParen:
                    op.push(t)

                elif t.token == TokenType.RParen:
                    if op.size != 0:
                        while op.peek().token != TokenType.LParen:
                            output.append(op.pop())
                    op.pop() # Remove LParen from the stack, don't put into output
                    if op.size() != 0:
                        if op.peek().token == TokenType.Function:
                            output.append(op.pop())

                #print("Output: {0} \t Stack: {1}".format(
                #    ",".join([str(t.value) for t in output]),
                #    ",".join([str(t.value) for t in op.items]),
                #))

            while op.size() != 0:
                output.append(op.pop())

            #print("Output: {0} \t Stack: {1}".format(
            #    ",".join([str(t.value) for t in output]),
            #    ",".join([str(t.value) for t in op.items]),
            #))

            return output

        def is_operator(token):
            return token.token == TokenType.Add \
                        or token.token == TokenType.Sub \
                        or token.token == TokenType.Mul \
                        or token.token == TokenType.Div \

        def eval_operator(token, left, right):
            #print(str(left.value))
            #print(str(right.value))
            if token == TokenType.Add:
                return int(left.value) + int(right.value)
            elif token == TokenType.Sub:
                return int(left.value) - int(right.value)
            elif token == TokenType.Mul:
                return int(left.value) * int(right.value)
            elif token == TokenType.Div:
                return int(left.value) / int(right.value)

        def apply_rpn(token_list):
            stack = Stack()

            for t in token_list:
                if t.token == TokenType.Identifier:
                    stack.push(t)
                elif is_operator(t):
                    # take N arguments off the stack
                    # TODO: Expand to include functions
                    var2 = stack.pop()
                    var1 = stack.pop()
                    res = eval_operator(t.token, var1, var2)
                    stack.push(Token(res, TokenType.Identifier))
                else:
                    print("ERROR: " + token.value)
            if stack.size() == 1:
                return stack.pop()
            else:
                print("ERROR: Something shitty happend.")


        # e.g.: var = ...
        match_assignment = lambda x: expr_matches(x, [TokenType.Identifier, TokenType.Equals])

        # POC first try at evaluating expressions
        def eval_expr(tokens):
            print(" ".join([str(t.value) for t in tokens]))
            rpn_notation = apply_shunting_yard(tokens)
            result = apply_rpn(rpn_notation).value
            print("RESULT: " + str(result))
            return result

        for ex in exprs:
            print("debug: {0}".format(" ".join([str(t.value) for t in ex.tokens])))

            if match_assignment(ex):
                var_name = str(ex.tokens[0].value)
                val = int(eval_expr(ex.tokens[2:]))
                var_mem[var_name] = val
                ASM.add_mem(var_name, val)
                print("match_assignment == True\n")

            if is_func_call(ex):
                print("\tassuming function call")
                parse_func_call(ex)


        assembly = ASM.build()
        ASM.debug_print()
        return exprs, assembly
