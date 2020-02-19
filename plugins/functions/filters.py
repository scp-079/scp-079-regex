# SCP-079-REGEX - Manage the regex patterns
# Copyright (C) 2019-2020 SCP-079 <https://scp-079.org>
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
from typing import Match, Optional, Union

from pyrogram import CallbackQuery, Filters, Message
from xeger import Xeger

from .. import glovar

# Enable logging
logger = logging.getLogger(__name__)

# Xeger config
xg = Xeger(limit=32)


def is_exchange_channel(_, message: Message) -> bool:
    # Check if the message is sent from the exchange channel
    try:
        if not message.chat:
            return False

        cid = message.chat.id

        if glovar.should_hide:
            return cid == glovar.hide_channel_id
        else:
            return cid == glovar.exchange_channel_id
    except Exception as e:
        logger.warning(f"Is exchange channel error: {e}", exc_info=True)

    return False


def is_from_user(_, message: Message) -> bool:
    # Check if the message is sent from a user
    try:
        if message.from_user and message.from_user.id != 777000:
            return True
    except Exception as e:
        logger.warning(f"Is from user error: {e}", exc_info=True)

    return False


def is_hide_channel(_, message: Message) -> bool:
    # Check if the message is sent from the hide channel
    try:
        if not message.chat:
            return False

        cid = message.chat.id

        if cid == glovar.hide_channel_id:
            return True
    except Exception as e:
        logger.warning(f"Is hide channel error: {e}", exc_info=True)

    return False


def is_test_group(_, update: Union[CallbackQuery, Message]) -> bool:
    # Check if the message is sent from the test group
    try:
        if isinstance(update, CallbackQuery):
            message = update.message
        else:
            message = update

        if not message.chat:
            return False

        cid = message.chat.id

        if cid == glovar.test_group_id:
            return True
    except Exception as e:
        logger.warning(f"Is test group error: {e}", exc_info=True)

    return False


def is_regex_group(_, update: Union[CallbackQuery, Message]) -> bool:
    # Check if the message is sent from regex group
    try:
        if isinstance(update, CallbackQuery):
            message = update.message
        else:
            message = update

        if not message.chat:
            return False

        cid = message.chat.id

        if cid == glovar.regex_group_id:
            return True
    except Exception as e:
        logger.warning(f"Is regex group error: {e}", exc_info=True)

    return False


exchange_channel = Filters.create(
    func=is_exchange_channel,
    name="Exchange Channel"
)

from_user = Filters.create(
    func=is_from_user,
    name="From User"
)

hide_channel = Filters.create(
    func=is_hide_channel,
    name="Hide Channel"
)

test_group = Filters.create(
    func=is_test_group,
    name="Test Group"
)

regex_group = Filters.create(
    func=is_regex_group,
    name="Regex Group"
)


def is_regex_text(word_type: str, text: str, ocr: bool = False, again: bool = False) -> Optional[Match]:
    # Check if the text hit the regex rules
    result = None
    try:
        if text:
            if not again:
                text = re.sub(r"\s{2,}", " ", text)
            elif " " in text:
                text = re.sub(r"\s", "", text)
            else:
                return None
        else:
            return None

        words = list(eval(f"glovar.{word_type}_words"))

        for word in words:
            if ocr and "(?# nocr)" in word:
                continue

            result = re.search(word, text, re.I | re.S | re.M)

            # Return
            if result:
                return result

        # Try again
        return is_regex_text(word_type, text, ocr, True)
    except Exception as e:
        logger.warning(f"Is regex text error: {e}", exc_info=True)

    return result


def is_similar(mode: str, a: str, b: str) -> bool:
    # Get regex match result
    try:
        if mode == "find":
            if b not in a:
                return False

        elif mode == "loose" or mode == "s":
            if not (re.search(a, b, re.I | re.M | re.S)
                    or re.search(b, a, re.I | re.M | re.S)
                    or re.search(a, xg.xeger(b), re.I | re.M | re.S)
                    or re.search(b, xg.xeger(a), re.I | re.M | re.S)):
                return False

        elif mode == "search":
            if not (re.search(b, a, re.I | re.M | re.S)
                    or re.search(b, xg.xeger(a), re.I | re.M | re.S)):
                return False

        elif mode == "strict":
            i = 0

            while i < 3:
                if not (re.search(a, xg.xeger(b), re.I | re.M | re.S)
                        or re.search(b, xg.xeger(a), re.I | re.M | re.S)):
                    return False

                i += 1

        elif mode == "test":
            b = re.sub(r"\s{2,}", " ", b)

            if not re.search(a, b, re.I | re.M | re.S):
                b = re.sub(r"\s", "", b)

                if not re.search(a, b, re.I | re.M | re.S):
                    return False

        return True
    except Exception as e:
        logger.warning(f"Is similar error: {e}", exc_info=True)

    return False
