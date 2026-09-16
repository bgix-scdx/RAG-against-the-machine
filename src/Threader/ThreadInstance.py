from threading import Thread, Event, current_thread
from typing import Any, Callable

class ThreadInstance(Thread):

    def __init__(self, func: Callable, *args: Any, **kwargs: Any):
        current_thread().stop_event = Event()
        func(*args, **kwargs)
