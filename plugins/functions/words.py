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
from typing import List, Optional, Set

from pyrogram import Client, InlineKeyboardMarkup, InlineKeyboardButton, Message

from .. import glovar
from .channel import share_regex_update
from .etc import code, button_data, get_command_context, get_int, get_list_page, get_now, get_text, italic, lang
from .etc import mention_id, random_str, thread
from .file import save, save_thread
from .filters import is_similar
from .telegram import send_message

# Enable logging
logger = logging.getLogger(__name__)


def add_word(word_type: str, word: str, aid: int) -> bool:
    # Add a word
    try:
        eval(f"glovar.{word_type}_words")[word] = deepcopy(glovar.default_word_status)
        eval(f"glovar.{word_type}_words")[word]["who"] = aid
        save_thread(f"{word_type}_words")

        return True
    except Exception as e:
        logger.warning(f"Add word error: {e}", exc_info=True)

    return False


def cc(client: Client, cc_list: Set[int], aid: int, mid: int) -> bool:
    # CC
    try:
        if not cc_list:
            return True

        # Text prefix
        text = (f"{lang('admin')}{lang('colon')}{mention_id(aid)}\n"
                f"{lang('action')}{lang('colon')}{code(lang('action_cc'))}\n")

        for cc_id in cc_list:
            text += f"{lang('admin')}{lang('colon')}{mention_id(cc_id)}\n"

        thread(send_message, (client, glovar.regex_group_id, text, mid))

        return True
    except Exception as e:
        logger.warning(f"CC error: {e}", exc_info=True)

    return False


def format_word(word: str) -> str:
    # Format a word
    result = word
    try:
        if not word:
            return result

        result = re.sub(r"((?<!\\)|(?<=\\\\))\(\?#\s*", "(?# ", word)
    except Exception as e:
        logger.warning(f"Format word error: {e}", exc_info=True)

    return result


def get_admin(message: Message) -> Optional[int]:
    # Get message's origin commander
    result = None
    try:
        if not message.text:
            return None

        result = get_int(message.text.split("\n")[0].split("：")[1])
    except Exception as e:
        logger.warning(f"Get admin error: {e}", exc_info=True)

    return result


def get_comments(regex: str) -> List[str]:
    # Get comments from the regex
    result = []
    try:
        if not regex:
            return []

        regex_list = regex.split("(?# ")
        regex_list = regex_list[1:]

        for comment in regex_list:
            result.append(comment.split(")")[0].strip())
    except Exception as e:
        logger.warning(f"Get commands error: {e}", exc_info=True)

    return result


def get_desc(message: Message) -> bool:
    # Get the list message's desc value
    try:
        if not message.text:
            return True

        text_list = message.text.split("\n")
        for text in text_list:
            text_units = text.split(f"{lang('colon')}")
            if text_units[0] == lang("order"):
                return text_units[1] == lang("order_desc")
    except Exception as e:
        logger.warning(f"Get desc error: {e}", exc_info=True)

    return True


def get_match(mode: str, regex: str, text: str) -> str:
    # Get match result
    try:
        if mode == "findall":
            match = re.findall(regex, text, re.I | re.M | re.S)
            return str(match)
        else:
            match = re.search(regex, text, re.I | re.M | re.S)

            if not match:
                return "None"

            if mode == "group":
                return str(match.group())
            elif mode == "groupdict":
                return str(match.groupdict())
            elif mode == "groups":
                return str(match.groups())
    except Exception as e:
        logger.warning(f"Get match error: {e}", exc_info=True)

    return "None"


def get_same_types(regex: str) -> Set[str]:
    # Get the same word types from regex
    try:
        comments = get_comments(regex)

        for comment in comments:
            word_list = comment.split()

            if not all(w in glovar.regex for w in word_list):
                continue

            return set(word_list)
    except Exception as e:
        logger.warning(f"Get same types error: {e}", exc_info=True)

    return set()


