import logging
from threading import Thread
from typing import Callable

# Enable logging
logger = logging.getLogger(__name__)


def code(text: str) -> str:
    if text != "":
        return f"`{text}`"

    return ""


def code_block(text: str) -> str:
    if text != "":
        return f"```{text}````"

    return ""


def thread(target: Callable, args: tuple) -> bool:
    t = Thread(target=target, args=args)
    t.daemon = True
    t.start()

    return True


def bytes_data(action: str, call_type: str = None, data: int = 1) -> bytes:
    text = ('{'
            f'"action":"{action}",'
            f'"type":"{call_type}",'
            f'"data":{data}'
            '}')

    return text.encode("utf-8")
