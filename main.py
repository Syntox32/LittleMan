import sys, os
import compiler

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Usage:\n\tmain.py <file>")
		sys.exit(1)

	ext = os.path.splitext(sys.argv[1])[1]

	if ext == ".man": # Compile assembly
		a = compiler.Assembler()
		a.run(sys.argv[1])
	elif ext == ".script": # Compile script
		s = compiler.ScriptCompiler()
		s.compile(sys.argv[1])
