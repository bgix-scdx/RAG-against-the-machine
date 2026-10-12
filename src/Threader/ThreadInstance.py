from threading import Thread, Event
from typing import Any, Callable


class ThreadInstance(Thread):
    """
    Instance for a thread, allowing to know status of it.
    """
    stop_event: Event = Event()

    def __init__(self, func: Callable[..., Any], *args: Any, **kwargs: Any):
        super().__init__()
        func(*args, **kwargs)
