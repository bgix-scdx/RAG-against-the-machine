from ..Utils.Decorators import service
from threading import Thread, current_thread, Lock, Event
from typing import List, Any, Callable


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
                func(*arg, **kwarg)
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
        if wait:
            self.joinAll(timeout=timeout)

    def joinAll(self, timeout: float | None = None) -> None:
        print("joining")
        with self._lock:
            threads_snapshot = list(self._threads)
        for t in threads_snapshot:
            t.join(timeout=timeout)
