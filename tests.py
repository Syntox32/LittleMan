import unittest, os
import compiler
from compiler.error import *
from compiler.executor import Executor

class TestExecutor(unittest.TestCase):
    def setUp(self):
        self.exe = Executor(testing=True)

    def test_execute(self):
        self.exe.execute_bytecode([901, 902, 0])

    def test_execute_error(self):
        with self.assertRaises(ExecuteError):
            self.exe.execute_bytecode([901, 90233333, 0])

    def test_execute_missing_halt(self):
        with self.assertRaises(ExecuteError):
            self.exe.execute_bytecode([901, 902])

class TestAssembler(unittest.TestCase):
    def setUp(self):
        self.assembler = compiler.Assembler(testing=True)

    def test_loading_file(self):
        filename = os.path.abspath("programs/io.man")
        self.assembler.run(filename, read_from_file=True)

    def test_loading_from_string(self):
        asm = """INP\nOUT\nHLT"""
        self.assembler.load(asm)

    def test_parse_error(self):
        asm = """INP\nOUTTTT\nHLT"""
        with self.assertRaises(ParseError):
            self.assembler.load(asm)

    def test_interpret_error(self):
        asm = """INP\nLDA 2 2\nMEM 0\nHLT"""
        with self.assertRaises(ParseError):
            self.assembler.load(asm)

if __name__ == "__main__":
    unittest.main()
