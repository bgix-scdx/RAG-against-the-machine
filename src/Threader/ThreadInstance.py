from threading import Thread, Event
from typing import Any, Callable


class ThreadInstance(Thread):
    stop_event: Event = Event()

    def __init__(self, func: Callable[..., Any], *args: Any, **kwargs: Any):
        super().__init__()
        func(*args, **kwargs)
