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

from ..functions.etc import thread, user_mention
from ..functions.filters import regex_group
from .. functions.words import get_admin, get_desc, words_ask, words_list_page, words_search_page
from ..functions.telegram import answer_callback, edit_message_text

# Enable logging
logger = logging.getLogger(__name__)


@Client.on_callback_query(regex_group)
def answer(client: Client, callback_query: CallbackQuery):
    # Answer the callback query
    try:
        cid = callback_query.message.chat.id
        uid = callback_query.from_user.id
        aid = get_admin(callback_query.message)
        # Check permission
        if uid == aid:
            # Basic callback data
            mid = callback_query.message.message_id
            callback_data = loads(callback_query.data)
            action = callback_data["a"]
            action_type = callback_data["t"]
            data = callback_data["d"]
            if action == "ask":
                text = (f"管理：{user_mention(aid)}\n"
                        f"{words_ask(client, action_type, data)}")
                thread(edit_message_text, (client, cid, mid, text))
            elif action == "list":
                word_type = action_type
                page = data
                desc = get_desc(callback_query.message)
                text, markup = words_list_page(uid, word_type, page, desc)
                thread(edit_message_text, (client, cid, mid, text, markup))
            elif action == "search":
                key = action_type
                page = data
                text, markup = words_search_page(uid, key, page)
                thread(edit_message_text, (client, cid, mid, text, markup))

            thread(answer_callback, (client, callback_query.id, ""))
    except Exception as e:
        logger.warning(f"Answer callback error: {e}", exc_info=True)
