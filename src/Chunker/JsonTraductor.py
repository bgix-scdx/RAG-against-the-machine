from ..DataModels.DataModel import MinimalSource
from typing import List, Dict, Any
from io import TextIOWrapper
from json import dumps


class JsonTraductor():
    """ Create a json from a list of MinimalSources """

    @staticmethod
    def write(file, lst: List[MinimalSource]) -> None:
        """ Write inside the file. """
        sort: Dict[str, Dict[str, int | str]] = {}
        for i in lst:
            print(i)
            if not sort.get(i.file_path):
                sort[i.file_path] = []
            text: str = ""
            with open(i.file_path, "r") as f:
                text = f.read()[i.first_character_index:
                                i.last_character_index]
            result = {
                "start": i.first_character_index,
                "end": i.last_character_index,
                "text": text
            }
            sort.get(i.file_path).append(result)
        JsonTraductor.unpack_dict(sort, file)

    @staticmethod
    def unpack_dict(value: dict[Any, Any], file: TextIOWrapper,
                    indent: int = 0) -> None:
        indentlevel = "\t" * indent
        file.write(f"{indentlevel}"+"{\n")
        for key, val in value.items():
            originkey = key
            if (isinstance(val, str) and JsonTraductor.checkdec(val)):
                if '.' in val:
                    val = float(val)
                else:
                    val = int(val)
            if (isinstance(key, str) and JsonTraductor.checkdec(key)):
                if '.' in key:
                    key = float(key)
                else:
                    key = int(key)
            if isinstance(val, dict) and len(val) > 0:
                file.write(f"{indentlevel}{dumps(str(key))}:\n")
                JsonTraductor.unpack_dict(val, file, indent + 1)
            elif isinstance(val, dict) and len(val) == 0:
                file.write(f"{indentlevel}\"{key}\": {{}}")
            elif isinstance(val, list) and len(val) > 0:
                file.write(f"{indentlevel}\"{key}\":\n")
                JsonTraductor.unpack_list(val, file, indent + 1)
            else:
                file.write(f"{indentlevel}{dumps(key)}: {dumps(val)}")
            if originkey != list(value.keys())[-1]:
                file.write(",")
            file.write("\n")
        file.write(f"{indentlevel}"+"}")

    @staticmethod
    def unpack_list(value: list[Any], file: TextIOWrapper,
                    indent: int = 0) -> None:
        indentlevel = "\t" * indent
        file.write(f"{indentlevel}[\n")
        for i, val in enumerate(value):
            if (isinstance(val, str) and JsonTraductor.checkdec(val)):
                if '.' in val:
                    val = float(val)
                else:
                    val = int(val)
            if isinstance(val, dict) and len(val) > 0:
                JsonTraductor.unpack_dict(val, file, indent + 1)
            elif isinstance(val, dict) and len(val) == 0:
                file.write(f"{indentlevel}{{}}")
            elif isinstance(val, list) and len(val) > 0:
                JsonTraductor.unpack_list(val, file, indent + 1)
            else:
                file.write(f"{indentlevel}{dumps(val)}")
            if i != len(value) - 1:
                file.write(",")
            file.write("\n")
        file.write(f"{indentlevel}]")

    @staticmethod
    def checkdec(val: str) -> bool:
        if not isinstance(val, str):
            return False
        tostr = ""
        for i in val:
            if i not in ".-":
                tostr = tostr + i
        try:
            print(tostr)
            float(tostr)
            return True
        except ValueError:
            return False