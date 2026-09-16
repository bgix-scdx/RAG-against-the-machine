from ..Utils.Decorators import service
from threading import Thread, current_thread, Lock, Event
from typing import List, Any, Callable
from .ThreadInstance import ThreadInstance

@service
class ThreadManager:
    _instance: None | Any = None
    _initialized: bool = False
    _threads: List[Thread] = []
    _lock = Lock()
    _shutdown_event = Event()

    def __init__(self) -> None:
        if not hasattr(self, "_initialized"):
            self._initialized = True

    def Start(self, func: Callable, *arg: Any, **kwarg: Any) -> Thread:

        def wrapper() -> None:
            currentThread = current_thread()
            try:
                ThreadInstance(func, *arg, **kwarg)
            finally:
                with self._lock:
                    self._threads.remove(currentThread)
        newthread: Thread = Thread(target=wrapper)
        self._threads.append(newthread)
        newthread.start()
        return newthread

    def Shutdown(self, wait: bool = True,
                 timeout: float | None = None) -> None:
        self._shutdown_event.set()
        print("was set")
        for thread in self._threads:
            thread.join()
