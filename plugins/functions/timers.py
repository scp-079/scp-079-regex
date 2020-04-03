# SCP-079-REGEX - Manage regex patterns
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
from time import sleep

from pyrogram import Client

from .. import glovar
from .channel import share_data
from .etc import code, get_now, lang, mention_id, thread
from .file import save
from .telegram import send_message
from .words import get_comments, words_ask

# Enable logging
logger = logging.getLogger(__name__)


def backup_files(client: Client) -> bool:
    # Backup data files to BACKUP
    try:
        for file in glovar.file_list:
            # Check
            if not eval(f"glovar.{file}"):
                continue

            # Share
            share_data(
                client=client,
                receivers=["BACKUP"],
                action="backup",
                action_type="data",
                data=file,
                file=f"data/{file}"
            )
            sleep(5)

        return True
    except Exception as e:
        logger.warning(f"Backup error: {e}", exc_info=True)

    return False


def interval_hour_01(client: Client) -> bool:
    # Execute every hour
    try:
        # Basic data
        now = get_now()

        # Clear old action sessions
        for key in list(glovar.ask_words):
            session = glovar.ask_words[key]
            time = session["time"]

            if now - time < 3600:
                continue

            lock = session["lock"]

            if not lock:
                words_ask(client, "timeout", key)

            glovar.ask_words.pop(key, {})

        save("ask_words")

        return True
    except Exception as e:
        logger.warning(f"Interval hour 01 error: {e}", exc_info=True)

    return False


def reset_count(client: Client) -> bool:
    # Reset the daily usage
    glovar.locks["regex"].acquire()
    try:
        for word_type in glovar.regex:
            deleted_words = {}

            for word in list(eval(f"glovar.{word_type}_words")):
                today = eval(f"glovar.{word_type}_words")[word]["today"]
                eval(f"glovar.{word_type}_words")[word]["today"] = 0

                if today == 0:
                    eval(f"glovar.{word_type}_words")[word]["temp"] += 1
                else:
                    eval(f"glovar.{word_type}_words")[word]["temp"] = 0

                comments = get_comments(word)

                if (not any("temp" in comment for comment in comments)
                        and not (word_type == "ban" and not any("forever" in comment for comment in comments))):
                    continue

                if eval(f"glovar.{word_type}_words")[word]["temp"] >= glovar.limit_temp:
                    deleted_words[word] = eval(f"glovar.{word_type}_words").pop(word, {})

            save(f"{word_type}_words")

            if not deleted_words:
                continue

            deleted_words_units = list(deleted_words)
            deleted_words_units_list = [deleted_words_units[i:i + glovar.per_page]
                                        for i in range(0, len(deleted_words_units), glovar.per_page)]

            for words in deleted_words_units_list:
                end_text = "\n\n".join(code(word) for word in words)
                cc_text = "\n".join(f"{lang('action_cc')}{lang('colon')}{mention_id(cc_id)}"
                                    for cc_id in {deleted_words[word]["who"]
                                                  for word in words if deleted_words[word].get("who", 0)})

                text = (f"{lang('action')}{lang('colon')}{code(lang('action_remove_auto'))}\n"
                        f"{lang('type')}{lang('colon')}{code(lang(word_type))}\n"
                        f"{cc_text}\n")

                if glovar.comments.get(word_type):
                    text += f"{lang('comment')}{lang('colon')}{code(glovar.comments[word_type])}\n"

                text += f"{lang('removed')}{lang('colon')}" + "-" * 24 + f"\n\n{end_text}\n"

                thread(send_message, (client, glovar.regex_group_id, text))

        return True
    except Exception as e:
        logger.warning(f"Reset count error: {e}", exc_info=True)
    finally:
        glovar.locks["regex"].release()

    return False


def update_status(client: Client, the_type: str) -> bool:
    # Update running status to BACKUP
    try:
        share_data(
            client=client,
            receivers=["BACKUP"],
            action="backup",
            action_type="status",
            data={
                "type": the_type,
                "backup": glovar.backup
            }
        )

        return True
    except Exception as e:
        logger.warning(f"Update status error: {e}", exc_info=True)

    return False
