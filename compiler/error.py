
class ExtensionError(Exception):
    pass

class ExecuteError(Exception):
    pass

class AssemblerError(Exception):
    pass

class ParseError(AssemblerError):
    pass
