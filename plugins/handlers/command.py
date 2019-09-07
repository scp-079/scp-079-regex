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
from copy import deepcopy

from pyrogram import Client, Filters, Message

from .. import glovar
from ..functions.channel import share_data, share_regex_update
from ..functions.etc import bold, code, general_link, get_callback_data, get_command_context, get_command_type, get_text
from ..functions.etc import message_link, thread, user_mention
from ..functions.file import save
from ..functions.filters import from_user, regex_group, test_group
from ..functions.telegram import edit_message_text, get_messages, send_message
from ..functions.words import get_admin, get_desc, word_add, words_ask, words_list, words_list_page, word_remove
from ..functions.words import words_search, words_search_page

# Enable logging
logger = logging.getLogger(__name__)


@Client.on_message(Filters.incoming & Filters.group & regex_group & from_user
                   & Filters.command(glovar.add_commands, glovar.prefix))
def add_word(client: Client, message: Message) -> bool:
    # Add a new word
    if glovar.locks["regex"].acquire():
        try:
            cid = message.chat.id
            mid = message.message_id
            text, markup = word_add(client, message)
            thread(send_message, (client, cid, text, mid, markup))

            return True
        except Exception as e:
            logger.warning(f"Add word error: {e}", exc_info=True)
        finally:
            glovar.locks["regex"].release()

    return False


@Client.on_message(Filters.incoming & Filters.group & regex_group & from_user
                   & Filters.command(["ask"], glovar.prefix))
def ask_word(client: Client, message: Message) -> bool:
    # Deal with a duplicated word
    if glovar.locks["regex"].acquire():
        try:
            cid = message.chat.id
            mid = message.message_id
            uid = message.from_user.id
            text = f"管理：{user_mention(uid)}\n"
            command_list = list(filter(None, message.command))
            if len(command_list) == 2 and command_list[1] in {"new", "replace", "cancel"}:
                command_type = command_list[1]
                if message.reply_to_message:
                    r_message = message.reply_to_message
                    aid = get_admin(r_message)
                    if uid == aid:
                        callback_data_list = get_callback_data(r_message)
                        if r_message.from_user.is_self and callback_data_list and callback_data_list[0]["a"] == "ask":
                            r_mid = r_message.message_id
                            ask_key = callback_data_list[0]["d"]
                            ask_text = (f"管理：{user_mention(aid)}\n"
                                        f"{words_ask(client, command_type, ask_key)}")
                            thread(edit_message_text, (client, cid, r_mid, ask_text))
                            text += (f"状态：{code('已操作')}\n"
                                     f"查看：{general_link(r_mid, message_link(r_message))}\n")
                        else:
                            text += (f"状态：{code('未操作')}\n"
                                     f"原因：{code('来源有误')}\n")
                    else:
                        text += (f"状态：{code('未操作')}\n"
                                 f"原因：{code('权限有误')}\n")
                else:
                    text += (f"状态：{code('未操作')}\n"
                             f"原因：{code('用法有误')}\n")
            else:
                text += (f"状态：{code('未操作')}\n"
                         f"原因：{code('格式有误')}\n")

            thread(send_message, (client, cid, text, mid))

            return True
        except Exception as e:
            logger.warning(f"Ask word error: {e}", exc_info=True)
        finally:
            glovar.locks["regex"].release()

    return False


@Client.on_message(Filters.incoming & Filters.group & regex_group & from_user
                   & Filters.command(["count"], glovar.prefix))
def count_words(client: Client, message: Message) -> bool:
    # Count words
    if glovar.locks["regex"].acquire():
        try:
            cid = message.chat.id
            mid = message.message_id
            uid = message.from_user.id
            receivers = []
            for word_type in glovar.receivers:
                receivers += glovar.receivers[word_type]

            receivers = list(set(receivers))
            receivers.sort()
            share_data(
                client=client,
                receivers=receivers,
                action="update",
                action_type="count",
                data="ask"
            )
            text = (f"管理：{user_mention(uid)}\n"
                    f"操作：{code('更新计数')}\n"
                    f"状态：{code('已请求')}\n")
            thread(send_message, (client, cid, text, mid))

            return True
        except Exception as e:
            logger.warning(f"Count words error: {e}", exc_info=True)
        finally:
            glovar.locks["regex"].release()

    return False


@Client.on_message(Filters.incoming & Filters.group & regex_group & from_user
                   & Filters.command(glovar.list_commands, glovar.prefix))
def list_words(client: Client, message: Message) -> bool:
    # List words
    try:
        cid = message.chat.id
        mid = message.message_id
        text, markup = words_list(message)
        thread(send_message, (client, cid, text, mid, markup))

        return True
    except Exception as e:
        logger.warning(f"List words error: {e}", exc_info=True)

    return False


@Client.on_message(Filters.incoming & Filters.group & regex_group & from_user
                   & Filters.command(["page"], glovar.prefix))
