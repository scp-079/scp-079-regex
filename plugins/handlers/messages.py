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

from .. import glovar
from ..functions.etc import code, get_text, thread
from ..functions.telegram import send_message
from ..functions.words import similar

# Enable logging
logger = logging.getLogger(__name__)


@Client.on_message(Filters.incoming & Filters.channel)
def test(client, message):
    try:
        if message.chat.id == glovar.channel_id:
            text = get_text(message)
            if text:
                result = ""
                mid = message.message_id
                for word_type in glovar.names:
                    if word_type != "sti":
                        if glovar.compiled[word_type].search(text):
                            w_list = [w for w in eval(f"glovar.{word_type}_words") if similar("test", w, text)]
                            result += f"{glovar.names[word_type]}：------------------------\n\n"
                            for w in w_list:
                                result += f"{code(w)}\n\n"

                if message.sticker and message.sticker.set_name:
                    result += f"贴纸名称：{code(message.sticker.set_name)}\n"
                    if glovar.compiled["sti"].search(text):
                        w_list = [w for w in glovar.sti_words if similar("test", w, text)]
                        result += f"{glovar.names['sti']}：------------------------\n\n"
                        for w in w_list:
                            result += f"{code(w)}\n\n"

                if result == "":
                    result = "并无匹配的各项检测结果"

                thread(send_message, (client, message.chat.id, result, mid))
    except Exception as e:
        logger.warning(f"Test error: {e}", exc_info=True)
