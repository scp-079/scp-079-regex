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

from pyrogram import Client, Filters, Message

from .. import glovar
from ..functions.etc import code, general_link, lang, thread
from ..functions.filters import exchange_channel, from_user, hide_channel, test_group
from ..functions.receive import receive_captcha_data, receive_count, receive_status_ask, receive_text_data
from ..functions.telegram import send_message
from ..functions.tests import name_test, sticker_test, text_test

# Enable logging
logger = logging.getLogger(__name__)


@Client.on_message(Filters.incoming & Filters.channel & ~Filters.command(glovar.all_commands, glovar.prefix)
                   & hide_channel, group=-1)
def exchange_emergency(client: Client, message: Message) -> bool:
    # Sent emergency channel transfer request
    try:
        # Read basic information
        data = receive_text_data(message)

        if not data:
            return True

        sender = data["from"]
        receivers = data["to"]
        action = data["action"]
        action_type = data["type"]
        data = data["data"]

        if "EMERGENCY" not in receivers:
            return True

        if action != "backup":
            return True

        if action_type != "hide":
            return True

        if data is True:
            glovar.should_hide = data
        elif data is False and sender == "MANAGE":
            glovar.should_hide = data

        project_text = general_link(glovar.project_name, glovar.project_link)
        hide_text = (lambda x: lang("enabled") if x else "disabled")(glovar.should_hide)
        text = (f"{lang('project')}{lang('colon')}{project_text}\n"
                f"{lang('action')}{lang('colon')}{code(lang('transfer_channel'))}\n"
                f"{lang('emergency_channel')}{lang('colon')}{code(hide_text)}\n")
        thread(send_message, (client, glovar.debug_channel_id, text))

        return True
    except Exception as e:
        logger.warning(f"Exchange emergency error: {e}", exc_info=True)

    return False


@Client.on_message((Filters.incoming or glovar.aio) & Filters.channel
                   & ~Filters.command(glovar.all_commands, glovar.prefix)
                   & exchange_channel)
def process_data(client: Client, message: Message) -> bool:
    # Process the data in exchange channel
    glovar.locks["receive"].acquire()
    try:
        data = receive_text_data(message)

        if not data:
            return True

        sender = data["from"]
        receivers = data["to"]
        action = data["action"]
        action_type = data["type"]
        data = data["data"]

        # This will look awkward,
        # seems like it can be simplified,
        # but this is to ensure that the permissions are clear,
        # so it is intentionally written like this
        if glovar.sender in receivers:

            if sender == "CAPTCHA":

                if action == "captcha":
                    if action_type == "result":
                        receive_captcha_data(client, message, data)

                if action == "regex":
                    if action_type == "count":
                        receive_count(client, message, data)

            elif sender == "CLEAN":

                if action == "regex":
                    if action_type == "count":
                        receive_count(client, message, data)

            elif sender == "LANG":

                if action == "regex":
                    if action_type == "count":
                        receive_count(client, message, data)

            elif sender == "LONG":

                if action == "regex":
                    if action_type == "count":
                        receive_count(client, message, data)

            elif sender == "NOFLOOD":

                if action == "regex":
                    if action_type == "count":
                        receive_count(client, message, data)

            elif sender == "NOPORN":

                if action == "regex":
                    if action_type == "count":
                        receive_count(client, message, data)

            elif sender == "NOSPAM":

                if action == "regex":
                    if action_type == "count":
                        receive_count(client, message, data)

            elif sender == "RECHECK":

                if action == "regex":
                    if action_type == "count":
                        receive_count(client, message, data)

            elif sender == "WATCH":

                if action == "regex":
                    if action_type == "count":
                        receive_count(client, message, data)

            elif sender == "MANAGE":

                if action == "status":
                    if action_type == "ask":
                        receive_status_ask(client, data)

        return True
    except Exception as e:
        logger.warning(f"Process data error: {e}", exc_info=True)
    finally:
        glovar.locks["receive"].release()

    return False


@Client.on_message(Filters.incoming & Filters.group & ~Filters.service
                   & ~Filters.command(glovar.all_commands, glovar.prefix)
                   & test_group
                   & from_user)
def test(client: Client, message: Message) -> bool:
    # Show test results in TEST group
    glovar.locks["test"].acquire()
    try:
        name_test(client, message)
        sticker_test(client, message)
        text_test(client, message)

        return True
    except Exception as e:
        logger.warning(f"Test error: {e}", exc_info=True)
    finally:
        glovar.locks["test"].release()

    return False
