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
from html import escape
from json import dumps, loads
from random import choice, uniform
from string import ascii_letters, digits
from threading import Thread, Timer
from time import sleep, time
from typing import Any, Callable, List, Optional, Union
from unicodedata import normalize

from cryptography.fernet import Fernet
from opencc import convert
from pyrogram import InlineKeyboardButton, InlineKeyboardMarkup, Message, User
from pyrogram.errors import FloodWait

from .. import glovar

# Enable logging
logger = logging.getLogger(__name__)


def bold(text: Any) -> str:
    # Get a bold text
    try:
        text = str(text).strip()
        if text:
            return f"<b>{escape(text)}</b>"
    except Exception as e:
        logger.warning(f"Bold error: {e}", exc_info=True)

    return ""


def button_data(action: str, action_type: str = None, data: Union[int, str] = None) -> Optional[bytes]:
    # Get a button's bytes data
    result = None
    try:
        button = {
            "a": action,
            "t": action_type,
            "d": data
        }
        result = dumps(button).replace(" ", "").encode("utf-8")
    except Exception as e:
        logger.warning(f"Button data error: {e}", exc_info=True)

    return result


def code(text: Any) -> str:
    # Get a code text
    try:
        text = str(text).strip()
        if text:
            return f"<code>{escape(text)}</code>"
    except Exception as e:
        logger.warning(f"Code error: {e}", exc_info=True)

    return ""


def code_block(text: Any) -> str:
    # Get a code block text
    try:
        text = str(text).rstrip()
        if text:
            return f"<pre>{escape(text)}</pre>"
    except Exception as e:
        logger.warning(f"Code block error: {e}", exc_info=True)

    return ""


def crypt_str(operation: str, text: str, key: str) -> str:
    # Encrypt or decrypt a string
    result = ""
    try:
        f = Fernet(key)
        text = text.encode("utf-8")

        if operation == "decrypt":
            result = f.decrypt(text)
        else:
            result = f.encrypt(text)

        result = result.decode("utf-8")
    except Exception as e:
        logger.warning(f"Crypt str error: {e}", exc_info=True)

    return result


def delay(secs: int, target: Callable, args: list) -> bool:
    # Call a function with delay
    try:
        t = Timer(secs, target, args)
        t.daemon = True
        t.start()

        return True
    except Exception as e:
        logger.warning(f"Delay error: {e}", exc_info=True)

    return False


def general_link(text: Union[int, str], link: str) -> str:
    # Get a general link
    result = ""
    try:
        text = str(text).strip()
        link = link.strip()
        if text and link:
            result = f'<a href="{link}">{escape(text)}</a>'
    except Exception as e:
        logger.warning(f"General link error: {e}", exc_info=True)

    return result


def get_channel_link(message: Union[int, Message]) -> str:
    # Get a channel reference link
    text = ""
    try:
        text = "https://t.me/"
        if isinstance(message, int):
            text += f"c/{str(message)[4:]}"
        else:
            if message.chat.username:
                text += f"{message.chat.username}"
            else:
                cid = message.chat.id
                text += f"c/{str(cid)[4:]}"
    except Exception as e:
        logger.warning(f"Get channel link error: {e}", exc_info=True)

    return text


def get_callback_data(message: Message) -> List[dict]:
    # Get a message's inline button's callback data
    callback_data_list = []
    try:
        reply_markup = message.reply_markup

        if (not reply_markup
                or not isinstance(reply_markup, InlineKeyboardMarkup)
                or not reply_markup.inline_keyboard):
            return []

        for button_row in reply_markup.inline_keyboard:
            for button in button_row:
                if not button.callback_data:
                    continue

                callback_data = button.callback_data
                callback_data = loads(callback_data)
                callback_data_list.append(callback_data)
    except Exception as e:
        logger.warning(f"Get callback data error: {e}", exc_info=True)

    return callback_data_list


