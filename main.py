import sys
from compiler import Assembler

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Usage:\n\tmain.py <file>")
		sys.exit(1)

	a = Assembler()
	a.run(sys.argv[1])