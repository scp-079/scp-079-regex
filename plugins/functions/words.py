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
from typing import Any, List, Optional

from pyrogram import Client, InlineKeyboardMarkup, InlineKeyboardButton, Message
from xeger import Xeger

from .. import glovar
from .channel import share_regex_update
from .etc import code, button_data, get_command_context, get_now, get_text, italic, random_str
from .etc import user_mention
from .file import save, save_thread

# Enable logging
logger = logging.getLogger(__name__)

# Xeger config
xg = Xeger(limit=32)


def add_word(word_type: str, word: str) -> bool:
    # Add a word
    try:
        eval(f"glovar.{word_type}_words")[word] = deepcopy(glovar.default_word_status)
        save_thread(f"{word_type}_words")
        # TEMP
        re_compile(word_type)

        return True
    except Exception as e:
        logger.warning(f"Add word error: {e}", exc_info=True)

    return False


def get_admin(message: Message) -> Optional[int]:
    # Get message's origin commander
    try:
        aid = int(message.text.split("\n")[0].split("：")[1])

        return aid
    except Exception as e:
        logger.warning(f"Get admin error: {e}", exc_info=True)

    return None


def get_desc(message: Message) -> bool:
    # Get the list message's desc value
    try:
        text_list = message.text.split("\n")
        for text in text_list:
            text_units = text.split("：")
            if text_units[0] == "顺序":
                if text_units[1] == "升序":
                    return False
                else:
                    return True
    except Exception as e:
        logger.warning(f"Get desc error: {e}", exc_info=True)

    return True


def remove_word(word_type: str, words: List[str]) -> bool:
    # Remove a word
    try:
        for word in words:
            eval(f"glovar.{word_type}_words").pop(word, {})

        save_thread(f"{word_type}_words")
        # TEMP
        re_compile(word_type)

        return True
    except Exception as e:
        logger.warning(f"Remove word error: {e}", exc_info=True)

    return False


def re_compile(word_type: str) -> bool:
    # Re compile the regex
    try:
        text = '|'.join(list(eval(f"glovar.{word_type}_words")))
        if text != "":
            glovar.compiled[word_type] = re.compile(text, re.I | re.S | re.M)
        else:
            glovar.compiled[word_type] = re.compile(fr"预留{glovar.names[f'{word_type}']}词组 {random_str(16)}",
                                                    re.I | re.M | re.S)

        save("compiled")

        return True
    except Exception as e:
        logger.warning(f"Re compile error: {e}")

    return False


def similar(mode: str, a: str, b: str) -> bool:
    # Check similar pattern, use strict mode to get more accurate
    if mode == "strict":
        i = 0
        while i < 3:
            if not (re.search(a, xg.xeger(b), re.I | re.M | re.S)
                    or re.search(b, xg.xeger(a), re.I | re.M | re.S)):
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


