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

from pyrogram import Client

from .. import glovar
from .channel import share_data
from .etc import get_now
from .file import save
from .words import words_ask

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


def reset_count() -> bool:
    # Reset the daily usage
    glovar.locks["regex"].acquire()
    try:
        for word_type in glovar.regex:
            for word in list(eval(f"glovar.{word_type}_words")):
                today = eval(f"glovar.{word_type}_words")[word]["today"]
                eval(f"glovar.{word_type}_words")[word]["today"] = 0

                if "(?# temp)" not in word:
                    continue

                if today == 0:
                    eval(f"glovar.{word_type}_words")[word]["temp"] += 1
                else:
                    eval(f"glovar.{word_type}_words")[word]["temp"] = 0

                if eval(f"glovar.{word_type}_words")[word]["temp"] >= glovar.limit_temp:
                    eval(f"glovar.{word_type}_words").pop(word)

            save(f"{word_type}_words")

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