def remove_word(word_type: str, words: List[str], aid: int) -> Set[int]:
    # Remove a word
    result = set()
    try:
        for word in words:
            word_status = eval(f"glovar.{word_type}_words").pop(word, {})
            result.add(word_status.get("who"))

        save_thread(f"{word_type}_words")
        result.discard(aid)
        result = {cc_id for cc_id in list(result) if cc_id}
    except Exception as e:
        logger.warning(f"Remove word error: {e}", exc_info=True)

    return result


def same_word(client: Client, message: Message, command: str, word: str, word_type_list: Set[str], mid: int) -> bool:
    # Same word
    try:
        for word_type in word_type_list:
            message.text = f"{command} {word_type} {word}"
            if command in glovar.add_commands:
                text, markup = word_add(client, message)
                thread(send_message, (client, glovar.regex_group_id, text, mid, markup))
            else:
                text, cc_list_unit = word_remove(client, message)
                thread(send_message, (client, glovar.regex_group_id, text, mid))

        return True
    except Exception as e:
        logger.warning(f"Same word error: {e}", exc_info=True)

    return False


def word_add(client: Client, message: Message) -> (str, InlineKeyboardMarkup):
    # Add a word
    text = ""
    markup = None
    try:
        # Basic data
        aid = message.from_user.id

        # Text prefix
        text = (f"{lang('admin')}{lang('colon')}{mention_id(aid)}\n"
                f"{lang('action')}{lang('colon')}{code(lang('action_add'))}\n")

        # Check if the command format is correct
        word_type, word = get_command_context(message)
        if not word_type or word_type not in glovar.regex or not word:
            text += (f"{lang('status')}{lang('colon')}{code(lang('status_failed'))}\n"
                     f"{lang('reason')}{lang('colon')}{code(lang('command_usage'))}\n")
            return text, markup

        # Word type and word info text
        text += f"{lang('type')}{lang('colon')}{code(lang(word_type))}\n"

        if glovar.comments.get(word_type):
            text += f"{lang('comment')}{lang('colon')}{code(glovar.comments[word_type])}\n"

        text += f"{lang('word')}{lang('colon')}{code(word)}\n"

        # Check if the word already exits
        word = format_word(word)
        if eval(f"glovar.{word_type}_words").get(word, {}):
            text += (f"{lang('status')}{lang('colon')}{code(lang('status_failed'))}\n"
                     f"{lang('reason')}{lang('colon')}{code(lang('reason_existed'))}\n")
            return text, markup

        # Check if the pattern is correct
        try:
            pattern = re.compile(word, re.I | re.M | re.S)
        except Exception as e:
            text += (f"{lang('status')}{lang('colon')}{code(lang('status_error'))}\n"
                     f"{lang('error')}{lang('colon')}{code(e)}\n")
            return text, markup

        # Check if the pattern is special
        for test in ["项脊轩，旧南阁子也。室仅方丈，可容一人居。",
                     "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                     "0123456789",
                     "abcdefjghijklmnopqrstuvwxyz"
                     ]:
            if pattern.search(test):
                text += (f"{lang('status')}{lang('colon')}{code(lang('status_failed'))}\n"
                         f"{lang('reason')}{lang('colon')}{code(lang('reason_not_specific'))}\n")
                return text, markup

        # Check similar patterns
        key = random_str(8)

        while glovar.ask_words.get(key):
            key = random_str(8)

        glovar.ask_words[key] = {
            "lock": False,
            "time": get_now(),
            "admin": aid,
            "mid": 0,
            "new": word,
            "old": [],
            "type": word_type
        }

        for old in list(eval(f"glovar.{word_type}_words")):
            if is_similar("strict", old, word):
                glovar.ask_words[key]["old"].append(old)

        if glovar.ask_words[key]["old"]:
            end_text = "\n\n".join(code(w) for w in glovar.ask_words[key]["old"])
            text += (f"{lang('status')}{lang('colon')}{code(lang('status_failed'))}\n"
                     f"{lang('reason')}{lang('colon')}{code(lang('reason_wait'))}\n"
                     f"{lang('duplicated')}{lang('colon')}" + "-" * 24 + f"\n\n{end_text}\n")

            add_new = button_data("ask", "new", key)
            replace_all = button_data("ask", "replace", key)
            cancel = button_data("ask", "cancel", key)

            markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text=lang("ask_new"),
                            callback_data=add_new
                        ),
                        InlineKeyboardButton(
                            text=lang("ask_replace"),
                            callback_data=replace_all
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text=lang("cancel"),
                            callback_data=cancel
                        )
                    ]
                ]
            )

            save("ask_words")
        else:
            glovar.ask_words.pop(key, None)
            add_word(word_type, word, aid)
            share_regex_update(client, word_type)
            text += f"{lang('status')}{lang('colon')}{code(lang('status_succeeded'))}\n"
    except Exception as e:
        logger.warning(f"Word add error: {e}", exc_info=True)

    return text, markup


