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
from typing import List, Union

from pyrogram import Client

from .. import glovar
from .etc import crypt_str, delay, format_data, thread
from .file import crypt_file
from .telegram import send_document, send_message


# Enable logging
logger = logging.getLogger(__name__)


def exchange_to_hide(client: Client) -> bool:
    # Let other bots exchange data in the hide channel instead
    try:
        glovar.should_hide = True
        text = format_data(
            sender="EMERGENCY",
            receivers=["EMERGENCY"],
            action="backup",
            action_type="hide",
            data=True
        )
        thread(send_message, (client, glovar.hide_channel_id, text))
        return True
    except Exception as e:
        logger.warning(f"Exchange to hide error: {e}", exc_info=True)

    return False


def share_data(client: Client, receivers: List[str], action: str, action_type: str, data: Union[dict, int, str],
               file: str = None) -> bool:
    # Use this function to share data in the exchange channel
    try:
        if glovar.sender in receivers:
            receivers.remove(glovar.sender)

        if glovar.should_hide:
            channel_id = glovar.hide_channel_id
        else:
            channel_id = glovar.exchange_channel_id

        if file:
            text = format_data(
                sender=glovar.sender,
                receivers=receivers,
                action=action,
                action_type=action_type,
                data=data
            )
            crypt_file("encrypt", f"data/{file}", f"tmp/{file}")
            result = send_document(client, channel_id, f"tmp/{file}", text)
        else:
            text = format_data(
                sender=glovar.sender,
                receivers=receivers,
                action=action,
                action_type=action_type,
                data=data
            )
            result = send_message(client, channel_id, text)

        if result is False:
            exchange_to_hide(client)
            thread(share_data, (client, receivers, action, action_type, data, file))

        return True
    except Exception as e:
        logger.warning(f"Share data error: {e}", exc_info=True)

    return False


def share_regex_update(client: Client) -> bool:
    # Use this function to share regex update to other bots
    try:
        if glovar.update_type == "reload":
            delay(
                5,
                share_data,
                [
                    client,
                    glovar.receivers_regex,
                    "update",
                    "reload",
                    crypt_str("encrypt", glovar.reload_path, glovar.key)
                ]
            )
        else:
            sleep(5)
            crypt_file("encrypt", "data/compiled", "tmp/compiled")
            thread(
                share_data,
                (
                    client,
                    glovar.receivers_regex,
                    "update",
                    "download",
                    crypt_str("encrypt", glovar.reload_path, glovar.key),
                    "tmp/compiled"
                )
            )

        return True
    except Exception as e:
        logger.warning(f"Data exchange error: {e}", exc_info=True)

    return False
