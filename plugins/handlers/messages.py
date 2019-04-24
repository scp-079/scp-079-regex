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

from pyrogram import Client, Filters

from ..functions.filters import test_group
from ..functions.test import name_test, sticker_test, text_test

from .. import glovar

# Enable logging
logger = logging.getLogger(__name__)


@Client.on_message(Filters.incoming & Filters.group & test_group & ~Filters.service
                   & ~Filters.command(glovar.all_commands, glovar.prefix))
def test(client, message):
    try:
        name_test(client, message)
        sticker_test(client, message)
        text_test(client, message)
    except Exception as e:
        logger.warning(f"Test error: {e}", exc_info=True)
