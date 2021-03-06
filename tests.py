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

    def test_bra(self):
        asm = """BRA 2\nMEM 33333\nLDA 1\nOUT\nHLT"""
        output = self.assembler.load(asm)
        assert output[0] == "33333"

    def test_bra_error_missing_address(self):
        asm = """BRA\nMEM 88\nLDA 1\nOUT\nHLT"""
        with self.assertRaises(ParseError):
            output = self.assembler.load(asm)

    def test_brz(self):
        asm = """LDA 5\nBRZ 3\nLDA 6\nOUT\nHLT\nMEM 3\nMEM 5"""
        output = self.assembler.load(asm)
        assert output[0] == "5"

    def test_brp(self):
        # test if it jumps when the AC is 0
        asm = """LDA 5\nBRP 3\nLDA 6\nOUT\nHLT\nMEM 0\nMEM 5"""
        output = self.assembler.load(asm)
        assert output[0] == "5" # it should not jump

        # test with a positive integer
        asm = """LDA 5\nBRP 3\nLDA 6\nOUT\nHLT\nMEM 1\nMEM 5"""
        output = self.assembler.load(asm)
        assert output[0] == "1"

    def test_inp_out(self):
        asm = """INP\nOUT\nHLT"""
        output = self.assembler.load(asm)
        assert output[0] == "7"  # testing output is 7 by default

    def test_lda_sta(self):
        asm = """INP\nLDA 5\nOUT\nSTA 5\nHLT\nMEM 12"""
        self.assembler.load(asm)

    def test_lda_sta_error(self):
        asm = """INP\nLDA 120\nOUT\nSTA 333\nHLT\nMEM 12"""
        with self.assertRaises(ExecuteError):
            self.assembler.load(asm)

    def test_add_sub(self):
        asm = """
        BRA 3
        MEM 10
        MEM 5
        LDA 1
        ADD 2  # Add 5 to 10
        OUT
        LDA 1
        SUB 2  # Sub 5 from 10
        OUT
        HLT
        """
        output = self.assembler.load(asm)
        assert output[0] == "15" # add operation
        assert output[1] == "5"  # sub operation


class TestCompiler(unittest.TestCase):
    def setUp(self):
        self.compiler = compiler.ScriptCompiler(testing=True)

    def test_load_from_file(self):
        filename = os.path.abspath("programs/demo1.script")
        self.compiler.compile_from_file(filename)

    def test_load_from_string(self):
        script = """
        foo = 13;
        userInput = 0;
        print(foo);
        """
        self.compiler.compile(script)

    def test_simple_output(self):
        script = """
        foo = 13;
        print(foo);
        """
        output = self.compiler.compile(script)
        assert output[0] == "13"

    def test_comments(self):
        script = """
        # this is a comment
        foo = 13;#this is a comment
        print(foo);      #     more comments
        #commenttttt
        """
        output = self.compiler.compile(script)
        assert output[0] == "13"

    def test_simple_negative(self):
        script = """
        foo = -13 + - + 10; #10 +-13+ -10;
        print(foo);
        """
        output = self.compiler.compile(script)
        assert output[0] == "-23"

        script = """
        foo = -13 + - 10 + 1; #10 +-13+ -10;
        print(foo);
        """
        output = self.compiler.compile(script)
        assert output[0] == "-22"

    def test_variable_assignment(self):
        script = """
        bar = 10000000;
        test=0;tester =10;

        print(bar);
        print(test);
        print(tester);
        """
        output = self.compiler.compile(script)
        assert output[0] == "10000000"
        assert output[1] == "0"
        assert output[2] == "10"

if __name__ == "__main__":
    unittest.main()
