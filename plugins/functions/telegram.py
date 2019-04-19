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
from time import sleep

from pyrogram import ParseMode
from pyrogram.errors import FloodWait

# Enable logging
logger = logging.getLogger(__name__)


def answer_callback(client, query_id: int, text: str):
    result = None
    try:
        while not result:
            try:
                result = client.answer_callback_query(
                    callback_query_id=query_id,
                    text=text,
                    show_alert=True
                )
            except FloodWait as e:
                sleep(e.x + 1)
    except Exception as e:
        logger.warning(f"Answer query to {query_id} error: {e}", exc_info=True)

    return result


def edit_message(client, cid: int, mid: int, text: str, markup=None):
    result = None
    try:
        if text.strip() != "":
            while not result:
                try:
                    result = client.edit_message_text(
                        chat_id=cid,
                        message_id=mid,
                        text=text,
                        parse_mode=ParseMode.MARKDOWN,
                        disable_web_page_preview=True,
                        reply_markup=markup
                    )
                except FloodWait as e:
                    sleep(e.x + 1)
    except Exception as e:
        logger.warning(f"Edit message at {cid} error: {e}", exc_info=True)

    return result


def send_document(client, cid: int, file: str, text: str = None, mid: int = None, markup=None):
    result = None
    try:
        while not result:
            try:
                result = client.send_document(
                    chat_id=cid,
                    document=file,
                    caption=text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_to_message_id=mid,
                    reply_markup=markup
                )
            except FloodWait as e:
                sleep(e.x + 1)
    except Exception as e:
        logger.warning(f"Send document at {cid} error: {e}", exec_info=True)

    return result


def send_message(client, cid: int, text: str, mid: int = None, markup=None):
    result = None
    try:
        if text.strip() != "":
            while not result:
                try:
                    result = client.send_message(
                        chat_id=cid,
                        text=text,
                        parse_mode=ParseMode.MARKDOWN,
                        disable_web_page_preview=True,
                        reply_to_message_id=mid,
                        reply_markup=markup
                    )
                except FloodWait as e:
                    sleep(e.x + 1)
    except Exception as e:
        logger.warning(f"Send message to {cid} error: {e}", exc_info=True)

    return result