def words_ask(client: Client, operation: str, key: str) -> (str, Set[int]):
    # Handle the reply to bot's asked question
    text = ""
    cc_list = set()
    try:
        # Check the data
        if not glovar.ask_words.get(key, {}):
            text += (f"{lang('status')}{lang('colon')}{lang('status_failed')}\n"
                     f"{lang('reason')}{lang('colon')}{lang('expired')}\n")
            return text, cc_list

        # Check lock
        if glovar.ask_words[key]["lock"]:
            return "", set()

        # Lock the session
        glovar.ask_words[key]["lock"] = True

        # Read data
        aid = glovar.ask_words[key]["admin"]
        word_type = glovar.ask_words[key]["type"]
        new_word = glovar.ask_words[key]["new"]
        old_words = glovar.ask_words[key]["old"]

        # Word type info text
        text += f"{lang('type')}{lang('colon')}{code(lang(word_type))}\n"

        if glovar.comments.get(word_type):
            text += f"{lang('comment')}{lang('colon')}{code(glovar.comments[word_type])}\n"

        text += f"{lang('word')}{lang('colon')}{code(new_word)}\n"

        # Waiting words info text
        end_text = "\n\n".join(code(w) for w in glovar.ask_words[key]["old"])

        # If admin decide to add new word
        if operation == "new":
            add_word(word_type, new_word, aid)
            share_regex_update(client, word_type)
            text = (f"{lang('action')}{lang('colon')}{code(lang('ask_new'))}\n"
                    f"{text}"
                    f"{lang('status')}{lang('colon')}{code(lang('status_succeeded'))}\n"
                    f"{lang('duplicated')}{lang('colon')}" + "-" * 24 + f"\n\n{end_text}\n")

        # Delete old words
        elif operation == "replace":
            add_word(word_type, new_word, aid)
            cc_list = remove_word(word_type, old_words, aid)
            share_regex_update(client, word_type)
            text = (f"{lang('action')}{lang('colon')}{code(lang('ask_replace'))}\n"
                    f"{text}"
                    f"{lang('status')}{lang('colon')}{code(lang('status_succeeded'))}\n"
                    f"{lang('replaced')}{lang('colon')}" + "-" * 24 + f"\n\n{end_text}\n")

        # Cancel
        elif operation == "cancel":
            text = (f"{lang('action')}{lang('colon')}{code(lang('action_cancel'))}\n"
                    f"{text}"
                    f"{lang('status')}{lang('colon')}{code(lang('status_succeeded'))}\n"
                    f"{lang('duplicated')}{lang('colon')}" + "-" * 24 + f"\n\n{end_text}\n")

        # Timeout
        elif operation == "timeout":
            text = (f"{text}"
                    f"{lang('status')}{lang('colon')}{code(lang('expired'))}\n"
                    f"{lang('duplicated')}{lang('colon')}" + "-" * 24 + f"\n\n{end_text}\n")

        save("ask_words")
    except Exception as e:
        logger.warning(f"Words ask error: {e}", exc_info=True)

    return text, cc_list


