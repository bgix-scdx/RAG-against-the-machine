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
        

def Process_Arguments(allow_multiples: bool = False) -> Dict[str, Dict[str, Any]]:
    args = argv[1:len(argv)]

    Arguments: Dict[str, Dict[str, Any]] = {}

    index = 0
    for i in args:
        index += 1
        if not i[0] == '-' and not i in Arguments:
            val = Process_Options(index)
            print(i, val)
            if not val == []:
                if not allow_multiples and len(Arguments) > 0:
                    raise ArgumentError("Too many arguments.")
                Arguments[i] = val
    return Arguments

def Process_Options(index: int) -> Dict[str, List[Any] | Any]:
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
        return {}
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
                Value = wanted(target) #  TODO: Ignore this part.
                if not OptionValue:
                    OptionValue = Value
                elif not isinstance(OptionValue, list):
                    OptionValue = [OptionValue, Value]
                elif isinstance(OptionValue, list):
                    OptionValue += [Value]
            except ValueError:
                raise ArgumentError("Invalid Argument Type: "
                                    f"{wanted.__name__},"
                                    f" got {target.__class__.__name__}")
        OptionPosition += 1
        index += 1
    if OptionValue:
        if OptionName:
            Options[OptionName] = OptionValue
        else:
            Options["-unamed"] = OptionValue
    return Options