# Little Man Compiler & Assembler

## Usage

`python3 main.py programs/bool.script`

The script need the `.script` extension

## Assembler language

All the Little Man instructions are implemented and working.  

See: `compiler/assembler.py` and `compiler/executor.py` for the implementation.

Example:
```
MEM 1   # give mem an initial value of '1'
MEM 5
LDA 1   # do '1 + 5'
ADD 0
OUT     # should print '6'
HLT
```

## Scripting language

These things are sort of working:
	- Variable assigmnent (but re-assignment is not working at the moment..).
	- Constant expressions can be evaluated.
	- "Runtime" expressions work with the `+` and `-` operator. e.g.: `bar = foo + 3;`
	- `if` statements are working with booleans, so `1` is `true`, this means the if-statement will excecute.
	- Printing of variables.
	- Reading into variables.
	- Nested if- and block-statements are working.
	- Comments and inline-comments are working.

Example:
```python
foo = 240;

constant = 2 * 10 * (4 + 10 * (2 + 1));   # constant expression evaluation
print(constant);

bar = 0
read(bar);
print(bar);

if (bar) {
    print(123);
    baz = foo + bar;
    print(baz);

    test1 = 0;
    read(test1);

    if (test1) {
        print(999999);
    }
}

print(foo);
```

## Requirements

A working version of Python 3.4+ is required.
