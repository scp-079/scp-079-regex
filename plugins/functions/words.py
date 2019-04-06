import logging
from copy import deepcopy
from pyrogram import InlineKeyboardMarkup, InlineKeyboardButton
from .. import glovar
from ..functions.etc import code, bytes_data

# Enable logging
logger = logging.getLogger(__name__)


def words_list(word_type, page):
    text = ""
    markup = None
    words = eval(f"glovar.{word_type}_words")
    if words:
        word = list(deepcopy(words))
        quo = int(len(words) / 50)
        if quo != 0:
            page_count = quo + 1
            if len(words) % 50 == 0:
                page_count = page_count - 1

            if page != page_count:
                word = word[(page - 1) * 50:page * 50]
            else:
                word = word[(page - 1) * 50:len(word)]
            if page_count > 1:
                if page == 1:
                    markup = InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    f"第 {page} 页",
                                    callback_data=bytes_data("none")
                                ),
                                InlineKeyboardButton(
                                    ">>",
                                    callback_data=bytes_data("list", word_type, page + 1)
                                )
                            ]
                        ]
                    )
                elif page == page_count:
                    markup = InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "<<",
                                    callback_data=bytes_data("list", word_type, page - 1)
                                ),
                                InlineKeyboardButton(
                                    f"第 {page} 页",
                                    callback_data=bytes_data("none")
                                )
                            ]
                        ]
                    )
                else:
                    markup = InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "<<",
                                    callback_data=bytes_data("list", word_type, page - 1)
                                ),
                                InlineKeyboardButton(
                                    f"第 {page} 页",
                                    callback_data=bytes_data("none")
                                ),
                                InlineKeyboardButton(
                                    '>>',
                                    callback_data=bytes_data("list", word_type, page + 1)
                                )
                            ]
                        ]
                    )

        for w in word:
            text += f"{code(w)}，"

        text = text[:-1]
        text = glovar.names[word_type] + "词组如下：\n\n" + text
    else:
        text = f"无{glovar.names[word_type]}词组"

    return text, markup
