class PermChecker:
    @staticmethod
    def CanOpenFile(path: str) -> bool:
        """Used to Validate if the file is a valid file to be chunked.\n
        Returns True if it is valid, False otherwise."""
        try:
            with open(path, "r"):
                pass
        except FileNotFoundError:
            return False
        except PermissionError:
            return False
        except IsADirectoryError:
            return False
        return True