def words_list(message: Message) -> (str, InlineKeyboardMarkup):
    # List words
    text = ""
    markup = None
    try:
        # Basic data
        aid = message.from_user.id

        # Text prefix
        text = (f"{lang('admin')}{lang('colon')}{mention_id(aid)}\n"
                f"{lang('action')}{lang('colon')}{code(lang('action_list'))}\n")

        command_list = list(filter(None, get_text(message).split(" ")))

        # Check command format
        if len(command_list) <= 1:
            end_text = ""

            for word_type in glovar.regex:
                end_text += f"{code(word_type)}    {italic(lang(word_type))}"

                if glovar.comments.get(word_type):
                    end_text += f"{italic(lang('comma'))}{italic(glovar.comments[word_type])}"

                end_text += "\n"

            text += (f"{lang('status')}{lang('colon')}{code(lang('status_failed'))}\n"
                     f"{lang('reason')}{lang('colon')}{code(lang('command_usage'))}\n"
                     f"{lang('valid_types')}{lang('colon')}" + "-" * 24 + f"\n\n{end_text}\n")

            return text, markup

        word_type = command_list[1]
        desc = True

        # Get desc value
        if len(command_list) > 2:
            if command_list[2] == "asc":
                desc = False

        # Check the word type
        if word_type not in glovar.regex:
            order_text = (lambda x: lang("order_desc") if x else lang("order_asc"))(desc)

            text += f"{lang('type')}{lang('colon')}{code(lang(word_type))}\n"

            if glovar.comments.get(word_type):
                text += f"{lang('comment')}{lang('colon')}{code(glovar.comments[word_type])}\n"

            text += (f"{lang('order')}{lang('colon')}{code(order_text)}\n"
                     f"{lang('status')}{lang('colon')}{code(lang('status_failed'))}\n"
                     f"{lang('reason')}{lang('colon')}{code(lang('command_usage'))}\n")
            return text, markup

        text, markup = words_list_page(aid, word_type, 1, desc)
    except Exception as e:
        logger.warning(f"Word list error: {e}", exc_info=True)

    return text, markup


def words_list_page(aid: int, word_type: str, page: int, desc: bool) -> (str, InlineKeyboardMarkup):
    # Generate a words list page
    text = ""
    markup = None
    try:
        # Text prefix
        text = (f"{lang('admin')}{lang('colon')}{mention_id(aid)}\n"
                f"{lang('action')}{lang('colon')}{code(lang('action_list'))}\n")

        # Get words
        words = eval(f"glovar.{word_type}_words")
        keys = list(words.keys())
        keys.sort()
        w_list = sorted(keys, key=lambda k: words[k]["average"], reverse=desc)

        # Get the list and generate the markup
        w_list, markup = get_list_page(w_list, "list", word_type, page)

        # Generate the text
        end_text = f"\n\n".join((f"{code(w)}\n"
                                 f"{italic(round(words[w]['average'], 1))} {code('/')} "
                                 f"{italic(words[w]['today'])} {code('/')} "
                                 f"{italic(words[w]['total'])} {code('/')} "
                                 f"{italic(words[w]['temp'])}")
                                for w in w_list)
        order_text = (lambda x: lang("order_desc") if x else lang("order_asc"))(desc)

        text += f"{lang('type')}{lang('colon')}{code(lang(word_type))}\n"

        if glovar.comments.get(word_type):
            text += f"{lang('comment')}{lang('colon')}{code(glovar.comments[word_type])}\n"

        if not end_text.strip():
            end_text = code(lang("reason_none"))

        text += (f"{lang('order')}{lang('colon')}{code(order_text)}\n"
                 f"{lang('query')}{lang('colon')}{code(lang('all'))}\n"
                 f"{lang('result')}{lang('colon')}" + "-" * 24 + f"\n\n{end_text}\n")
    except Exception as e:
        logger.warning(f"Words list page error: {e}", exc_info=True)

    return text, markup


