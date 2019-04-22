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
from time import sleep

from pyrogram import Client, InlineKeyboardMarkup, InlineKeyboardButton, Message
from xeger import Xeger

from .. import glovar
from .etc import code, crypt_str, button_data, get_text, delay, italic, random_str, send_data, thread, user_mention
from .files import crypt_file, save
from .telegram import send_document, send_message

# Enable logging
logger = logging.getLogger(__name__)

# Xeger config
xg = Xeger(limit=32)


def data_exchange(client: Client):
    try:
        receivers = glovar.update_to
        if glovar.update_type == "reload":
            exchange_text = send_data(
                sender="REGEX",
                receivers=receivers,
                action="update",
                action_type="reload",
                data=crypt_str("encrypt", glovar.reload_path, glovar.key)
            )
            delay(5, send_message, [client, glovar.exchange_channel_id, exchange_text])
        else:
            exchange_text = send_data(
                sender="REGEX",
                receivers=receivers,
                action="update",
                action_type="download",
                data=crypt_str("encrypt", glovar.reload_path, glovar.key)
            )
            sleep(5)
            crypt_file("encrypt", "data/compiled", "tmp/compiled")
            thread(send_document, (client, glovar.exchange_channel_id, "tmp/compiled", exchange_text))
    except Exception as e:
        logger.warning(f"Data exchange error: {e}")


def get_type(command_list: list) -> (int, str):
    i = 1
    word_type = command_list[i]
    while word_type == "" and i < len(command_list):
        i += 1
        word_type = command_list[i]

    return i, word_type


def re_compile(word_type: str):
    text = '|'.join(eval(f"glovar.{word_type}_words"))
    if text != "":
        glovar.compiled[word_type] = re.compile(fr"{text}", re.I | re.S | re.M)
    else:
        glovar.compiled[word_type] = re.compile(fr"预留{glovar.names[f'{word_type}']}词组 {random_str(16)}",
                                                re.I | re.M | re.S)

    save("compiled")
    save(f"{word_type}_words")


def similar(mode: str, a: str, b: str) -> bool:
    if mode == "strict":
        i = 0
        while i < 3:
            if not (re.search(a, xg.xeger(b), re.I | re.M | re.S) or re.search(b, xg.xeger(a), re.I | re.M | re.S)):
                return False

            i += 1
    elif mode == "loose":
        if not (re.search(a, b, re.I | re.M | re.S)
                or re.search(b, a, re.I | re.M | re.S)
                or re.search(a, xg.xeger(b), re.I | re.M | re.S)
                or re.search(b, xg.xeger(a), re.I | re.M | re.S)):
            return False
    else:
        if not re.search(a, b, re.I | re.M | re.S):
            return False

    return True


def words_add(message: Message) -> (str, InlineKeyboardMarkup):
    uid = message.from_user.id
    text = f"管理：{user_mention(uid)}\n"
    command_list = message.command
    # Check if the command format is correct
    if len(command_list) > 1:
        i, word_type = get_type(command_list)
        if len(command_list) > 2 and word_type in glovar.names:
            word = get_text(message)[1 + len(command_list[0]) + i + len(command_list[1]):].strip()
            # Check if the word already exits
            if word in eval(f"glovar.{word_type}_words"):
                text += (f"状态：{code('未添加')}\n"
                         f"类别：{code(f'{glovar.names[word_type]}')}\n"
                         f"词组：{code(word)}\n"
                         f"原因：{code('已存在')}")
                markup = None
            else:
                # Check if the pattern is correct
                try:
                    pattern = re.compile(word, re.I | re.M | re.S)
                except Exception as e:
                    text += (f"状态：{code('未添加')}\n"
                             f"类别：{code(f'{glovar.names[word_type]}')}\n"
                             f"词组：{code(word)}\n"
                             f"原因：{code('出现错误')}\n"
                             f"错误：{code(e)}")
                    markup = None
                    return text, markup

                # Check if the pattern is special
                for test in ["项脊轩，旧南阁子也。室仅方丈，可容一人居。",
                             "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                             "0123456789"
                             ]:
                    if pattern.search(test):
                        text += (f"状态：{code('未添加')}\n"
                                 f"类别：{code(f'{glovar.names[word_type]}')}\n"
                                 f"词组：{code(word)}\n"
                                 f"原因：{code('不具有特殊性')}")
                        markup = None
                        return text, markup

                # Check similar patterns
                ask_key = random_str(8)
                while ask_key in glovar.ask_words:
                    ask_key = random_str(8)

                glovar.ask_words[ask_key] = {
                    "type": word_type,
                    "new": word,
                    "old": []
                }
                for old in eval(f"glovar.{word_type}_words"):
                    if similar("strict", old, word):
                        glovar.ask_words[ask_key]["old"].append(old)

                if glovar.ask_words[ask_key]["old"]:
                    end_text = "\n\n".join([code(w) for w in glovar.ask_words[ask_key]["old"]])
                    text += (f"状态：{code('未添加')}\n"
                             f"类别：{code(f'{glovar.names[word_type]}')}\n"
                             f"词组：{code(word)}\n"
                             f"原因：{code('等待确认')}\n"
                             f"重复：------------------------\n\n{end_text}")
                    add_new = button_data("ask", "new", ask_key)
                    replace_all = button_data("ask", "replace", ask_key)
                    cancel = button_data("ask", "cancel", ask_key)
                    markup = InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "另增新词",
                                    callback_data=add_new
                                ),
                                InlineKeyboardButton(
                                    "替换全部",
                                    callback_data=replace_all
                                )
                            ],
                            [
                                InlineKeyboardButton(
                                    "取消",
                                    callback_data=cancel
                                )
                            ]
                        ]
                    )
                else:
                    glovar.ask_words.pop(ask_key, None)
                    eval(f"glovar.{word_type}_words").add(word)
                    re_compile(word_type)
                    text += (f"状态：{code(f'已添加')}\n"
                             f"类别：{code(f'{glovar.names[word_type]}')}\n"
                             f"词组：{code(word)}")
                    markup = None
        else:
            text += (f"类别：{code(glovar.names.get(word_type, word_type))}\n"
                     f"状态：{code('未添加')}\n"
                     f"原因：{code('格式有误')}")
            markup = None
    else:
        text += (f"状态：{code('未添加')}\n"
                 f"原因：{code('格式有误')}")
        markup = None

    return text, markup


