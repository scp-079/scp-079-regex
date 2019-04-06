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
        logger.warning(f"Send message to {cid} error: {e}", exc_info=True)


def edit_message(client, cid, mid, text, markup=None):
    try:
        if text.strip() != "":
            try:
                client.edit_message_text(
                    chat_id=cid,
                    message_id=mid,
                    text=text,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True,
                    reply_markup=markup
                )
            except FloodWait as e:
                sleep(e.x + 1)
                client.edit_message_text(
                    chat_id=cid,
                    message_id=mid,
                    text=text,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True,
                    reply_markup=markup
                )
    except Exception as e:
        logger.warning(f"Edit message to {cid} error: {e}", exc_info=True)


def answer_callback(client, query_id, text):
    try:
        try:
            client.answer_callback_query(
                callback_query_id=query_id,
                text=text,
                show_alert=True
            )
        except FloodWait as e:
            sleep(e.x + 1)
            client.answer_callback_query(
                callback_query_id=query_id,
                text=text,
                show_alert=True
            )
    except Exception as e:
        logger.warning(f"Answer query to {query_id} error: {e}", exc_info=True)


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
