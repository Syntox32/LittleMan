# Little Man Compiler & Assembler

This projects implements a Little Man Computer assembler and a high-level programming language compiler.

This was written for fun as an educational exercise, to understand a bit more of how a computer
interprets rudimentary instructions, and how compilers are built.

## Usage

`python3 main.py <file>`

Script files need the `.script` extension.

If you want to run assembler written by hand, use the `.man` extension.

## Assembler language

All the Little Man instructions are implemented and working.  

See: `compiler/assembler.py` and `compiler/executor.py` for the implementation.

Example:
```
LDA 6   # do '1 + 5'
ADD 5
OUT     # should print '6'
HLT
MEM 1   # give mem an initial value of '1'
MEM 5
```

## Scripting language

These things are sort of working:
  1. Variable assigmnent and re-assignment.
  3. Can evaluate expressions with the `+` and `-` operator. e.g.: `bar = foo + 3;`
  4. `if` can evaluate `0` to "false" and all positive integers to "true".
  5. Printing of variables.
  6. Reading into variables.
  7. Nested if- and block-statements.
  8. Comments and inline-comments.

Example:
```python
#
# Name: demo1.script
# Summary: Read one variable, then sum it with a constant.
#

foo = 13;
userInput = 0;

print(foo);			# print variables
print(userInput);

read(userInput);    # read input

foo = foo + userInput;
print(foo);

print(foo);
```

```python
#
# Name: demo2.script
# Summary: Read user input. If true then print some number.
#

foo = 42;
userInput = 0;

read(userInput);    # read input

if (userInput) {
	var = 123;
	print(var);
}
```
## Requirements

A working version of Python 3.4+ is required.
