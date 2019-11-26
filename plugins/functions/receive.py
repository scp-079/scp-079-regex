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
import pickle
from json import loads
from typing import Any

from pyrogram import Client, Message

from .. import glovar
from .channel import share_data
from .etc import get_now, get_text, lang, thread
from .file import crypt_file, data_to_file, delete_file, get_downloaded_path, get_new_path, save

# Enable logging
logger = logging.getLogger(__name__)


def receive_count(client: Client, message: Message, data: str) -> bool:
    # Receive count
    glovar.locks["regex"].acquire()
    try:
        word_type = data.replace("_words", "")
        data = receive_file_data(client, message)

        if not data:
            return True

        data_set = set(data)
        word_set = set(eval(f"glovar.{word_type}_words"))
        the_set = data_set & word_set

        for word in the_set:
            eval(f"glovar.{word_type}_words")[word]["today"] += data[word]
            eval(f"glovar.{word_type}_words")[word]["total"] += data[word]
            total = eval(f"glovar.{word_type}_words")[word]["total"]
            time = get_now() - eval(f"glovar.{word_type}_words")[word]["time"]
            eval(f"glovar.{word_type}_words")[word]["average"] = total / (time / 86400)

        save(f"{word_type}_words")

        return True
    except Exception as e:
        logger.warning(f"Receive count error: {e}", exc_info=True)
    finally:
        glovar.locks["regex"].release()

    return False


def receive_file_data(client: Client, message: Message, decrypt: bool = True) -> Any:
    # Receive file's data from exchange channel
    data = None
    try:
        if not message.document:
            return None

        file_id = message.document.file_id
        file_ref = message.document.file_ref
        path = get_downloaded_path(client, file_id, file_ref)

        if not path:
            return None

        if decrypt:
            # Decrypt the file, save to the tmp directory
            path_decrypted = get_new_path()
            crypt_file("decrypt", path, path_decrypted)
            path_final = path_decrypted
        else:
            # Read the file directly
            path_decrypted = ""
            path_final = path

        with open(path_final, "rb") as f:
            data = pickle.load(f)

        for f in {path, path_decrypted}:
            thread(delete_file, (f,))
    except Exception as e:
        logger.warning(f"Receive file error: {e}", exc_info=True)

    return data


def receive_status_ask(client: Client, data: dict) -> bool:
    # Receive version info request
    glovar.locks["regex"].acquire()
    try:
        # Basic data
        aid = data["admin_id"]
        mid = data["message_id"]

        status = {}

        for word_type in glovar.regex:
            if not glovar.regex[word_type]:
                continue

            status[lang("word_type")] = f"{len(eval(f'glovar.{word_type}_words'))} {lang('rules')}"

        file = data_to_file(status)
        share_data(
            client=client,
            receivers=["MANAGE"],
            action="status",
            action_type="reply",
            data={
                "admin_id": aid,
                "message_id": mid
            },
            file=file
        )

        return True
    except Exception as e:
        logger.warning(f"Receive version ask error: {e}", exc_info=True)
    finally:
        glovar.locks["regex"].release()

    return False


def receive_text_data(message: Message) -> dict:
    # Receive text's data from exchange channel
    data = {}
    try:
        text = get_text(message)

        if not text:
            return {}

        data = loads(text)
    except Exception as e:
        logger.warning(f"Receive text data error: {e}")

    return data