def get_command_context(message: Message) -> (str, str):
    # Get the type "a" and the context "b" in "/command a b"
    command_type = ""
    command_context = ""
    try:
        text = get_text(message)
        command_list = text.split(" ")

        if len(list(filter(None, command_list))) <= 1:
            return "", ""

        i = 1
        command_type = command_list[i]

        while command_type == "" and i < len(command_list):
            i += 1
            command_type = command_list[i]

        command_context = text[1 + len(command_list[0]) + i + len(command_type):].strip()
    except Exception as e:
        logger.warning(f"Get command context error: {e}", exc_info=True)

    return command_type, command_context


def get_command_type(message: Message) -> str:
    # Get the command type "a" in "/command a"
    result = ""
    try:
        text = get_text(message)
        command_list = list(filter(None, text.split(" ")))
        result = text[len(command_list[0]):].strip()
    except Exception as e:
        logger.warning(f"Get command type error: {e}", exc_info=True)

    return result


def get_filename(message: Message, normal: bool = False, printable: bool = False) -> str:
    # Get file's filename
    text = ""
    try:
        if message.document:
            if message.document.file_name:
                text += message.document.file_name
        elif message.audio:
            if message.audio.file_name:
                text += message.audio.file_name

        if text:
            text = t2t(text, normal, printable)
    except Exception as e:
        logger.warning(f"Get filename error: {e}", exc_info=True)

    return text


def get_forward_name(message: Message, normal: bool = False, printable: bool = False) -> str:
    # Get forwarded message's origin sender's name
    text = ""
    try:
        if message.forward_from:
            user = message.forward_from
            text = get_full_name(user, normal, printable)
        elif message.forward_sender_name:
            text = message.forward_sender_name
        elif message.forward_from_chat:
            chat = message.forward_from_chat
            text = chat.title

        if text:
            text = t2t(text, normal, printable)
    except Exception as e:
        logger.warning(f"Get forward name error: {e}", exc_info=True)

    return text


def get_full_name(user: User, normal: bool = False, printable: bool = False) -> str:
    # Get user's full name
    text = ""
    try:
        if not user or user.is_deleted:
            return ""

        text = user.first_name
        if user.last_name:
            text += f" {user.last_name}"

        if text and normal:
            text = t2t(text, normal, printable)
    except Exception as e:
        logger.warning(f"Get full name error: {e}", exc_info=True)

    return text


def get_int(text: str) -> Optional[int]:
    # Get a int from a string
    result = None
    try:
        result = int(text)
    except Exception as e:
        logger.info(f"Get int error: {e}", exc_info=True)

    return result


def get_list_page(the_list: list, action: str, action_type: str, page: int) -> (list, InlineKeyboardMarkup):
    # Generate a list for elements and markup buttons
    markup = None
    try:
        per_page = glovar.per_page
        quo = int(len(the_list) / per_page)

        if quo == 0:
            return the_list, None

        page_count = quo + 1

        if len(the_list) % per_page == 0:
            page_count = page_count - 1

        if page != page_count:
            the_list = the_list[(page - 1) * per_page:page * per_page]
        else:
            the_list = the_list[(page - 1) * per_page:len(the_list)]

        if page_count == 1:
            return the_list, markup

        if page == 1:
            markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text=lang("page").format(page),
                            callback_data=button_data("none")
                        ),
                        InlineKeyboardButton(
                            text=">>",
                            callback_data=button_data(action, action_type, page + 1)
                        )
                    ]
                ]
            )
        elif page == page_count:
            markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="<<",
                            callback_data=button_data(action, action_type, page - 1)
                        ),
                        InlineKeyboardButton(
                            text=lang("page").format(page),
                            callback_data=button_data("none")
                        )
                    ]
                ]
            )
        else:
            markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="<<",
                            callback_data=button_data(action, action_type, page - 1)
                        ),
                        InlineKeyboardButton(
                            text=lang("page").format(page),
                            callback_data=button_data("none")
                        ),
                        InlineKeyboardButton(
                            text=">>",
                            callback_data=button_data(action, action_type, page + 1)
                        )
                    ]
                ]
            )
    except Exception as e:
        logger.warning(f"Get list page error: {e}", exc_info=True)

    return the_list, markup