def words_ask(operation: str, key: str) -> str:
    if key in glovar.ask_words:
        word_type = glovar.ask_words[key]["type"]
        new_word = glovar.ask_words[key]["new"]
        old_words = glovar.ask_words[key]["old"]
        text = ""
        for old in glovar.ask_words[key]["old"]:
            text += f"{code(old)}\n\n"

        text = text[:-2]
        if operation == "new":
            eval(f"glovar.{word_type}_words").add(new_word)
            re_compile(word_type)
            text = (f"状态：{code(f'已添加')}\n"
                    f"类别：{code(f'{glovar.names[word_type]}')}\n"
                    f"词组：{code(new_word)}\n"
                    f"重复：------------------------\n\n{text}")
        elif operation == "replace":
            eval(f"glovar.{word_type}_words").add(new_word)
            for old in old_words:
                eval(f"glovar.{word_type}_words").discard(old)

            re_compile(word_type)
            text = (f"状态：{code(f'已添加')}\n"
                    f"类别：{code(f'{glovar.names[word_type]}')}\n"
                    f"词组：{code(new_word)}\n"
                    f"替换：------------------------\n\n{text}")
        else:
            text = (f"状态：{code(f'已取消')}\n"
                    f"类别：{code(f'{glovar.names[word_type]}')}\n"
                    f"词组：{code(new_word)}\n"
                    f"重复：------------------------\n\n{text}")

        glovar.ask_words.pop(key, None)
    else:
        text = (f"状态：{code('未添加')}\n"
                f"原因：{code('会话失效')}")

    return text


def words_list(message: Message) -> (str, InlineKeyboardMarkup):
    uid = message.from_user.id
    text = f"管理：{user_mention(uid)}\n"
    command_list = list(filter(None, message.command))
    if len(command_list) > 1:
        word_type = command_list[1]
        if word_type in glovar.names:
            text, markup = words_list_page(uid, word_type, 1)
        else:
            text += (f"类别：{code(glovar.names.get(word_type, word_type))}\n"
                     f"结果：{code('无法显示')}\n"
                     f"原因：{code('格式有误')}")
            markup = None
    else:
        text += (f"结果：{code('无法显示')}\n"
                 f"原因：{code('格式有误')}")
        markup = None

    return text, markup


def words_list_page(uid, word_type, page) -> (str, InlineKeyboardMarkup):
    text = f"管理：{user_mention(uid)}\n"
    words = eval(f"glovar.{word_type}_words")
    w_list = list(words)
    w_list.sort()
    w_list, markup = words_page(w_list, "list", word_type, page)
    end_text = "\n\n".join([code(w) for w in w_list])
    text += (f"类别：{code(glovar.names[word_type])}\n"
             f"查询：{code('全部')}\n"
             f"结果：------------------------\n\n{end_text}")

    return text, markup


