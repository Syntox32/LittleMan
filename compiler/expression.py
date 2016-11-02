import random
from compiler.token import TokenType, SYMBOLS, KEYWORDS
from compiler.tokenizer import Token
from compiler.instruction import Instruction, AsmExpressionContainer, JumpFlag

class Stack:
    def __init__(self): self.items = []
    def push(self, item): self.items.append(item)
    def pop(self): return self.items.pop()
    def peek(self): return self.items[len(self.items)-1]
    def size(self): return len(self.items)


class Expression:
    def __init__(self, tokens=None, expressions=None, value=0):
        self.tokens = [] if tokens is None else tokens
        self.expressions = [] if expressions is None else expressions
        self.value = 0

    def __str__(self):
        if len(self.tokens) == 0: return "empty"
        return " ".join([str(t.value) for t in self.tokens])


class ExpressionSolver:
    def solve_expr(self, tokens, variables, functions=None):
        #tokens = expression.tokens
        #print("eval expression: " + str(expression)) # debug
        print("eval expression: " + " ".join([str(t.value) for t in tokens]))

        rpn_notation = self._apply_shunting_yard(tokens, variables)
        result_token = self._apply_rpn(rpn_notation)

        if result_token is not None:
            print("eval result: " + str(result_token.value)) # debug
            return result_token.value
        else:
            print("eval result: error") # debug
            return None

    def gen_runtime_expression(self, tokens, memory, functions=None, *, result_var=None):
        rpn_notation = self._apply_shunting_yard(tokens, None, substitute_vars=False)
        memory = {}

        def get_name(static_object=[]):
            if len(static_object) == 0: static_object.append(random.randint(1000, 9999))
            s = str(static_object[0])
            static_object[0] = static_object[0] + 1
            return s

        def add_mem_ref(memory, value, name=None):
            ref_name = name if name is not None else get_name() #str(len(memory) + 1)
            #print("ref_name: " + ref_name)
            memory.update({ref_name: {"value":value, "line": -1}})
            return ref_name

        stack = Stack()
        asm = AsmExpressionContainer(tokens)

        print("rpn_notation: " + str([str(t.value) for t in rpn_notation]))
        #def _gen_add(token_right, token_left): pass

        temp = add_mem_ref(memory, 0, "temp_" + get_name())

        for t in rpn_notation:
            if t.token == TokenType.Identifier:
                stack.push(t)
            elif self._is_operator(t):
                # take N arguments off the stack
                # TODO: Expand to include functions
                var2 = stack.pop()
                var1 = stack.pop()

                if var1.value.isdigit(): #var1.token == TokenType.IntValue:
                    var1_name = add_mem_ref(memory, var1.value)
                else:
                    var1_name = var1.value

                if var2.value.isdigit(): #.token == TokenType.IntValue:
                    var2_name = add_mem_ref(memory, var2.value)
                else:
                    var2_name = var2.value

                if t.token == TokenType.Add:
                    asm.load(var1_name)
                    #asm.append(Instruction("LDA", variable=var1_name))
                    asm.add(Instruction("ADD", variable=var2_name))
                    #asm.append(Instruction("STA", variable=temp))
                    asm.store(temp)
                elif t.token == TokenType.Sub:
                    asm.load(var1_name)
                    #asm.append(Instruction("LDA", variable=var1_name))
                    asm.add(Instruction("SUB", variable=var2_name))
                    #asm.append(Instruction("STA", variable=temp))
                    asm.store(temp)

                #asm.load(temp)
                #asm.store(result_var)

                stack.push(Token(temp, TokenType.Identifier))

                #res = self._eval_operator(t.token, var1, var2)
                #stack.push(Token(res, TokenType.Identifier))
            else:
                print("ERROR: " + token.value)

        asm.load(temp)
        asm.store(result_var)

        #if stack.size() == 1:
            # return object is of type 'Token'
        #    return stack.pop() # success
        #else:
        #    print("ERROR: Something bad happend.")

        return (memory, asm)


    def _apply_rpn(self, token_list):
        stack = Stack()

        for t in token_list:
            if t.token == TokenType.Identifier:
                stack.push(t)
            elif self._is_operator(t):
                # take N arguments off the stack
                # TODO: Expand to include functions
                var2 = stack.pop()
                var1 = stack.pop()
                res = self._eval_operator(t.token, var1, var2)
                stack.push(Token(res, TokenType.Identifier))
            else:
                print("ERROR: " + token.value)

        if stack.size() == 1:
            # return object is of type 'Token'
            return stack.pop() # success
        else:
            print("ERROR: Something bad happend.")

        return None # default, should cause error

    def _apply_shunting_yard(self, tokens, variables, substitute_vars=True):
        output = []
        op = Stack()

        for t in tokens:
            v = t.value

            if t.token == TokenType.Function:
                output.append(t)

            elif t.token == TokenType.Identifier and t.value.isdigit():
                temp = t
                temp.token == TokenType.IntValue
                output.append(temp)
            elif t.token == TokenType.Identifier: # token is a variable identifier
                # TODO: Find memory value before entering this Function
                #       just to remove the extra parameter?
                if substitute_vars:
                    temp = t
                    temp.token == TokenType.IntValue
                    output.append(Token(variables[str(t.value)]["value"], t.token))
                else:
                    temp = t
                    temp.token == TokenType.Identifier
                    output.append(temp)

            elif t.token == TokenType.Seperator:
                if op.size != 0:
                    while op.peek().token != TokenType.LParen:
                        output.append(op.pop())

            elif t.token == TokenType.Add or \
                    t.token == TokenType.Sub or \
                    t.token == TokenType.Mul or \
                    t.token == TokenType.Div:
                if op.size() != 0:
                    while op.size() > 0 and self._precedence(t) <= self._precedence(op.peek()):
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

            #self._debug_print(output, op) # debug

        while op.size() != 0:
            output.append(op.pop())

        #self._debug_print(output, op) # debug

        return output

    def _precedence(self, token):
        if token.token == TokenType.Add or token.token == TokenType.Sub:
            return 1
        elif token.token == TokenType.Mul or token.token == TokenType.Div:
            return 2
        return 0

    def _is_operator(self, token):
        return token.token == TokenType.Add \
                    or token.token == TokenType.Sub \
                    or token.token == TokenType.Mul \
                    or token.token == TokenType.Div \

    def _eval_operator(self, token, left, right):
        if token == TokenType.Add:
            return int(left.value) + int(right.value)
        elif token == TokenType.Sub:
            return int(left.value) - int(right.value)
        elif token == TokenType.Mul:
            return int(left.value) * int(right.value)
        elif token == TokenType.Div:
            return int(left.value) / int(right.value)

    def _debug_print(self, output, op_stack):
        print("Output: {0} \t Stack: {1}".format(
            ",".join([str(t.value) for t in output]),
            ",".join([str(t.value) for t in op_stack.items])))
