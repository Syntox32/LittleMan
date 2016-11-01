from compiler.token import TokenType, SYMBOLS, KEYWORDS
from compiler.tokenizer import Token

class Stack:
    def __init__(self): self.items = []
    def push(self, item): self.items.append(item)
    def pop(self): return self.items.pop()
    def peek(self): return self.items[len(self.items)-1]
    def size(self): return len(self.items)


class Expression:
    def __init__(self, tokens=None, expressions=None):
        self.tokens = [] if tokens is None else tokens
        self.expressions = [] if expressions is None else expressions

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

    def _apply_shunting_yard(self, tokens, variables):
        output = []
        op = Stack()

        for t in tokens:
            v = t.value

            if t.token == TokenType.Function:
                output.append(t)

            elif t.token == TokenType.Identifier and t.value.isdigit():
                output.append(t)
            elif t.token == TokenType.Identifier: # token is a variable identifier
                # TODO: Find memory value before entering this Function
                #       just to remove the extra parameter?
                output.append(Token(variables[str(t.value)], t.token))

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