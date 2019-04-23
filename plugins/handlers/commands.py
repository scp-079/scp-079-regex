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

from pyrogram import Client, Filters

from .. import glovar
from ..functions.etc import code, get_text, thread, user_mention
from ..functions.filters import regex_group, test_group
from ..functions.telegram import send_message
from .. functions.words import data_exchange, get_type, word_add, words_list, word_remove, words_search

# Enable logging
logger = logging.getLogger(__name__)


@Client.on_message(Filters.incoming & Filters.group & regex_group
                   & Filters.command(glovar.add_commands, glovar.prefix))
def add_word(client, message):
    try:
        cid = message.chat.id
        mid = message.message_id
        text, markup = word_add(message)
        thread(send_message, (client, cid, text, mid, markup))
        if "已添加" in text:
            thread(data_exchange, (client,))
    except Exception as e:
        logger.warning(f"Add words error: {e}", exc_info=True)


@Client.on_message(Filters.incoming & Filters.group & test_group
                   & Filters.command(["ping"], glovar.prefix))
def ping(client, message):
    try:
        text = code(f"{code('Pong!')}")
        thread(send_message, (client, message.chat.id, text))
    except Exception as e:
        logger.warning(f"Ping error: {e}", exc_info=True)


@Client.on_message(Filters.incoming & Filters.group & regex_group
                   & Filters.command(glovar.list_commands, glovar.prefix))
def list_words(client, message):
    try:
        cid = message.chat.id
        mid = message.message_id
        text, markup = words_list(message)
        thread(send_message, (client, cid, text, mid, markup))
    except Exception as e:
        logger.warning(f"List words error: {e}", exc_info=True)


@Client.on_message(Filters.incoming & Filters.group & regex_group
                   & Filters.command(glovar.remove_commands, glovar.prefix))
def remove_word(client, message):
    try:
        cid = message.chat.id
        mid = message.message_id
        text = word_remove(message)
        thread(send_message, (client, cid, text, mid))
        if "已移除" in text:
            thread(data_exchange, (client,))
    except Exception as e:
        logger.warning(f"Remove words error: {e}", exc_info=True)


@Client.on_message(Filters.incoming & Filters.group & regex_group
                   & Filters.command(["same"], glovar.prefix))
def same_word(client, message):
    try:
        cid = message.chat.id
        mid = message.message_id
        uid = message.from_user.id
        text = f"管理：{user_mention(uid)}\n"
        new_command_list = list(filter(None, message.command))
        new_word_type_list = new_command_list[1:]
        if len(new_command_list) > 1 and all([new_word_type in glovar.names for new_word_type in new_word_type_list]):
            if message.reply_to_message:
                old_message = message.reply_to_message
                aid = old_message.from_user.id
                if uid == aid:
                    old_command_list_raw = get_text(old_message).split(' ')
                    old_command_list = list(filter(None, old_command_list_raw))
                    old_command_type = old_command_list[0][1:]
                    if (len(old_command_list) > 2
                            and old_command_type in glovar.add_commands + glovar.remove_commands):
                        i, _ = get_type(old_command_list_raw)
                        old_word = get_text(old_message)[1
                                                         + len(old_command_list_raw[0])
                                                         + i
                                                         + len(old_command_list_raw[1]):].strip()
                        for new_word_type in new_word_type_list:
                            old_message.text = f"{old_command_type} {new_word_type} {old_word}"
                            if old_command_type in glovar.add_commands:
                                text, markup = word_add(old_message)
                                thread(send_message, (client, cid, text, mid, markup))
                            else:
                                text = word_remove(old_message)
                                thread(send_message, (client, cid, text, mid))

                        return
                    elif (old_command_type in glovar.remove_commands
                          and len(old_command_list) == 1
                          and old_message.reply_to_message):
                        old_message = old_message.reply_to_message
                        aid = old_message.from_user.id
                        if uid == aid:
                            old_command_list_raw = get_text(old_message).split(' ')
                            old_command_list = list(filter(None, old_command_list_raw))
                            old_command_type = old_command_list[0][1:]
                            if (len(old_command_list) > 2
                                    and old_command_type in glovar.remove_commands):
                                i, _ = get_type(old_command_list_raw)
                                old_word = get_text(old_message)[1
                                                                 + len(old_command_list_raw[0])
                                                                 + i
                                                                 + len(old_command_list_raw[1]):].strip()
                                for new_word_type in new_word_type_list:
                                    old_message.text = f"{old_command_type} {new_word_type} {old_word}"
                                    text = word_remove(old_message)
                                    thread(send_message, (client, cid, text, mid))

                                return
                            else:
                                text += (f"状态：{code('未执行')}\n"
                                         f"原因：{code('来源有误')}")
                        else:
                            text += (f"状态：{code('未执行')}\n"
                                     f"原因：{code('权限错误')}")
                    else:
                        text += (f"状态：{code('未执行')}\n"
                                 f"原因：{code('来源有误')}")
                else:
                    text += (f"状态：{code('未执行')}\n"
                             f"原因：{code('权限错误')}")
            else:
                text += (f"状态：{code('未执行')}\n"
                         f"原因：{code('操作有误')}")
        else:
            text += (f"状态：{code('未执行')}\n"
                     f"原因：{code('格式有误')}")

        thread(send_message, (client, cid, text, mid))
        if "已移除" in text:
            thread(data_exchange, (client,))
    except Exception as e:
        logger.warning(f"Remove words error: {e}", exc_info=True)


@Client.on_message(Filters.incoming & Filters.group & regex_group
                   & Filters.command(glovar.search_commands, glovar.prefix))
def search_words(client, message):
    try:
        cid = message.chat.id
        mid = message.message_id
        text, markup = words_search(message)
        thread(send_message, (client, cid, text, mid, markup))
    except Exception as e:
        logger.warning(f"Search words error: {e}", exc_info=True)
