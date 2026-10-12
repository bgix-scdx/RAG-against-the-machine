from ..Utils.Decorators import service
from threading import Thread, current_thread, Lock, Event
from typing import List, Any, Callable
from .ThreadInstance import ThreadInstance


@service
class ThreadManager:
    """
    A service allowing to start and use separate threads with ease.
    """
    _instance: None | Any = None
    _initialized: bool = False
    _threads: List[Thread] = []
    _lock = Lock()
    _shutdown_event = Event()

    def __init__(self) -> None:
        if not hasattr(self, "_initialized"):
            self._initialized = True

    def Start(self, func: Callable[..., Any],
              *arg: Any, **kwarg: Any) -> Thread:
        """
        Start the thread, calling and using arguments given.
        """

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
        """
        Call all threads to shutdown.
        """
        self._shutdown_event.set()
        print("was set")
        for thread in self._threads:
            thread.join()