def words_page(w_list: list, action: str, action_type: str, page: int) -> (list, InlineKeyboardMarkup):
    markup = None
    quo = int(len(w_list) / glovar.per_page)
    if quo != 0:
        page_count = quo + 1
        if len(w_list) % glovar.per_page == 0:
            page_count = page_count - 1

        if page != page_count:
            w_list = w_list[(page - 1) * glovar.per_page:page * glovar.per_page]
        else:
            w_list = w_list[(page - 1) * glovar.per_page:len(w_list)]
        if page_count > 1:
            if page == 1:
                markup = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                f"第 {page} 页",
                                callback_data=button_data("none")
                            ),
                            InlineKeyboardButton(
                                ">>",
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
                                "<<",
                                callback_data=button_data(action, action_type, page - 1)
                            ),
                            InlineKeyboardButton(
                                f"第 {page} 页",
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
                                "<<",
                                callback_data=button_data(action, action_type, page - 1)
                            ),
                            InlineKeyboardButton(
                                f"第 {page} 页",
                                callback_data=button_data("none")
                            ),
                            InlineKeyboardButton(
                                '>>',
                                callback_data=button_data(action, action_type, page + 1)
                            )
                        ]
                    ]
                )

    return w_list, markup


def words_remove(message: Message) -> str:
    uid = message.from_user.id
    text = f"管理：{user_mention(uid)}\n"
    command_list = message.command
    # Check if the command format is correct
    if len(command_list) > 1:
        i, word_type = get_type(command_list)
        if len(command_list) > 2 and word_type in glovar.names:
            word = get_text(message)[1 + len(command_list[0]) + i + len(command_list[1]):].strip()
            if word in eval(f"glovar.{word_type}_words"):
                eval(f"glovar.{word_type}_words").discard(word)
                re_compile(word_type)
                text += (f"状态：{code(f'已移除')}\n"
                         f"类别：{code(f'{glovar.names[word_type]}')}\n"
                         f"词组：{code(word)}")
            else:
                text += (f"状态：{code('未移除')}\n"
                         f"类别：{code(f'{glovar.names[word_type]}')}\n"
                         f"词组：{code(word)}\n"
                         f"原因：{code('不存在')}")
        else:
            text += (f"类别：{code(glovar.names.get(word_type, word_type))}\n"
                     f"状态：{code('未移除')}\n"
                     f"原因：{code('格式有误')}")
    else:
        text += (f"状态：{code('未移除')}\n"
                 f"原因：{code('格式有误')}")

    return text


def words_search(message: Message) -> (str, InlineKeyboardMarkup):
    uid = message.from_user.id
    text = f"管理：{user_mention(uid)}\n"
    markup = None
    command_list = message.command
    if len(command_list) > 1:
        i, word_type = get_type(command_list)
        if len(command_list) > 2 and (word_type in glovar.names or word_type == "all"):
            word = get_text(message)[1 + len(command_list[0]) + i + len(command_list[1]):].strip()
            search_key = random_str(8)
            while search_key in glovar.ask_words:
                search_key = random_str(8)

            glovar.search_words[search_key] = {
                "type": word_type,
                "word": word,
                "result": {}
            }
            result = {}
            if word_type != "all":
                result = {w: [] for w in eval(f"glovar.{word_type}_words")
                          if similar("loose", w, word)}
            else:
                for n in glovar.names:
                    for w in eval(f"glovar.{n}_words"):
                        if similar("loose", w, word):
                            if result.get(w) is None:
                                result[w] = []

                            result[w].append(n)

            glovar.search_words[search_key]["result"] = result
            text, markup = words_search_page(uid, search_key, 1)
        else:
            text += (f"类别：{code(glovar.names.get(word_type, word_type))}\n"
                     f"结果：{code('无法显示')}\n"
                     f"原因：{code('格式有误')}")
    else:
        text = (f"结果：{code('无法显示')}\n"
                f"原因：{code('格式有误')}")

    return text, markup


def words_search_page(uid: int, key: str, page: int) -> (str, InlineKeyboardMarkup):
    if key in glovar.search_words:
        word_type = glovar.search_words[key]["type"]
        word = glovar.search_words[key]["word"]
        text = f"管理：{user_mention(uid)}\n"
        markup = None
        words = glovar.search_words[key]["result"]
        if words:
            w_list = list(words)
            w_list.sort()
            w_list, markup = words_page(w_list, "search", key, page)
            if word_type == "all":
                end_text = ""
                for w in w_list:
                    end_text += (f"{code(w)}\n\n"
                                 + "\t" * 4
                                 + "，".join([f"{italic(glovar.names[t])}"
                                             for t in glovar.search_words[key]['result'][w]])
                                 + "\n\n")

                end_text = end_text[:-2]
            else:
                end_text = "\n\n".join([f"{code(w)}" for w in w_list])

            text += (f"类别：{code(glovar.names.get(word_type, '全部'))}\n"
                     f"查询：{code(word)}\n"
                     f"结果：------------------------\n\n{end_text}")
        else:
            text += (f"类别：{code(glovar.names.get(word_type, '全部'))}\n"
                     f"查询：{code(word)}\n"
                     f"结果：{code('无法显示')}\n"
                     f"原因：{code('没有找到')}")
    else:
        text = (f"结果：{code('无法显示')}\n"
                f"原因：{code('会话失效')}")
        markup = None

    return text, markup
