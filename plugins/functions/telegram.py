import logging
from time import sleep
from pyrogram import ParseMode, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.api.errors import FloodWait

# Enable logging
logger = logging.getLogger(__name__)


def send_message(client, cid, text, mid=None, markup=None):
    try:
        if text.strip() != "":
            try:
                client.send_message(
                    chat_id=cid,
                    text=text,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True,
                    reply_to_message_id=mid,
                    reply_markup=markup
                )
            except FloodWait as e:
                sleep(e.x + 1)
                client.send_message(
                    chat_id=cid,
                    text=text,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True,
                    reply_to_message_id=mid,
                    reply_markup=markup
                )
    except Exception as e:
        logger.warning(f"Send message to {cid} error: {e}")


# Test
def send_reply_keyboard(client, cid):
    client.send_message(
        chat_id=cid,
        text="This is a ReplyKeyboardMarkup example",
        reply_markup=ReplyKeyboardMarkup(
            [
                ["A", "B", "C", "D"],
                ["E", "F", "G"],
                ["H", "I"],
                ["J"]
            ],
            resize_keyboard=True
        )
    )


# Test
def send_inline_keyboard(client, cid):
    client.send_message(
        chat_id=cid,
        text="This is a InlineKeyboardMarkup example",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Button",
                        callback_data=b"data"
                    ),
                    InlineKeyboardButton(
                        "URL",
                        url="https://docs.pyrogram.ml"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Choose chat",
                        switch_inline_query="pyrogram"
                    ),
                    InlineKeyboardButton(
                        "Inline here",
                        switch_inline_query_current_chat="pyrogram"
                    )
                ]
            ]
        )
    )