def word_remove(client: Client, message: Message) -> (str, Set[int]):
    # Remove a word
    text = ""
    cc_list = set()
    try:
        # Basic data
        uid = message.from_user.id

        # Get the report text
        text, cc_list = word_remove_try(client, message)

        if text:
            return text, cc_list

        if message.reply_to_message:
            aid = message.reply_to_message.from_user.id
            if uid != aid:
                text = (f"{lang('admin')}{lang('colon')}{mention_id(uid)}\n"
                        f"{lang('action')}{lang('colon')}{code(lang('action_remove'))}\n"
                        f"{lang('status')}{lang('colon')}{code(lang('status_failed'))}\n"
                        f"{lang('reason')}{lang('colon')}{code(lang('command_permission'))}\n")
                return text, cc_list

            r_text, cc_list = word_remove_try(client, message.reply_to_message)
            if r_text:
                return r_text, cc_list

        text = (f"{lang('admin')}{lang('colon')}{mention_id(uid)}\n"
                f"{lang('action')}{lang('colon')}{code(lang('action_remove'))}\n"
                f"{lang('status')}{lang('colon')}{code(lang('status_failed'))}\n"
                f"{lang('reason')}{lang('colon')}{code(lang('command_usage'))}\n")
    except Exception as e:
        logger.warning(f"Word remove error: {e}", exc_info=True)

    return text, cc_list


def word_remove_try(client: Client, message: Message) -> (str, Set[int]):
    # Try to remove a word
    text = ""
    cc_list = set()
    try:
        # Basic data
        aid = message.from_user.id

        # Check if the command format is correct
        word_type, word = get_command_context(message)

        if not word_type:
            return "", set()

        # Text prefix
        text = (f"{lang('admin')}{lang('colon')}{mention_id(aid)}\n"
                f"{lang('action')}{lang('colon')}{code(lang('action_remove'))}\n")

        # Word type info text
        text += f"{lang('type')}{lang('colon')}{code(lang(word_type))}\n"

        if glovar.comments.get(word_type):
            text += f"{lang('comment')}{lang('colon')}{code(glovar.comments[word_type])}\n"

        # Check the word type
        if not (word and word_type in glovar.regex):
            text += (f"{lang('status')}{lang('colon')}{code(lang('status_failed'))}\n"
                     f"{lang('reason')}{lang('colon')}{code(lang('command_usage'))}\n")

            return text, cc_list

        # Word info text
        text += f"{lang('word')}{lang('colon')}{code(word)}\n"

        # Format the word
        word = format_word(word)

        # Check if the word exists
        if not eval(f"glovar.{word_type}_words").get(word, {}):
            text += (f"{lang('status')}{lang('colon')}{code(lang('status_failed'))}\n"
                     f"{lang('reason')}{lang('colon')}{code(lang('reason_not_exist'))}\n")

            return text, cc_list

        cc_list = remove_word(word_type, [word], aid)
        text += f"{lang('status')}{lang('colon')}{code(lang('status_succeeded'))}\n"

        for cc_id in cc_list:
            text += f"{lang('action_cc')}{lang('colon')}{mention_id(cc_id)}\n"

        share_regex_update(client, word_type)
    except Exception as e:
        logger.warning(f"Word remove try error: {e}", exc_info=True)

    return text, cc_list


