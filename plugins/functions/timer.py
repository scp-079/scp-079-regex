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

from .. import glovar
from .etc import send_data, thread
from .files import crypt_file
from .telegram import send_document

# Enable logging
logger = logging.getLogger(__name__)


def backup(client):
    try:
        exchange_text = send_data(
            sender="REGEX",
            receivers=["ALL"],
            action="backup",
            action_type="pickle",
            data="compiled"
        )
        crypt_file("encrypt", "data/compiled", "tmp/compiled")
        thread(send_document, (client, glovar.exchange_id, "tmp/compiled", exchange_text))
    except Exception as e:
        logger.warning(f"Backup error: {e}", exc_info=True)
