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

from pyrogram import Client

from .. import glovar
from ..functions.etc import delay, send_data, thread, user_mention
from .. functions.words import words_ask, words_list
from ..functions.telegram import answer_callback, edit_message, send_document, send_message

# Enable logging
logger = logging.getLogger(__name__)


@Client.on_callback_query()
def answer(client, callback_query):
    try:
        cid = callback_query.message.chat.id
        if cid == glovar.main_group_id:
            aid = callback_query.from_user.id
            mid = callback_query.message.message_id
            callback_data = loads(callback_query.data)
            operation = callback_data["o"]
            operation_type = callback_data["t"]
            data = callback_data["d"]
            if operation == "list":
                word_type = operation_type
                page = data
                text, markup = words_list(word_type, page)
                text = f"管理：{user_mention(aid)}\n" + text
                thread(edit_message, (client, cid, mid, text, markup))
            elif operation == "ask":
                text = words_ask(operation_type, data)
                text = f"管理：{user_mention(aid)}\n" + text
                thread(edit_message, (client, cid, mid, text))
                if "已添加" in text:
                    if glovar.update_type == "reload":
                        exchange_text = send_data(
                            sender="REGEX",
                            receivers=["USER", "WATCHER"],
                            operation="update",
                            operation_type="reload",
                            data=glovar.reload_path
                        )
                        delay(5, send_message, [client, glovar.exchange_id, exchange_text])
                    else:
                        exchange_text = send_data(
                            sender="REGEX",
                            receivers=["USER", "WATCHER"],
                            operation="update",
                            operation_type="download"
                        )
                        delay(5, send_document, [client, glovar.exchange_id, "data/compiled", exchange_text])

            thread(answer_callback, (client, callback_query.id, ""))
    except Exception as e:
        logger.warning(f"Answer callback error: {e}", exc_info=True)
