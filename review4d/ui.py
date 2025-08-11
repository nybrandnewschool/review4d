import contextlib

__all__ = [
    "suppress_messages",
    "messages_suppressed",
]


@contextlib.contextmanager
def suppress_messages(ui):
    previous_value = getattr(ui, "messages_suppressed", False)
    try:
        ui.messages_suppressed = True
        yield
    finally:
        ui.messages_suppressed = previous_value


def messages_suppressed(ui):
    return getattr(ui, "messages_suppressed", False)
