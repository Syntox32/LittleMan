import inspect

class Utils:
    DebugPrint = True

    @staticmethod
    def debug(string):
        if Utils.DebugPrint:
            #name =  inspect.stack()[0][3]
            name = inspect.currentframe().f_back.f_code.co_name # caller func name
            print("dbg::\'{0}\'::  {1}".format(name, string))

    @staticmethod
    def check_none_critical(obj):
        if obj is None:
            name = inspect.currentframe().f_back.f_code.co_name # caller func name
            print("dbg::\'{0}\'::  {1}".format(name, "Critical!: Object was None."))
            return True
        return False
