# SCP-079-REGEX - Manage the regex patterns
# Copyright (C) 2019 SCP-079 <https://scp-079.org>
#
# This file is part of SCP-079-REGEX.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
from json import dumps, loads
from random import choice
from string import ascii_letters, digits
from threading import Thread, Timer
from typing import Callable, List, Optional, Union

from cryptography.fernet import Fernet
from opencc import convert
from pyrogram import Message

# Enable logging
logger = logging.getLogger(__name__)


def bold(text) -> str:
    if text != "":
        return f"**{text}**"

    return ""


def button_data(action: str, action_type: str = None, data: Union[int, str] = None) -> bytes:
    button = {
        "a": action,
        "t": action_type,
        "d": data
    }
    return dumps(button).replace(" ", "").encode("utf-8")


def code(text) -> str:
    if text != "":
        return f"`{text}`"

    return ""


def code_block(text) -> str:
    if text != "":
        return f"```{text}```"

    return ""


def crypt_str(operation: str, text: str, key: str) -> str:
    f = Fernet(key)
    text = text.encode("utf-8")
    if operation == "decrypt":
        result = f.decrypt(text)
    else:
        result = f.encrypt(text)

    result = result.decode("utf-8")

    return result


def delay(secs: int, target: Callable, args: list) -> bool:
    t = Timer(secs, target, args)
    t.daemon = True
    t.start()

    return True


def get_text(message: Message) -> Optional[str]:
    text = None
    if message.text:
        text = message.text
    elif message.caption:
        text = message.caption

    if text:
        text = t2s(text)

    return text


def italic(text) -> str:
    if text != "":
        return f"__{text}__"

    return ""


def random_str(i: int) -> str:
    return ''.join(choice(ascii_letters + digits) for _ in range(i))


def receive_data(message: Message) -> dict:
    text = get_text(message)
    try:
        assert text is not None, f"Can't get text from message: {message}"
        data = loads(text)
        return data
    except Exception as e:
        logger.warning(f"Receive data error: {e}")

    return {}


def send_data(sender: str, receivers: List[str], action: str, action_type: str, data=None) -> str:
    """Make a unified format string for data exchange.

    Args:
        sender (str):
            The sender's name. It can be any of the followings:
                REGEX - Stands for SCP-079-REGEX
                USER - Stands for SCP-079-USER
                WATCH - Stands for SCP-079-WATCHER

        receivers (list of str):
            The receivers' names. It can be any of the followings:
                USER - Stands for SCP-079-USER
                WATCH - Stands for SCP-079-WATCHER

        action (str):
            The operation that the data receivers need to perform. It can be any of the followings:
                add - Add id to some list
                backup - Announce backup data
                remove - Remove id in some list
                update - Update some data

        action_type (str):
            Type of operation. It can be any of the followings:
                When operation is add or remove:
                    bad channel - Spam channel
                    bad user - Spam user
                    except channel - Exception channel
                    except user - Exception user
                    watch bad - Suspicious user.
                                Recommended to ban the user when meets certain conditions
                    watch delete - Suspicious user.
                                   Recommended to delete messages from the user when meets certain conditions

                When operation is backup:
                    pickle - Pickle file

                When operation is update:
                    download - Download the data, then update
                    reload - Update the data from local machines


        data (optional):
            Additional data required for operation.

    Returns:
        A formatted string.
    """
    data = {
        "from": sender,
        "to": receivers,
        "action": action,
        "type": action_type,
        "data": data
    }

    return code_block(dumps(data, indent=4))


def t2s(text: str) -> str:
    return convert(text, config="t2s.json")


def thread(target: Callable, args: tuple) -> bool:
    t = Thread(target=target, args=args)
    t.daemon = True
    t.start()

    return True


def user_mention(uid: int) -> str:
    return f"[{uid}](tg://user?id={uid})"