def page_word(client: Client, message: Message) -> bool:
    # Change words page
    try:
        cid = message.chat.id
        mid = message.message_id
        uid = message.from_user.id
        text = f"管理：{user_mention(uid)}\n"
        command_type = get_command_type(message)
        if command_type and command_type in {"previous", "next"}:
            if message.reply_to_message:
                r_message = message.reply_to_message
                aid = get_admin(r_message)
                if uid == aid:
                    pass
                    callback_data_list = get_callback_data(r_message)
                    if (r_message.from_user.is_self
                            and callback_data_list
                            and ((command_type == "previous" and callback_data_list[0]["a"] in {"list", "search"})
                                 or (command_type == "next" and callback_data_list[-1]["a"] in {"list", "search"}))):
                        r_mid = r_message.message_id
                        if command_type == "previous":
                            i = 0
                        else:
                            i = -1

                        action = callback_data_list[i]["a"]
                        action_type = callback_data_list[i]["t"]
                        page = callback_data_list[i]["d"]
                        if action == "list":
                            word_type = action_type
                            desc = get_desc(r_message)
                            page_text, markup = words_list_page(uid, word_type, page, desc)
                        else:
                            search_key = action_type
                            page_text, markup = words_search_page(uid, search_key, page)

                        thread(edit_message_text, (client, cid, r_mid, page_text, markup))
                        text += (f"状态：{code('已更新')}\n"
                                 f"查看：{general_link(r_mid, message_link(r_message))}\n")
                    else:
                        text += (f"状态：{code('未更新')}\n"
                                 f"原因：{code('来源有误')}\n")
                else:
                    text += (f"状态：{code('未更新')}\n"
                             f"原因：{code('权限有误')}\n")
            else:
                text += (f"状态：{code('未更新')}\n"
                         f"原因：{code('用法有误')}\n")
        else:
            text += (f"状态：{code('未更新')}\n"
                     f"原因：{code('格式有误')}\n")

        thread(send_message, (client, cid, text, mid))

        return True
    except Exception as e:
        logger.warning(f"Page word error: {e}", exc_info=True)

    return False


@Client.on_message(Filters.incoming & Filters.group & regex_group & from_user
                   & Filters.command(["push"], glovar.prefix))
def push_words(client: Client, message: Message) -> bool:
    # Push words
    if glovar.locks["regex"].acquire():
        try:
            cid = message.chat.id
            mid = message.message_id
            uid = message.from_user.id
            text = (f"管理：{user_mention(uid)}\n"
                    f"操作：{code('手动推送')}\n")
            command_type = get_command_type(message)
            if command_type and command_type in glovar.names:
                share_regex_update(client, command_type)
                text += (f"类别：{code(glovar.names[command_type])}\n"
                         f"状态：{code('已推送')}\n")
            elif command_type == "all":
                for word_type in glovar.names:
                    thread(share_regex_update, (client, word_type))

                text += (f"类别：{code('全部')}\n"
                         f"状态：{code('已推送')}\n")
            else:
                text += (f"类别：{code(command_type or '未知')}\n"
                         f"状态：{code('未推送')}\n"
                         f"原因：{code('格式有误')}\n")

            thread(send_message, (client, cid, text, mid))

            return True
        except Exception as e:
            logger.warning(f"Push words error: {e}", exc_info=True)
        finally:
            glovar.locks["regex"].release()

    return False


@Client.on_message(Filters.incoming & Filters.group & regex_group & from_user
                   & Filters.command(glovar.remove_commands, glovar.prefix))
def remove_word(client: Client, message: Message) -> bool:
    # Remove a word
    if glovar.locks["regex"].acquire():
        try:
            cid = message.chat.id
            mid = message.message_id
            text = word_remove(client, message)
            thread(send_message, (client, cid, text, mid))

            return True
        except Exception as e:
            logger.warning(f"Remove word error: {e}", exc_info=True)
        finally:
            glovar.locks["regex"].release()

    return False


@Client.on_message(Filters.incoming & Filters.group & regex_group & from_user
                   & Filters.command(["reset"], glovar.prefix))
def reset_words(client: Client, message: Message) -> bool:
    # Push words
    if glovar.locks["regex"].acquire():
        try:
            cid = message.chat.id
            mid = message.message_id
            uid = message.from_user.id
            text = (f"管理：{user_mention(uid)}\n"
                    f"操作：{code('清除计数')}\n")
            command_type = get_command_type(message)
            if command_type and command_type in ["all"] + list(glovar.names):
                if command_type == "all":
                    type_list = list(glovar.names)
                else:
                    type_list = [command_type]

                for word_type in type_list:
                    for word in list(eval(f"glovar.{word_type}_words")):
                        eval(f"glovar.{word_type}_words")[word] = deepcopy(glovar.default_word_status)

                    save(f"{word_type}_words")

                text += (f"类别：{code((lambda t: glovar.names[t] if t != 'all' else '全部')(command_type))}\n"
                         f"状态：{code('已清除')}\n")
            else:
                text += (f"类别：{code(command_type or '未知')}\n"
                         f"状态：{code('未清除')}\n"
                         f"原因：{code('格式有误')}\n")

            thread(send_message, (client, cid, text, mid))

            return True
        except Exception as e:
            logger.warning(f"Reset words error: {e}", exc_info=True)
        finally:
            glovar.locks["regex"].release()

    return False


