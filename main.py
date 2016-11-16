import argparse, sys, os
import compiler

if __name__ == "__main__":

	if len(sys.argv) < 2:
		print("Usage:\n\tmain.py <file>")
		sys.exit(1)

	debug = False
	if len(sys.argv) > 2:
		if sys.argv[2] == "--debug" or sys.argv[2] == "-d":
			debug = True

	ext = os.path.splitext(sys.argv[1])[1]

	try:
		if ext == ".man": # Compile assembly
			a = compiler.Assembler()
			a.run(sys.argv[1], read_from_file=True)

		elif ext == ".script": # Compile script
			s = compiler.ScriptCompiler()
			s.compile(sys.argv[1])

	except Exception as e:
		print("Error: {0}".format(str(e)))