def words_search(message: Message, mode: str) -> (str, InlineKeyboardMarkup):
    # Search words
    text = ""
    markup = None
    try:
        # Basic data
        aid = message.from_user.id

        # Text prefix
        text = (f"{lang('admin')}{lang('colon')}{mention_id(aid)}\n"
                f"{lang('action')}{lang('colon')}{code(lang('action_search'))}\n"
                f"{lang('mode')}{lang('colon')}{code(lang(mode))}\n")

        # Check if the command format is correct
        word_type, word = get_command_context(message)

        if not word_type:
            text += (f"{lang('status')}{lang('colon')}{code(lang('status_failed'))}\n"
                     f"{lang('reason')}{lang('colon')}{code(lang('command_usage'))}\n")
            return text, markup

        if not (word and (word_type in list(glovar.regex) + ["all"])
                or (not word and word_type not in list(glovar.regex) + ["all"])):
            text += (f"{lang('type')}{lang('colon')}{code(lang(word_type))}\n"
                     f"{lang('status')}{lang('colon')}{code(lang('status_failed'))}\n"
                     f"{lang('reason')}{lang('colon')}{code(lang('command_usage'))}\n")
            return text, markup

        if not word:
            word = word_type
            word_type = "all"

        # Get the search key
        key = random_str(8)
        
        while key in glovar.result_search:
            key = random_str(8)

        glovar.result_search[key] = {
            "result": {},
            "type": word_type,
            "word": word,
            "mode": mode
        }

        # Get the result
        result = {}

        if word_type == "all":
            for n in glovar.regex:
                for w in eval(f"glovar.{n}_words"):
                    if not is_similar(mode, w, word):
                        continue

                    if result.get(w) is None:
                        result[w] = []

                    result[w].append(n)
        else:
            result = {w: [] for w in eval(f"glovar.{word_type}_words")
                      if is_similar(mode, w, word)}

        glovar.result_search[key]["result"] = result
        text, markup = words_search_page(aid, key, 1)
    except Exception as e:
        logger.warning(f"Words search error: {e}", exc_info=True)

    return text, markup


def words_search_page(aid: int, key: str, page: int) -> (str, InlineKeyboardMarkup):
    # Generate searched words page
    text = ""
    markup = None
    try:
        # Text prefix
        text = (f"{lang('admin')}{lang('colon')}{mention_id(aid)}\n"
                f"{lang('action')}{lang('colon')}{code(lang('action_search'))}\n")

        if key not in glovar.result_search:
            text += (f"{lang('status')}{lang('colon')}{code(lang('status_failed'))}\n"
                     f"{lang('reason')}{lang('colon')}{code(lang('expired'))}\n")
            return text, markup

        word_type = glovar.result_search[key]["type"]
        word = glovar.result_search[key]["word"]
        mode = glovar.result_search[key]["mode"]

        text += f"{lang('mode')}{lang('colon')}{code(lang(mode))}\n"
        text += f"{lang('type')}{lang('colon')}{code(glovar.lang.get(word_type, lang('all')))}\n"

        if glovar.comments.get(word_type):
            text += f"{lang('comment')}{lang('colon')}{code(glovar.comments[word_type])}\n"

        text += f"{lang('word')}{lang('colon')}{code(word)}\n"

        words = glovar.result_search[key]["result"]

        if not words:
            text += (f"{lang('status')}{lang('colon')}{code(lang('status_failed'))}\n"
                     f"{lang('reason')}{lang('colon')}{code(lang('reason_not_found'))}\n")
            return text, markup

        w_list = list(words)
        w_list.sort()
        w_list, markup = get_list_page(w_list, "search", key, page)

        # Get the result text
        if word_type == "all":
            result = glovar.result_search[key]['result']
            end_text = "\n\n".join(f"{code(w)}\n\n"
                                   + "\t" * 4
                                   + italic(lang('comma').join(lang(t) for t in result[w]))
                                   for w in w_list)
        else:
            words = eval(f"glovar.{word_type}_words")
            end_text = "\n\n".join((f"{code(w)}\n"
                                    f"{italic(round(words[w]['average'], 1))} {code('/')} "
                                    f"{italic(words[w]['today'])} {code('/')} "
                                    f"{italic(words[w]['total'])} {code('/')} "
                                    f"{italic(words[w]['temp'])}")
                                   for w in w_list)

        text += f"{lang('result')}{lang('colon')}" + "-" * 24 + f"\n\n{end_text}"
    except Exception as e:
        logger.warning(f"Words search page error: {e}", exc_info=True)

    return text, markup
