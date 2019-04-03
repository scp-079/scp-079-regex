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


def send_reply_keyboard(client, cid):
    client.send_message(
        chat_id=cid,
        text="This is a ReplyKeyboardMarkup example",
        reply_markup=ReplyKeyboardMarkup(
            [
                ["A", "B", "C", "D"],  # First row
                ["E", "F", "G"],  # Second row
                ["H", "I"],  # Third row
                ["J"]  # Fourth row
            ],
            resize_keyboard=True  # Make the keyboard smaller
        )
    )


def send_inline_keyboard(client, cid):
    client.send_message(
        chat_id=cid,
        text="This is a InlineKeyboardMarkup example",
        reply_markup=InlineKeyboardMarkup(
            [
                [  # First row
                    InlineKeyboardButton(  # Generates a callback query when pressed
                        "Button",
                        callback_data=b"data"
                    ),  # Note how callback_data must be bytes
                    InlineKeyboardButton(  # Opens a web URL
                        "URL",
                        url="https://docs.pyrogram.ml"
                    ),
                ],
                [  # Second row
                    # Opens the inline interface
                    InlineKeyboardButton(
                        "Choose chat",
                        switch_inline_query="pyrogram"
                    ),
                    InlineKeyboardButton(  # Opens the inline interface in the current chat
                        "Inline here",
                        switch_inline_query_current_chat="pyrogram"
                    )
                ]
            ]
        )
    )
