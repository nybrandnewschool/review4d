import traceback

try:
    from queue import Queue
except ImportError:
    from Queue import Queue

import c4d

from .constants import COMMAND_QUEUE_ID

__all__ = [
    "execute_in_main_thread",
    "execute_queued_commands",
]


COMMAND_QUEUE = Queue()


def execute_in_main_thread(task, *args, **kwargs):
    COMMAND_QUEUE.put((task, args, kwargs))
    c4d.SpecialEventAdd(COMMAND_QUEUE_ID)


def execute_queued_commands():
    while not COMMAND_QUEUE.empty():
        task, args, kwargs = COMMAND_QUEUE.get()
        try:
            task(*args, **kwargs)
        except:
            traceback.print_exc()
