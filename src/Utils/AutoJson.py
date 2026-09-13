import json
from typing import List, Dict, Any


class AutoJson:
    @staticmethod
    def to_json(obj: List[Any] | Dict[Any, Any]) -> str:
        """Convert a list or dictionary to a JSON string."""
        if isinstance(obj, dict):
            return AutoJson.json_dict(obj)
        else:
            return AutoJson.json_list(obj)

    @staticmethod
    def json_dict(value: Dict[Any, Any],
                  indent: int = 0, text: str = "") -> str:
        "Load a json dict and returns it as a str"
        collevel: str = "\t" * indent
        textlevel: str = "\t" * (indent + 1)
        index: int = 0
        indent += 1
        text += f"{collevel}"+"{\n"
        for key in value:
            val = value.get(key)
            index += 1
            text += textlevel + f"{json.dumps(key)}: "
            if isinstance(val, (list, dict)):
                text += " "
                if isinstance(val, list):
                    text += AutoJson.json_list(val, indent)
                elif isinstance(val, dict):
                    text += AutoJson.json_dict(val, indent)
            else:
                text += json.dumps(val)
            if index < len(value):
                text += ","
            text += textlevel + "\n"
        text += f"{collevel}"+"}"
        return text

    @staticmethod
    def json_list(value: List[Any], indent: int = 0, text: str = "") -> str:
        "Load a json list and returns it as a str"
        collevel: str = "\t" * indent
        textlevel: str = "\t" * (indent + 1)
        indent += 1
        text += collevel + "[\n"
        for index in range(len(value)):
            val = value[index]
            if isinstance(val, (list, dict)):
                text += " "
                if isinstance(val, list):
                    text += AutoJson.json_list(val, indent)
                elif isinstance(val, dict):
                    text += AutoJson.json_dict(val, indent)
            else:
                text += textlevel + json.dumps(val)
            if index+1 < len(value):
                text += ","
            text += "\n"
        text += collevel + "]"
        return text

    @staticmethod
    def open_json(path: str) -> Any | None:
        """Return the value contained in a json file.\n
        Return None if an error occured."""
        try:
            with open(path, "r") as p:
                return json.load(p)
        except FileNotFoundError:
            return None
        except PermissionError:
            return None
        except IsADirectoryError:
            return None
        except json.decoder.JSONDecodeError:
            return None
