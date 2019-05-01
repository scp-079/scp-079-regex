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
import re

from pyrogram import Client, Message

from .. import glovar
from .etc import code, get_text, t2s, thread
from .telegram import send_message
from .words import similar


# Enable logging
logger = logging.getLogger(__name__)


def name_test(client: Client, message: Message) -> bool:
    # Test user's or channel's name
    try:
        if message.forward_from or message.forward_from_name or message.forward_from_chat:
            cid = message.chat.id
            result = ""
            mid = message.message_id
            if message.forward_from:
                user = message.forward_from
                if user.is_deleted:
                    text = ""
                else:
                    text = user.first_name
                    if user.last_name:
                        text += f" {message.forward_from.last_name}"
            elif message.forward_from_name:
                text = message.forward_from_name
            else:
                chat = message.forward_from_chat
                text = chat.title

            if text:
                text = t2s(text)
                result += f"来源名称：{code(text)}\n\n"
                # Can add more test to the "for in" list
                for word_type in ["nm"]:
                    if glovar.compiled[word_type].search(text):
                        w_list = [w for w in eval(f"glovar.{word_type}_words") if similar("test", w, text)]
                        result += "\t" * 4 + f"{glovar.names[word_type]}：" + "-" * 16 + "\n\n"
                        for w in w_list:
                            result += "\t" * 8 + f"{code(w)}\n\n"

                thread(send_message, (client, cid, result, mid))
                return True
    except Exception as e:
        logger.warning(f"Name test error: {e}", exc_info=True)

    return False


def sticker_test(client: Client, message: Message) -> bool:
    # Test sticker set name
    try:
        if message.sticker and message.sticker.set_name:
            cid = message.chat.id
            result = ""
            mid = message.message_id
            text = message.sticker.set_name
            text = t2s(text)
            result += f"贴纸名称：{code(text)}\n\n"
            # Can add more test to the "for in" list
            for word_type in ["sti"]:
                if glovar.compiled[word_type].search(text):
                    w_list = [w for w in eval(f"glovar.{word_type}_words") if similar("test", w, text)]
                    result += "\t" * 4 + f"{glovar.names[word_type]}：" + "-" * 16 + "\n\n"
                    for w in w_list:
                        result += "\t" * 8 + f"{code(w)}\n\n"

            thread(send_message, (client, cid, result, mid))
            return True
    except Exception as e:
        logger.warning(f"Sticker test error: {e}", exc_info=True)

    return False


def text_test(client: Client, message: Message) -> bool:
    # Test message text or caption
    try:
        text = get_text(message)
        except_pattern = ("^版本：|"
                          "^#(bug|done|fixed|todo)|"
                          "^已(解禁|警告)|"
                          "^被举报|"
                          "^管理员|"
                          "^{|"
                          "^NSFW 得分|"
                          "^复查模型")
        if text and not re.search(except_pattern, text, re.I):
            cid = message.chat.id
            result = ""
            mid = message.message_id
            for word_type in glovar.names:
                if glovar.compiled[word_type].search(text):
                    w_list = [w for w in eval(f"glovar.{word_type}_words") if similar("test", w, text)]
                    result += f"{glovar.names[word_type]}：" + "-" * 24 + "\n\n"
                    for w in w_list:
                        result += "\t" * 4 + f"{code(w)}\n\n"

            if result:
                thread(send_message, (client, cid, result, mid))

            return True
    except Exception as e:
        logger.warning(f"Text test error: {e}", exc_info=True)

    return False
