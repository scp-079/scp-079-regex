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
from copy import deepcopy
from string import ascii_lowercase

from pyrogram import Client, Message

from .. import glovar
from .etc import code, get_filename, get_forward_name, get_int, get_text, lang, mention_id, thread
from .filters import is_regex_text
from .telegram import get_sticker_title, send_message
from .words import is_similar

# Enable logging
logger = logging.getLogger(__name__)


def name_test(client: Client, message: Message) -> bool:
    # Test user's or channel's name
    try:
        text = get_forward_name(message)

        if not text:
            return True

        cid = message.chat.id
        aid = message.from_user.id
        mid = message.message_id
        result = ""

        for word_type in ["ad", "con", "iml", "nm", "wb", "test"]:
            if not is_regex_text(word_type, text):
                continue

            w_list = [w for w in deepcopy(eval(f"glovar.{word_type}_words")) if is_similar("test", w, text)]
            result += "\t" * 4 + f"{lang(word_type)}：" + "-" * 16 + "\n\n"
            for w in w_list:
                result += "\t" * 8 + f"{code(w)}\n\n"

        if not result:
            return True

        result = (f"{lang('admin')}{lang('colon')}{mention_id(aid)}\n\n"
                  f"{lang('from_name')}{lang('colon')}{code(text)}\n\n") + result
        thread(send_message, (client, cid, result, mid))

        return True
    except Exception as e:
        logger.warning(f"Name test error: {e}", exc_info=True)

    return False


def sticker_test(client: Client, message: Message) -> bool:
    # Test sticker set name
    try:
        if not message.sticker or not message.sticker.set_name:
            return True

        cid = message.chat.id
        aid = message.from_user.id
        mid = message.message_id
        result = ""

        result += f"{lang('admin')}{lang('colon')}{mention_id(aid)}\n\n"
        sticker_name = message.sticker.set_name
        result += f"{lang('sticker_name')}{lang('colon')}{code(sticker_name)}\n\n"

        for word_type in ["sti", "test"]:
            if not is_regex_text(word_type, sticker_name):
                continue

            w_list = [w for w in deepcopy(eval(f"glovar.{word_type}_words"))
                      if is_similar("test", w, sticker_name)]
            result += "\t" * 4 + f"{lang(word_type)}：" + "-" * 16 + "\n\n"
            for w in w_list:
                result += "\t" * 8 + f"{code(w)}\n\n"

        sticker_title = get_sticker_title(client, sticker_name)
        result += f"{lang('sticker_title')}{lang('colon')}{code(sticker_title)}\n\n"

        for word_type in ["ad", "con", "ban", "sti", "test"]:
            if not is_regex_text(word_type, sticker_title):
                continue

            w_list = [w for w in deepcopy(eval(f"glovar.{word_type}_words"))
                      if is_similar("test", w, sticker_title)]
            result += "\t" * 4 + f"{lang(word_type)}：" + "-" * 16 + "\n\n"
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
        origin_text = get_text(message)
        if re.search(f"^{lang('admin')}{lang('colon')}[0-9]", origin_text):
            aid = get_int(origin_text.split("\n\n")[0].split(lang('colon'))[1])
        else:
            aid = message.from_user.id

        except_pattern = (f"^#(bug|done|fixed|todo)|"
                          f"^{lang('version')}{lang('colon')}|"
                          f"^{lang('message_print')}{lang('colon')}")

        text = get_filename(message, True) + get_text(message, True)

        if not text or re.search(except_pattern, origin_text, re.I | re.M | re.S):
            return True

        result_list = [""]

        # Make test result in this order
        # ad adx
        # con iml
        # ban bio nm del
        # wb wd bad
        # etc
        order_list = ["ad"] + [f"ad{c}" for c in ascii_lowercase]
        order_list += ["con", "iml", "ban", "bio", "nm", "del", "wb", "wd", "bad"]
        order_set = set(order_list)
        type_set = set(glovar.regex)
        type_list = order_list + list(type_set - order_set)

        for word_type in type_list:
            if len(result_list[-1]) > 2000:
                result_list.append("")

            if is_regex_text(word_type, text):
                w_list = [w for w in deepcopy(eval(f"glovar.{word_type}_words")) if is_similar("test", w, text)]
                result_list[-1] += f"{lang(word_type)}：" + "-" * 24 + "\n\n"
                for w in w_list:
                    result_list[-1] += "\t" * 4 + f"{code(w)}\n\n"

        for result in result_list:
            if result:
                result = f"{lang('admin')}{lang('colon')}{mention_id(aid)}\n\n" + result
                send_message(client, glovar.test_group_id, result, message.message_id)

        return True
    except Exception as e:
        logger.warning(f"Text test error: {e}", exc_info=True)

    return False
