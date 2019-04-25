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

import re

from pyrogram import Client, Message

from .. import glovar
from .etc import code, get_text, t2s, thread
from .telegram import send_message
from .words import similar


def name_test(client: Client, message: Message) -> bool:
    if message.forward_from or message.forward_from_name or message.forward_from_chat:
        cid = message.chat.id
        result = ""
        mid = message.message_id

        if message.forward_from:
            user = message.forward_from
            if user.is_deleted:
                text = ""
            else:
                first_name = user.first_name
                last_name = ""
                if user.last_name:
                    last_name = message.forward_from.last_name

                text = f"{first_name} {last_name}"
        elif message.forward_from_name:
            text = message.forward_from_name
        else:
            chat = message.forward_from_chat
            text = chat.title

        if text != "":
            text = t2s(text)
            result += f"来源名称：{code(text)}\n\n"
            for word_type in ["nm", "wb"]:
                if glovar.compiled[word_type].search(text):
                    w_list = [w for w in eval(f"glovar.{word_type}_words") if similar("test", w, text)]
                    result += "\t" * 4 + f"{glovar.names[word_type]}：----------------\n\n"
                    for w in w_list:
                        result += "\t" * 8 + f"{code(w)}\n\n"

            thread(send_message, (client, cid, result, mid))
            return True

    return False


def sticker_test(client: Client, message: Message) -> bool:
    if message.sticker and message.sticker.set_name:
        cid = message.chat.id
        result = ""
        mid = message.message_id

        text = message.sticker.set_name
        text = t2s(text)
        result += f"贴纸名称：{code(text)}\n\n"
        for word_type in ["sti"]:
            if glovar.compiled[word_type].search(text):
                w_list = [w for w in eval(f"glovar.{word_type}_words") if similar("test", w, text)]
                result += "\t" * 4 + f"{glovar.names[word_type]}：----------------\n\n"
                for w in w_list:
                    result += "\t" * 8 + f"{code(w)}\n\n"

        thread(send_message, (client, cid, result, mid))
        return True

    return False


def text_test(client: Client, message: Message) -> bool:
    text = get_text(message)
    if text and not re.search("^版本：", text):
        cid = message.chat.id
        result = ""
        mid = message.message_id

        for word_type in glovar.names:
            if glovar.compiled[word_type].search(text):
                w_list = [w for w in eval(f"glovar.{word_type}_words") if similar("test", w, text)]
                result += f"{glovar.names[word_type]}：------------------------\n\n"
                for w in w_list:
                    result += "\t" * 4 + f"{code(w)}\n\n"

        if result == "":
            result = "并无匹配的各项检测结果"

        thread(send_message, (client, cid, result, mid))
        return True

    return False
