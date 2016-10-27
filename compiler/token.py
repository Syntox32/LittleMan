from enum import Enum, IntEnum

class TokenType(IntEnum):
	IntValue = 0
	Function = 2
	LParen = 3
	RParen = 4
	Equals   = 5 # =
	EqualTo = 6 # ==
	If = 7
	While = 8
	Var = 9
	Identifier = 10
	Print = 11
	Read = 12
	SemiColon = 13
	Add = 14
	Sub = 15
	Mul = 16
	Div = 17
	FuncStart = 18
	FuncEnd = 19
	Colon = 20
	Comment = 21
	Period = 22
	Seperator = 23
	Conditional = 24
	FuncDecl = 25

SYMBOLS = {
	"(": TokenType.LParen,
	")": TokenType.RParen,
	"+": TokenType.Add,
	"-": TokenType.Sub,
	"*": TokenType.Mul,
	"/": TokenType.Div,

	"{": TokenType.FuncStart,
	"}": TokenType.FuncEnd,
	".": TokenType.Period,
	",": TokenType.Seperator,
	";": TokenType.SemiColon,
	":": TokenType.Colon,
	"=": TokenType.Equals,
	"#": TokenType.Comment

	#"var": Token.Var,
	#"if": Token.If,
	#"while": Token.While,
	#"def": Token.Function
}

KEYWORDS = {
	"if": TokenType.Conditional,
	"while": TokenType.While,
	"def": TokenType.FuncDecl,
	"print": TokenType.Function,
	"read": TokenType.Function,
    "sin": TokenType.Function,
    "min": TokenType.Function,
    "max": TokenType.Function,
    "testFunc": TokenType.Function
}
