from sys import argv
from typing import List, Dict, Any
from inspect import isclass
path = str
query = str
dir = str

ArgumentTarget = [
    ["index", "-max_chunk_size", int],
    ["search", query, "-k", int],
    ["search_dataset", "-dataset_path", path, "-k", int, "-save_directory", path],
    ["answer", query, "-k", int],
    ["answer_dataset", "-student_search_results_path", path, "-save_directory", dir],
    ["evaluate", "-student_search_results_path", path, "-dataset_path", path]
]

class ArgumentError(Exception):
    message: str

    def __init__(self, message: str = "Invalid Argment Passed"):
        self.message = message
        super().__init__(self.message)
        

def Process_Arguments(allow_multiples: bool = False) -> Dict[str, str | int]:
    args = argv[1:len(argv)]

    Arguments = {}

    index = 0
    for i in args:
        if not i[0] == '-' and not i in Arguments:
            index += 1
            val = Process_Options(index)
            print(i, val)
            if not val == []:
                Arguments[i] = val
    return Arguments

def Process_Options(index: int):
    args = argv[1:len(argv)]

    OptionPosition = 1
    CommandName = args[index - 1]
    CommandInfo = None
    Options = {}
    OptionName = None
    OptionValue = None

    for i in ArgumentTarget:
        if i[0] == CommandName:
            CommandInfo = i
            break
    if not CommandInfo:
        return []
    print(f"Trying ", CommandName) 

    while OptionPosition < len(CommandInfo):
        wanted = CommandInfo[OptionPosition]
        target = args[index]
        if not isclass(wanted) and target == wanted:
            if OptionValue:
                if OptionName:
                    Options[OptionName] = OptionValue
                else:
                    Options["-unamed"] = OptionValue
            OptionName = target
            OptionValue = None
        elif isclass(wanted):
            try:
                Value = wanted(target)
                if not OptionValue:
                    OptionValue = Value
                elif not isinstance(OptionValue, list):
                    OptionValue = [OptionValue, Value]
                else:
                    OptionValue += Value
            except:
                ArgumentError("Error")
        OptionPosition += 1
        index += 1
    if OptionValue:
        if OptionName:
            Options[OptionName] = OptionValue
        else:
            Options["-unamed"] = OptionValue
    return Options