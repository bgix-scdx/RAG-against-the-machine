from .Threader.ThreadService import ThreadManager

def Loop():
    while True:
        pass

if __name__ == "__main__":
    TM = ThreadManager()
    TM.Start(Loop)
    TM.Shutdown()
