import sys, os
import compiler

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Usage:\n\tmain.py <file>")
		sys.exit(1)

	ext = os.path.splitext(sys.argv[1])[1]

	if ext == ".man": # Compile assembly
		#a = compiler.Assembler()
		#a.run(sys.argv[1], read_from_file=True)
		d = compiler.Debugger()
		d.load_assembler_from_file(sys.argv[1])
		#d.display()
		d.next()
	elif ext == ".script": # Compile script
		s = compiler.ScriptCompiler()
		s.compile(sys.argv[1])