@Client.on_message(Filters.incoming & Filters.group & regex_group & from_user
                   & Filters.command(glovar.same_commands, glovar.prefix))
def same_words(client: Client, message: Message) -> bool:
    # Same with other types
    if glovar.locks["regex"].acquire():
        try:
            cid = message.chat.id
            mid = message.message_id
            uid = message.from_user.id
            text = f"管理：{user_mention(uid)}\n"
            # Get this new command's list
            new_command_list = list(filter(None, message.command))
            new_word_type_list = new_command_list[1:]
            # Check new command's format
            if (len(new_command_list) > 1
                    and all([new_word_type in glovar.names for new_word_type in new_word_type_list])):
                if message.reply_to_message:
                    old_message = message.reply_to_message
                    aid = old_message.from_user.id
                    # Check permission
                    if uid == aid:
                        old_command_list = list(filter(None, get_text(old_message).split(" ")))
                        old_command_type = old_command_list[0][1:]
                        # Check old command's format
                        if (len(old_command_list) > 2
                                and old_command_type in glovar.add_commands + glovar.remove_commands):
                            _, old_word = get_command_context(old_message)
                            for new_word_type in new_word_type_list:
                                old_message.text = f"{old_command_type} {new_word_type} {old_word}"
                                if old_command_type in glovar.add_commands:
                                    text, markup = word_add(client, old_message)
                                    thread(send_message, (client, cid, text, mid, markup))
                                else:
                                    text = word_remove(client, old_message)
                                    thread(send_message, (client, cid, text, mid))

                            return True
                        # If origin old message just simply "/rm", bot should check which message it replied to
                        elif (old_command_type in glovar.remove_commands
                              and len(old_command_list) == 1):
                            # Get the message replied by old message
                            old_message = get_messages(client, cid, [old_message.message_id])[0]
                            if old_message.reply_to_message:
                                old_message = old_message.reply_to_message
                                aid = old_message.from_user.id
                                # Check permission
                                if uid == aid:
                                    old_command_list = list(filter(None, get_text(old_message).split(" ")))
                                    old_command_type = old_command_list[0][1:]
                                    if (len(old_command_list) > 2
                                            and old_command_type in glovar.add_commands):
                                        _, old_word = get_command_context(old_message)
                                        for new_word_type in new_word_type_list:
                                            old_message.text = f"{old_command_type} {new_word_type} {old_word}"
                                            text = word_remove(client, old_message)
                                            thread(send_message, (client, cid, text, mid))

                                        return True
                                    else:
                                        text += (f"状态：{code('未执行')}\n"
                                                 f"原因：{code('二级来源有误')}\n")
                                else:
                                    text += (f"状态：{code('未执行')}\n"
                                             f"原因：{code('权限错误')}\n")
                            else:
                                text += (f"状态：{code('未执行')}\n"
                                         f"原因：{code('来源有误')}\n")
                        else:
                            text += (f"状态：{code('未执行')}\n"
                                     f"原因：{code('来源有误')}\n")
                    else:
                        text += (f"状态：{code('未执行')}\n"
                                 f"原因：{code('权限错误')}\n")
                else:
                    text += (f"状态：{code('未执行')}\n"
                             f"原因：{code('操作有误')}\n")
            else:
                text += (f"状态：{code('未执行')}\n"
                         f"原因：{code('格式有误')}\n")

            thread(send_message, (client, cid, text, mid))

            return True
        except Exception as e:
            logger.warning(f"Same words error: {e}", exc_info=True)
        finally:
            glovar.locks["regex"].release()

    return False


@Client.on_message(Filters.incoming & Filters.group & regex_group & from_user
                   & Filters.command(glovar.search_commands, glovar.prefix))
def search_words(client: Client, message: Message) -> bool:
    # Search words
    try:
        cid = message.chat.id
        mid = message.message_id
        text, markup = words_search(message)
        thread(send_message, (client, cid, text, mid, markup))

        return True
    except Exception as e:
        logger.warning(f"Search words error: {e}", exc_info=True)

    return False


@Client.on_message(Filters.incoming & Filters.group & test_group & from_user
                   & Filters.command(["version"], glovar.prefix))
def version(client: Client, message: Message) -> bool:
    # Check the program's version
    try:
        cid = message.chat.id
        aid = message.from_user.id
        mid = message.message_id
        text = (f"管理员：{user_mention(aid)}\n\n"
                f"版本：{bold(glovar.version)}\n")
        thread(send_message, (client, cid, text, mid))

        return True
    except Exception as e:
        logger.warning(f"Version error: {e}", exc_info=True)

    return False