def word_add(client: Client, message: Message) -> (str, InlineKeyboardMarkup):
    # Add a word
    uid = message.from_user.id
    text = f"管理：{user_mention(uid)}\n"
    # Check if the command format is correct
    word_type, word = get_command_context(message)
    if word_type:
        if word and word_type in glovar.names:
            # Check if the word already exits
            if "(?#" in word and "(?# " not in word:
                word = word.replace("(?#", "(?# ")

            if eval(f"glovar.{word_type}_words").get(word, {}):
                text += (f"状态：{code('未添加')}\n"
                         f"类别：{code(glovar.names[word_type])}\n"
                         f"词组：{code(word)}\n"
                         f"原因：{code('已存在')}")
                markup = None
            else:
                # Check if the pattern is correct
                try:
                    pattern = re.compile(word, re.I | re.M | re.S)
                except Exception as e:
                    text += (f"状态：{code('未添加')}\n"
                             f"类别：{code(glovar.names[word_type])}\n"
                             f"词组：{code(word)}\n"
                             f"原因：{code('出现错误')}\n"
                             f"错误：{code(e)}")
                    markup = None
                    return text, markup

                # Check if the pattern is special
                for test in ["项脊轩，旧南阁子也。室仅方丈，可容一人居。",
                             "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                             "0123456789",
                             "abcdefjghijklmnopqrstuvwxyz"
                             ]:
                    if pattern.search(test):
                        text += (f"状态：{code('未添加')}\n"
                                 f"类别：{code(glovar.names[word_type])}\n"
                                 f"词组：{code(word)}\n"
                                 f"原因：{code('不具有特殊性')}")
                        markup = None
                        return text, markup

                # Check similar patterns
                ask_key = random_str(8)
                while glovar.ask_words.get(ask_key):
                    ask_key = random_str(8)

                glovar.ask_words[ask_key] = {
                    "new": word,
                    "old": [],
                    "type": word_type
                }
                for old in list(eval(f"glovar.{word_type}_words")):
                    if similar("strict", old, word):
                        glovar.ask_words[ask_key]["old"].append(old)

                if glovar.ask_words[ask_key]["old"]:
                    end_text = "\n\n".join([code(w) for w in glovar.ask_words[ask_key]["old"]])
                    text += (f"状态：{code('未添加')}\n"
                             f"类别：{code(glovar.names[word_type])}\n"
                             f"词组：{code(word)}\n"
                             f"原因：{code('等待确认')}\n"
                             f"重复：" + "-" * 24 + f"\n\n{end_text}")
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
                    add_word(word_type, word)
                    share_regex_update(client, word_type)
                    text += (f"状态：{code(f'已添加')}\n"
                             f"类别：{code(glovar.names[word_type])}\n"
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


def words_ask(client: Client, operation: str, key: str) -> str:
    # Handle the reply to bot's asked question
    if key in glovar.ask_words:
        word_type = glovar.ask_words[key]["type"]
        new_word = glovar.ask_words[key]["new"]
        old_words = glovar.ask_words[key]["old"]
        text = (f"类别：{code(f'{glovar.names[word_type]}')}\n"
                f"词组：{code(new_word)}\n")
        end_text = "\n\n".join([code(w) for w in glovar.ask_words[key]["old"]])
        # If admin decide to add new word
        if operation == "new":
            add_word(word_type, new_word)
            share_regex_update(client, word_type)
            begin_text = f"状态：{code(f'已添加')}\n"
            text = begin_text + text + "重复：" + "-" * 24 + f"\n\n{end_text}"
        # Else delete old words
        elif operation == "replace":
            add_word(word_type, new_word)
            remove_word(word_type, old_words)
            share_regex_update(client, word_type)
            begin_text = f"状态：{code(f'已添加')}\n"
            text = begin_text + text + "替换：" + "-" * 24 + f"\n\n{end_text}"
        else:
            begin_text = f"状态：{code(f'已取消')}\n"
            text = begin_text + text + "重复：" + "-" * 24 + f"\n\n{end_text}"

        glovar.ask_words.pop(key, None)
    else:
        text = (f"状态：{code('未添加')}\n"
                f"原因：{code('会话失效')}")

    return text


def words_count(word_type: str, data: Any) -> bool:
    # Calculate the rules' usage
    if glovar.lock["count"].acquire():
        try:
            if data:
                data_set = set(data)
                word_set = set(eval(f"glovar.{word_type}_words"))
                the_set = data_set & word_set
                for word in the_set:
                    eval(f"glovar.{word_type}_words")[word]["today"] = data[word]
                    eval(f"glovar.{word_type}_words")[word]["total"] += data[word]
                    total = eval(f"glovar.{word_type}_words")[word]["total"]
                    time = get_now() - eval(f"glovar.{word_type}_words")[word]["time"]
                    eval(f"glovar.{word_type}_words")[word]["average"] = total / (time / 86400)

                save(f"{word_type}_words")

                return True
        except Exception as e:
            logger.warning(f"Words count error: {e}", exc_info=True)
        finally:
            glovar.lock["count"].release()

    return False


def words_list(message: Message) -> (str, InlineKeyboardMarkup):
    # List words
    uid = message.from_user.id
    text = f"管理：{user_mention(uid)}\n"
    command_list = list(filter(None, get_text(message).split(" ")))
    if len(command_list) > 1:
        word_type = command_list[1]
        desc = True
        if len(command_list) > 2:
            if command_list[2] == "asc":
                desc = False

        if word_type in glovar.names:
            text, markup = words_list_page(uid, word_type, 1, desc)
        else:
            text += (f"类别：{code(glovar.names.get(word_type, word_type))}\n"
                     f"顺序：{code((lambda x: '降序' if x else '升序')(desc))}\n"
                     f"结果：{code('无法显示')}\n"
                     f"原因：{code('格式有误')}\n")
            markup = None
    else:
        text += (f"结果：{code('无法显示')}\n"
                 f"原因：{code('格式有误')}\n"
                 f"可选：" + "-" * 24 + "\n\n" +
                 f"\n".join([f"{code(name)}    {italic(glovar.names[name])}" for name in glovar.names]))
        markup = None

    return text, markup


def words_list_page(uid: int, word_type: str, page: int, desc: bool) -> (str, InlineKeyboardMarkup):
    # Generate a words list page
    text = f"管理：{user_mention(uid)}\n"
    words = eval(f"glovar.{word_type}_words")
    keys = list(words.keys())
    keys.sort()
    w_list = sorted(keys, key=lambda k: words[k]["average"], reverse=desc)
    w_list, markup = words_page(w_list, "list", word_type, page)
    text += (f"类别：{code(glovar.names[word_type])}\n"
             f"顺序：{code((lambda x: '降序' if x else '升序')(desc))}\n"
             f"查询：{code('全部')}\n"
             f"结果：" + "-" * 24 + "\n\n" +
             f"\n\n".join([(f"{code(w)}\n{italic(round(words[w]['average'], 1))} "
                            f"{code('/')} {italic(words[w]['today'])} "
                            f"{code('/')} {italic(words[w]['total'])}")
                           for w in w_list]))

    return text, markup


def words_page(w_list: list, action: str, action_type: str, page: int) -> (list, InlineKeyboardMarkup):
    # Generate a list for words and markup buttons
    markup = None
    # Get page count
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


def word_remove(client: Client, message: Message) -> str:
    # Remove a word
    uid = message.from_user.id
    text = word_remove_try(client, message)
    if text:
        return text
    elif message.reply_to_message:
        aid = message.reply_to_message.from_user.id
        if uid == aid:
            r_text = word_remove_try(client, message.reply_to_message)
            if r_text:
                return r_text
        else:
            text = (f"管理：{user_mention(uid)}\n"
                    f"状态：{code('未移除')}\n"
                    f"原因：{code('权限错误')}")
            return text

    text = (f"管理：{user_mention(uid)}\n"
            f"状态：{code('未移除')}\n"
            f"原因：{code('格式有误')}")

    return text


def word_remove_try(client: Client, message: Message) -> Optional[str]:
    # Try to remove a word
    uid = message.from_user.id
    text = f"管理：{user_mention(uid)}\n"
    # Check if the command format is correct
    word_type, word = get_command_context(message)
    if word_type:
        if word and word_type in glovar.names:
            if "(?#" in word and "(?# " not in word:
                word = word.replace("(?#", "(?# ")

            if eval(f"glovar.{word_type}_words").get(word, {}):
                remove_word(word_type, [word])
                text += (f"状态：{code(f'已移除')}\n"
                         f"类别：{code(f'{glovar.names[word_type]}')}\n"
                         f"词组：{code(word)}")
                share_regex_update(client, word_type)
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
        text = None

    return text


def words_search(message: Message) -> (str, InlineKeyboardMarkup):
    # Search words
    uid = message.from_user.id
    text = f"管理：{user_mention(uid)}\n"
    markup = None
    # Check if the command format is correct
    word_type, word = get_command_context(message)
    if word_type:
        if (word and (word_type in list(glovar.names) + ["all"])
                or (not word and word_type not in list(glovar.names) + ["all"])):
            if not word:
                word = word_type
                word_type = "all"

            search_key = random_str(8)
            while search_key in glovar.result_search:
                search_key = random_str(8)

            glovar.result_search[search_key] = {
                "result": {},
                "type": word_type,
                "word": word
            }
            result = {}
            if word_type != "all":
                result = {w: [] for w in list(eval(f"glovar.{word_type}_words"))
                          if similar("loose", w, word)}
            else:
                for n in glovar.names:
                    for w in list(eval(f"glovar.{n}_words")):
                        if similar("loose", w, word):
                            if result.get(w) is None:
                                result[w] = []

                            result[w].append(n)

            glovar.result_search[search_key]["result"] = result
            text, markup = words_search_page(uid, search_key, 1)
        else:
            text += (f"类别：{code(glovar.names.get(word_type, word_type))}\n"
                     f"结果：{code('无法显示')}\n"
                     f"原因：{code('格式有误')}")
    else:
        text += (f"结果：{code('无法显示')}\n"
                 f"原因：{code('格式有误')}")

    return text, markup


def words_search_page(uid: int, key: str, page: int) -> (str, InlineKeyboardMarkup):
    # Generate searched words page
    text = f"管理：{user_mention(uid)}\n"
    if key in glovar.result_search:
        word_type = glovar.result_search[key]["type"]
        word = glovar.result_search[key]["word"]
        text += (f"类别：{code(glovar.names.get(word_type, '全部'))}\n"
                 f"查询：{code(word)}\n")
        markup = None
        words = glovar.result_search[key]["result"]
        if words:
            w_list = list(words)
            w_list.sort()
            w_list, markup = words_page(w_list, "search", key, page)
            if word_type == "all":
                end_text = ""
                for w in w_list:
                    end_text += (f"{code(w)}\n\n"
                                 + "\t" * 4
                                 + italic("，".join([glovar.names[t]
                                                    for t in glovar.result_search[key]['result'][w]]))
                                 + "\n\n")

                end_text = end_text[:-2]
            else:
                end_text = "\n\n".join([f"{code(w)}" for w in w_list])

            text += "结果：" + "-" * 24 + f"\n\n{end_text}"
        else:
            text += (f"结果：{code('无法显示')}\n"
                     f"原因：{code('没有找到')}")
    else:
        text += (f"结果：{code('无法显示')}\n"
                 f"原因：{code('会话失效')}")
        markup = None

    return text, markup
