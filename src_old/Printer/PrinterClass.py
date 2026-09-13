class Printer:
    @staticmethod
    def FullCol(col: str, text: str, ending: str = "\033[0m") -> None:
        print(f"{col}{text}{ending}")

    @staticmethod
    def Error(text: str) -> None:
        print(f"\033[38;2;255m{text}\033[0m")

    @staticmethod
    def Warn(text: str) -> None:
        print(f"\033[38;2;255;255m{text}\033[0m")
