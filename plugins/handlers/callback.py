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
from json import loads

from pyrogram import Client, CallbackQuery

from .. import glovar
from ..functions.etc import get_now, lang, mention_id, thread
from ..functions.filters import regex_group
from ..functions.words import cc, get_admin, get_desc, words_ask, words_list_page, words_search_page
from ..functions.telegram import answer_callback, edit_message_reply_markup, edit_message_text

# Enable logging
logger = logging.getLogger(__name__)


@Client.on_callback_query(regex_group)
def answer(client: Client, callback_query: CallbackQuery) -> bool:
    # Answer the callback query
    glovar.locks["regex"].acquire()
    try:
        # Basic data
        cid = callback_query.message.chat.id
        uid = callback_query.from_user.id
        aid = get_admin(callback_query.message)
        mid = callback_query.message.message_id
        callback_data = loads(callback_query.data)
        action = callback_data["a"]
        action_type = callback_data["t"]
        data = callback_data["d"]

        # Check permission
        if uid != aid:
            return True

        # Check the date
        date = callback_query.message.date
        now = get_now()
        if now - date > 86400:
            thread(edit_message_reply_markup, (client, cid, mid, None))

        # Answer the words ask
        if action == "ask":
            text = f"{lang('admin')}{lang('colon')}{mention_id(aid)}\n"
            result_text, cc_list = words_ask(client, action_type, data)
            text += result_text
            edit_message_text(client, cid, mid, text)
            cc(client, cc_list, aid, mid)

        # List the word
        elif action == "list":
            word_type = action_type
            page = data
            desc = get_desc(callback_query.message)
            text, markup = words_list_page(uid, word_type, page, desc)
            thread(edit_message_text, (client, cid, mid, text, markup))

        # Search the word
        elif action == "search":
            key = action_type
            page = data
            text, markup = words_search_page(uid, key, page)
            thread(edit_message_text, (client, cid, mid, text, markup))

        thread(answer_callback, (client, callback_query.id, ""))

        return True
    except Exception as e:
        logger.warning(f"Answer callback error: {e}", exc_info=True)
    finally:
        glovar.locks["regex"].release()

    return False