def get_now() -> int:
    # Check time for now
    result = 0
    try:
        result = int(time())
    except Exception as e:
        logger.warning(f"Get now error: {e}", exc_info=True)

    return result


def get_text(message: Message, normal: bool = False, printable: bool = False) -> str:
    # Get message's text, including links and buttons
    text = ""
    try:
        if not message:
            return ""

        the_text = message.text or message.caption
        if the_text:
            text += the_text
            entities = message.entities or message.caption_entities
            if entities:
                for en in entities:
                    if not en.url:
                        continue

                    text += f"\n{en.url}"

        reply_markup = message.reply_markup
        if (reply_markup
                and isinstance(reply_markup, InlineKeyboardMarkup)
                and reply_markup.inline_keyboard):
            for button_row in reply_markup.inline_keyboard:
                for button in button_row:
                    if not button:
                        continue

                    if button.text:
                        text += f"\n{button.text}"

                    if button.url:
                        text += f"\n{button.url}"

        if text:
            text = t2t(text, normal, printable)
    except Exception as e:
        logger.warning(f"Get text error: {e}", exc_info=True)

    return text


def italic(text: Any) -> str:
    # Get italic text
    try:
        text = str(text).strip()
        if text:
            return f"<i>{escape(text)}</i>"
    except Exception as e:
        logger.warning(f"Italic error: {e}", exc_info=True)

    return ""


def lang(text: str) -> str:
    # Get the text
    result = ""
    try:
        result = glovar.lang.get(text, text)
    except Exception as e:
        logger.warning(f"Lang error: {e}", exc_info=True)

    return result


def mention_id(uid: int) -> str:
    # Get a ID mention string
    result = ""
    try:
        result = general_link(f"{uid}", f"tg://user?id={uid}")
    except Exception as e:
        logger.warning(f"Mention id error: {e}", exc_info=True)

    return result


def message_link(message: Message) -> str:
    # Get a message link in a channel
    text = ""
    try:
        mid = message.message_id
        text = f"{get_channel_link(message)}/{mid}"
    except Exception as e:
        logger.warning(f"Message link error: {e}", exc_info=True)

    return text


def random_str(i: int) -> str:
    # Get a random string
    text = ""
    try:
        text = "".join(choice(ascii_letters + digits) for _ in range(i))
    except Exception as e:
        logger.warning(f"Random str error: {e}", exc_info=True)

    return text


def t2t(text: str, normal: bool, printable: bool) -> str:
    # Convert the string, text to text
    try:
        if not text:
            return ""

        if normal:
            for special in ["spc", "spe"]:
                text = "".join(eval(f"glovar.{special}_dict").get(t, t) for t in text)

            text = normalize("NFKC", text)

        if printable:
            text = "".join(t for t in text if t.isprintable() or t in {"\n", "\r", "\t"})

        if glovar.zh_cn:
            text = convert(text, config="t2s.json")
    except Exception as e:
        logger.warning(f"T2T error: {e}", exc_info=True)

    return text


def thread(target: Callable, args: tuple) -> bool:
    # Call a function using thread
    try:
        t = Thread(target=target, args=args)
        t.daemon = True
        t.start()

        return True
    except Exception as e:
        logger.warning(f"Thread error: {e}", exc_info=True)

    return False


def wait_flood(e: FloodWait) -> bool:
    # Wait flood secs
    try:
        sleep(e.x + uniform(0.5, 1.0))

        return True
    except Exception as e:
        logger.warning(f"Wait flood error: {e}", exc_info=True)

    return False
